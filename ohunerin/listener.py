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
import sounddevice as sd
import websockets.exceptions
import websockets.legacy.client
from websockets.asyncio.client import ClientConnection as WebSocket

from .audio import Audio
from .logger import logger
from .mqtt import MQTTClient


class AudioListener:
  def __init__(self, audio_stream: Audio, websocket: WebSocket, mqtt_client: MQTTClient):
    self.audio_stream = audio_stream
    self.websocket = websocket
    self.mqtt_client = mqtt_client

  async def listening(self) -> None:
    logger.info(f"Listening from {self.audio_stream.device_name}...")
    self.mqtt_client.set_availability(True)

    async with self.audio_stream:
      while not self.audio_stream.stream.closed:
        try:
          data = await self.audio_stream.data()
          await self.websocket.send(data)
        except websockets.exceptions.ConnectionClosedOK:
          logger.info('Connection closed')
          break
        except websockets.exceptions.ConnectionClosedError as error:
          logger.error(error)
          break
        except sd.PortAudioError as error:
          logger.error(error)
          await self.websocket.close()
          break

    logger.info('Stream closed')
