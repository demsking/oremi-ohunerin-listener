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
from typing import Any

import sounddevice as sd


class Audio:
  def __init__(
    self,
    *,
    dtype='int16',
    samplerate=16000,
    blocksize=8000,
    device_index: int | None = None,
  ) -> None:
    loop = asyncio.get_event_loop()
    self.audio_queue = asyncio.Queue[bytes]()
    self.samplerate = samplerate
    self.blocksize = blocksize
    device = device_index or Audio.find_compatible_device()

    if isinstance(device, dict):
      device = device['index']

    self.stream = sd.RawInputStream(
      dtype=dtype,
      samplerate=samplerate,
      blocksize=blocksize,
      device=device or None,
      channels=1,
      callback=lambda indata, frames, time, status: loop.call_soon_threadsafe(
        self.audio_queue.put_nowait,
        bytes(indata),
      ),
    )

  async def __aenter__(self):
    self.stream.start()
    return self

  async def __aexit__(self, exc_type, exc, tb):
    self.stream.stop()
    self.stream.close()

  def __str__(self) -> str:
    return f'{self.device_name} with samplerate {self.samplerate}, blocksize {self.blocksize}, channels {self.stream.channels}'

  @property
  def device_name(self) -> str:
    device_info = sd.query_devices(self.stream.device, 'input')
    return device_info['name']  # type: ignore

  @property
  def info(self):
    return {
      'samplerate': self.samplerate,
      'dtype': self.stream.dtype,
      'channels': self.stream.channels,
      'blocksize': self.blocksize,
      'device': self.stream.device,
    }

  @staticmethod
  def find_compatible_device() -> dict | None:
    devices = sd.query_devices()

    for device in devices:
      # Check if the device is an input device
      if device['max_input_channels'] > 0:  # type: ignore
        try:
          sd.check_input_settings(device=device['name'], samplerate=16000)  # type: ignore
          return device  # type: ignore
        except Exception as _exception:
          # If the device does not support the given sample rate, an exception is raised
          pass

    return None

  async def data(self):
    return await self.audio_queue.get()

  def stop(self) -> None:
    if self.stream.active:
      self.stream.stop()

  @staticmethod
  def list_input_devices() -> None:
    devices: Any = sd.query_devices()

    if len(devices) > 0:
      print('Available input devices:')
      for index, device in enumerate(devices):
        if device['max_input_channels'] > 0:
          print(f"  {index}. {device['name']} - {device['max_input_channels']} channel(s) - Sample rate: {device['default_samplerate']} Hz")
    else:
      print('No available input devices found')
