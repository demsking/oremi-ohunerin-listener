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
import asyncio
import json
from datetime import datetime

from websockets.asyncio.client import ClientConnection as WebSocket

from .audio import Audio
from .logger import logger
from .models import DetectedSound
from .models import DetectedSoundType
from .mqtt import MQTTClient
from .string import get_slug


class SoundDetector:
  def __init__(
    self,
    mqtt_client: MQTTClient,
    websocket: WebSocket,
    audio_stream: Audio,
    *,
    delay: int,
    threshold: int,
  ):
    self.mqtt_client = mqtt_client
    self.websocket = websocket
    self.audio_stream = audio_stream
    self.delay = delay
    self.threshold = threshold
    self.published_sound_sentinel: dict[str, asyncio.Task] = {}

  async def clear_sound_after_delay(self, data: DetectedSound) -> None:
    await asyncio.sleep(self.delay)
    if data['sound'] in self.published_sound_sentinel:
      del self.published_sound_sentinel[data['sound']]
    if data['type'] == 'wakeword':
      self.send_clearing_message('wakeword')
    elif not self.published_sound_sentinel:
      self.send_clearing_message('sound')

  def send_clearing_message(self, type: DetectedSoundType) -> None:
    data: DetectedSound = {
      'type': type,
      'sound': '...',
      'score': 1.0,
      'date': datetime.now().isoformat(),
    }
    message = json.dumps(data)
    self.mqtt_client.publish(type, message, True)

  async def detecting(self) -> None:
    try:
      async for message in self.websocket:
        data: DetectedSound = json.loads(message)
        if data['score'] >= self.threshold:
          await self.process_detected_sound(data)
    except asyncio.CancelledError:
      logger.info('Recording cancelled')
    finally:
      self.terminate()

  async def process_detected_sound(self, data: DetectedSound) -> None:
    data['sound'] = get_slug(data['sound'])
    current_sound = data['sound']
    payload = json.dumps(data)

    if data['type'] == 'wakeword':
      self.mqtt_client.publish(data['type'], payload)
      self.schedule_clearing_task(data)
    elif current_sound not in self.published_sound_sentinel:
      self.mqtt_client.publish(data['type'], payload)
      self.schedule_clearing_task(data)

  def schedule_clearing_task(self, data: DetectedSound) -> None:
    self.published_sound_sentinel[data['sound']] = asyncio.create_task(self.clear_sound_after_delay(data))

  def terminate(self) -> None:
    self.mqtt_client.set_availability(False)
    self.audio_stream.stop()
    self.mqtt_client.disconnect()

    for task in self.published_sound_sentinel.values():
      if task and not task.done():
        task.cancel()
