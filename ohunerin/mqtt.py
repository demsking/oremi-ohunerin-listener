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
from typing import Literal

import paho.mqtt.client as mqtt

from .logger import logger
from .models import DetectedSoundType


class MQTTClient:
  def __init__(
    self,
    broker: str,
    port: int,
    *,
    topic: str,
    username: str | None = None,
    password: str | None = None,
  ):
    self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    self.broker = broker
    self.port = port
    self.topic = topic
    self.username = username
    self.password = password

  def connect(self) -> None:
    if self.username:
      self.client.username_pw_set(username=self.username, password=self.password)
    self.client.connect(self.broker, self.port, keepalive=0)

  def publish(self, topic: DetectedSoundType | str, message: str, retain: bool = False) -> None:
    logger.debug(f"Publishing #{self.topic}/{topic}: {message} with retain {retain}")
    self.client.publish(f'{self.topic}/{topic}', message, retain=retain)

  def set_availability(self, available: bool) -> None:
    message: Literal['online', 'offline'] = 'online' if available else 'offline'
    self.publish('available', message, retain=True)

  def disconnect(self) -> None:
    self.client.disconnect()
