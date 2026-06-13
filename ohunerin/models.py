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
import json
from dataclasses import dataclass
from dataclasses import field
from typing import Literal
from typing import TypedDict

from dataclasses_json import dataclass_json


DetectedSoundType = Literal['sound', 'wakeword']


class DetectedSound(TypedDict):
  """
  Example: {"type": "sound", "sound": "snoring", "score": 0.109375, "datetime": "2023-08-16T14:42:46.424809"}
  """

  type: DetectedSoundType
  sound: str
  score: float
  date: str


@dataclass_json
@dataclass
class Wakeword:
  word: str
  phones: list[str]


@dataclass_json
@dataclass
class Discriminant:
  word: str
  phones: list[str]


@dataclass_json
@dataclass
class WakewordDetectionFeature:
  name: Literal['wakeword-detection'] = 'wakeword-detection'
  language: Literal['fr', 'en'] = 'fr'
  wakewords: list[Wakeword] = field(default_factory=list)
  discriminants: list[Discriminant] = field(default_factory=list)


@dataclass_json
@dataclass
class SoundDetectionFeature:
  name: Literal['sound-detection'] = 'sound-detection'
  allowlist: list[str] = field(default_factory=list)


@dataclass_json
@dataclass
class ClientInitMessage:
  type: Literal['init']
  features: list[WakewordDetectionFeature | SoundDetectionFeature]

  @classmethod
  def from_file(cls, features_file: str):
    features = []

    with open(features_file, 'r', encoding='utf-8') as file:
      data = json.load(file)

    if isinstance(data, list):
      for feature_data in data:
        if feature_data['name'] == 'wakeword-detection':
          features.append(WakewordDetectionFeature.from_dict(feature_data))
        elif feature_data['name'] == 'sound-detection':
          features.append(SoundDetectionFeature.from_dict(feature_data))
    else:
      raise ValueError('Invalid features file format: expected an array')

    return cls(type='init', features=features)


class ServerInitMessage(TypedDict):
  type: Literal['init']
  server: str
  status: str
  languages: list[str]
