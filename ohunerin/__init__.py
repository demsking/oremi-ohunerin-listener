# Copyright 2025 Sébastien Demanou. All Rights Reserved.
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
from datetime import datetime
from typing import Literal

import paho.mqtt.client as mqtt
import sounddevice as sd
import websockets.exceptions
import websockets.legacy.client

from .args import parse_arguments
from .audio import Audio
from .logger import LOG_LEVEL_STR
from .logger import logger
from .models import DetectedSound
from .models import DetectedSoundType
from .package import APP_DESCRIPTION
from .package import APP_NAME
from .package import APP_VERSION
from .string import get_slug


async def main() -> None:
  # Parse arguments for --list-devices option
  list_devices_parser = argparse.ArgumentParser(
    prog=APP_NAME,
    description=APP_DESCRIPTION,
    add_help=False,
  )

  list_devices_parser.add_argument(
    '--list-devices',
    action='store_true',
    help='List available input devices.',
  )

  list_devices_args, _ = list_devices_parser.parse_known_args()

  # Check if --list-devices is provided without other required args
  if list_devices_args.list_devices:
    Audio.list_input_devices()
    return

  args = parse_arguments()
  audio_stream = Audio(device_index=args.device_index)

  # Dictionary to track the last published sounds and their clearing tasks
  published_sound_sentinel: dict[str, asyncio.Task] = {}

  # Starting
  logger.info(f'Starting {APP_NAME}/{APP_VERSION}')
  logger.info(f'Log level: {LOG_LEVEL_STR}')
  logger.info(f'Threshold: {args.threshold}')
  logger.info(f'Delay: {args.delay}s')

  if args.cert_file:
    uri: str = f'wss://{args.host}:{args.port}'

    logger.info(f'Using certificat file "{args.cert_file}"')
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(args.cert_file)
  else:
    uri = f'ws://{args.host}:{args.port}'
    ssl_context = None

  mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

  mqtt_client.on_connect = lambda client, userdata, flags, reason_code, properties: (
    logger.info(f'Connected to mqtt://{args.mqtt_broker}:{args.mqtt_port}')
  )

  mqtt_client.on_disconnect = lambda client, userdata, flags, reason_code, properties: (
    logger.info(f'Disconnected from mqtt://{args.mqtt_broker}:{args.mqtt_port}')
  )

  def mqtt_publish(topic: DetectedSoundType | str, message: str, retain: bool = False) -> None:
    _topic = f'{args.mqtt_topic}/{topic}'

    logger.debug(f'Publishing #{_topic}: {message} with retain {retain}')
    mqtt_client.publish(f'{_topic}', message, retain=retain)

  def set_availability(available: bool) -> None:
    message: Literal['online', 'offline'] = 'online' if available else 'offline'

    mqtt_publish('available', message, retain=True)

  def send_clearing_message(type: DetectedSoundType) -> None:
    data: DetectedSound = {
      'type': type,
      'sound': '...',
      'score': 1.0,
      'date': datetime.now().isoformat(),
    }

    message = json.dumps(data)

    mqtt_publish(type, message, True)

  if args.mqtt_username:
    mqtt_client.username_pw_set(username=args.mqtt_username, password=args.mqtt_password)

  mqtt_client.connect(args.mqtt_broker, args.mqtt_port, keepalive=0)
  send_clearing_message('wakeword')
  send_clearing_message('sound')
  set_availability(False)

  async with websockets.legacy.client.connect(uri, ssl=ssl_context, user_agent_header='sds-client/1.0.0') as websocket:
    loop = asyncio.get_running_loop()

    loop.add_signal_handler(signal.SIGINT, lambda: loop.create_task(websocket.close(), name='SIGINT Signal Task'))
    loop.add_signal_handler(signal.SIGTERM, lambda: loop.create_task(websocket.close(), name='SIGTERM Signal Task'))

    logger.info('Sending init message')
    await websocket.send(json.dumps({
      'type': 'init',
      'language': args.language,
    }))

    init_message_response = await websocket.recv()
    logger.info(init_message_response)

    async def clear_sound_after_delay(data: DetectedSound) -> None:
      """Clear the sound from the published_sound_sentinel after a delay."""
      await asyncio.sleep(args.delay)  # Wait for the specified delay

      if data['sound'] in published_sound_sentinel:
        del published_sound_sentinel[data['sound']]  # Remove the sound from the dictionary

      if data['type'] == 'wakeword':
        send_clearing_message('wakeword')
      elif not published_sound_sentinel:
        send_clearing_message('sound')  # Clear if sentinel is empty

    async def detecting() -> None:
      nonlocal published_sound_sentinel

      try:
        async for message in websocket:
          data: DetectedSound = json.loads(message)
          type = data['type']

          # Only process the sound if its score is above the threshold
          if data['score'] >= args.threshold:
            schedule_clearing_task = False
            data['sound'] = get_slug(data['sound'])
            current_sound = data['sound']
            payload = json.dumps(data)

            if type == 'wakeword':
              mqtt_publish(type, payload)

              schedule_clearing_task = True
            else:
              # Only publish if the current sound is different from the last published sound
              if current_sound not in published_sound_sentinel:
                mqtt_publish(type, payload)

                schedule_clearing_task = True

            if schedule_clearing_task:
              # Add the sound to the sentinel dictionary and start a task to clear it after a delay
              published_sound_sentinel[current_sound] = asyncio.create_task(
                clear_sound_after_delay(data)
              )
      except asyncio.CancelledError:
        logger.info('Recording cancelled')
      finally:
        terminate()

    def terminate() -> None:
      nonlocal published_sound_sentinel

      set_availability(False)
      audio_stream.stop()
      mqtt_client.disconnect()

      for task in published_sound_sentinel.values():
        if task and not task.done():
          task.cancel()

    async def listening() -> None:
      logger.info(f'Listening from {audio_stream.device_name}...')
      set_availability(True)

      async with audio_stream:
        while not audio_stream.stream.closed:
          try:
            data = await audio_stream.data()
            await websocket.send(data)
          except websockets.exceptions.ConnectionClosedOK:
            logger.info('Connection closed')
            break
          except websockets.exceptions.ConnectionClosedError as error:
            logger.error(error)
            break
          except sd.PortAudioError as error:
            logger.error(error)
            await websocket.close()
            break

      logger.info('Stream closed')

    def handle_task_done(task: asyncio.Task) -> None:
      try:
        if task.exception() is not None:
          logger.error(task)
        elif task.cancelled():
          logger.info(f'{task.get_name()} cancelled')
        else:
          logger.info(f'{task.get_name()} done')
      except (asyncio.CancelledError, asyncio.InvalidStateError) as error:
        logger.error(error)

    detecting_task = loop.create_task(detecting(), name='Detection Task')
    listening_task = loop.create_task(listening(), name='Listening Task')

    detecting_task.add_done_callback(handle_task_done)
    listening_task.add_done_callback(handle_task_done)

    await asyncio.wait([detecting_task, listening_task])
