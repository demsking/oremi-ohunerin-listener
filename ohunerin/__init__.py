# Copyright 2025-2026 Sébastien Demanou. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import argparse
import asyncio
import json
import signal
import ssl
import urllib.parse

from websockets.asyncio.client import connect

from .args import parse_arguments
from .audio import Audio
from .detector import SoundDetector
from .listener import AudioListener
from .logger import LOG_LEVEL_STR
from .logger import logger
from .mqtt import MQTTClient
from .package import APP_DESCRIPTION
from .package import APP_NAME
from .package import APP_VERSION

USER_AGENT = f"{APP_NAME}/{APP_VERSION}"


def build_connection_uri(args: argparse.Namespace) -> str:
  params = {}

  if args.features_file:
    with open(args.features_file, "r", encoding="utf-8") as file:
      features_data = json.load(file)

    if not isinstance(features_data, list):
      raise ValueError("Invalid features file format: expected an array")

    feature_names = []

    for feature in features_data:
      name = feature.get("name")

      if not name:
        continue

      feature_names.append(name)

      if name == "wakeword-detection":
        params["language"] = feature.get("language", args.language)

        if "wakewords" in feature:
          params["wakewords"] = json.dumps(feature["wakewords"])

        if "discriminants" in feature:
          params["discriminants"] = json.dumps(feature["discriminants"])
      elif name == "sound-detection":
        if "allowlist" in feature:
          params["allowlist"] = ",".join(feature["allowlist"])

    params["features"] = ",".join(feature_names)
  else:
    params["features"] = "wakeword-detection,sound-detection"
    params["language"] = args.language

  query_string = urllib.parse.urlencode(params)

  return (
    f"wss://{args.host}:{args.port}/ws?{query_string}" if args.cert_file else f"ws://{args.host}:{args.port}/ws?{query_string}"
  )


async def main() -> None:
  list_devices_parser = argparse.ArgumentParser(
    prog=APP_NAME,
    description=APP_DESCRIPTION,
    add_help=False,
  )

  list_devices_parser.add_argument(
    "--list-devices",
    action="store_true",
    help="List available input devices.",
  )
  list_devices_args, _ = list_devices_parser.parse_known_args()

  if list_devices_args.list_devices:
    Audio.list_input_devices()
    return

  args = parse_arguments()
  audio_stream = Audio(device_index=args.device_index)

  # Log initial configuration
  logger.info(f"Starting {APP_NAME}/{APP_VERSION}")
  logger.info(f"Log level: {LOG_LEVEL_STR}")
  logger.info(f"Configuration Threshold: {args.threshold}")
  logger.info(f"Configuration Delay: {args.delay}s")
  logger.info(f"Configuration MQTT Topic: #{args.mqtt_topic}s")

  mqtt_client = MQTTClient(
    broker=args.mqtt_broker,
    port=args.mqtt_port,
    topic=args.mqtt_topic,
    username=args.mqtt_username,
    password=args.mqtt_password,
  )

  @mqtt_client.client.connect_callback()
  def mqtt_on_connect(client, userdata, flags, reason_code, properties) -> None:
    logger.info(f"Connected to {client} with result code {reason_code}")

  @mqtt_client.client.disconnect_callback()
  def mqtt_on_disconnect(client, userdata, flags, reason_code, properties) -> None:
    if audio_stream.is_active():
      logger.warning(f"Unexpected disconnection from {client} with result code {reason_code}. Reconnecting...")
      mqtt_client.connect()
    else:
      logger.info(f"Disconnected from {client} with result code {reason_code}")

  mqtt_client.connect()
  mqtt_client.set_availability(False)

  if args.cert_file:
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(args.cert_file)
  else:
    ssl_context = None

  uri = build_connection_uri(args)

  async with connect(uri, ssl=ssl_context, user_agent_header=USER_AGENT) as websocket:
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: loop.create_task(websocket.close(), name="SIGINT Signal Task"))
    loop.add_signal_handler(signal.SIGTERM, lambda: loop.create_task(websocket.close(), name="SIGTERM Signal Task"))

    logger.info(f"Connected to Oremi Ohunerin server at {args.host}:{args.port}")

    sound_detector = SoundDetector(mqtt_client, websocket, audio_stream, delay=args.delay, threshold=args.threshold)
    audio_listener = AudioListener(audio_stream, websocket, mqtt_client)

    detecting_task = loop.create_task(sound_detector.detecting(), name="Detection Task")
    listening_task = loop.create_task(audio_listener.listening(), name="Listening Task")

    def handle_task_done(task: asyncio.Task) -> None:
      try:
        if task.exception() is not None:
          logger.error(task)
        elif task.cancelled():
          logger.info(f"{task.get_name()} cancelled")
        else:
          logger.info(f"{task.get_name()} done")
      except (asyncio.CancelledError, asyncio.InvalidStateError) as error:
        logger.error(error)

    detecting_task.add_done_callback(handle_task_done)
    listening_task.add_done_callback(handle_task_done)

    await asyncio.wait([detecting_task, listening_task])
