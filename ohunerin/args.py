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

from .package import APP_DESCRIPTION
from .package import APP_NAME
from .package import APP_VERSION


def parse_arguments() -> argparse.Namespace:
  parser = argparse.ArgumentParser(prog=APP_NAME, description=APP_DESCRIPTION)
  subparsers = parser.add_subparsers(dest='command')

  parser.add_argument(
    '-v', '--version',
    action='version',
    version=f'%(prog)s {APP_VERSION}',
    help='Show the version of the application.'
  )

  #
  # Listen
  listen = subparsers.add_parser(name='listen', help='Start listening')

  listen.add_argument(
    '-l', '--language',
    type=str,
    default='fr',
    help='The language to use for wake word detection and audio processing. Default is "fr" (French).',
  )

  listen.add_argument(
    '-i', '--device-index',
    type=int,
    default=None,
    help='Index of the audio device to be used for recording audio.',
  )

  listen.add_argument(
    '-d', '--device',
    type=str,
    default=None,
    help='Name of the device.',
  )

  listen.add_argument(
    '-t', '--threshold',
    type=float,
    default=0.85,
    help='The minimum confidence score required to process a sound event (default: 0.85).'
  )

  listen.add_argument(
    '--delay',
    type=int,
    default=3,
    help='The cooldown period (in seconds) to wait before sending the same sound event again (default: 3).'
  )

  listen.add_argument(
    '--host',
    type=str,
    help='Host address to connect to.',
  )

  listen.add_argument(
    '-p', '--port',
    type=int,
    default=5023,
    help='Port number to connect to (default: 5023).',
  )

  listen.add_argument(
    '--cert-file',
    type=str,
    help='Path to the certificate file for secure connection.',
  )

  # listen.add_argument(
  #   '--key-file',
  #   type=str,
  #   help='Path to the private key file for secure connection.',
  # )

  # listen.add_argument(
  #   '--password',
  #   type=str,
  #   help='Password to unlock the private key (if protected by a password).',
  # )

  # MQTT Broker address
  listen.add_argument(
    '--mqtt-broker',
    type=str,
    required=True,
    help='The address of the MQTT broker.'
  )

  # MQTT Broker port
  listen.add_argument(
    '--mqtt-port',
    type=int,
    default=1883,
    help='The port of the MQTT broker. Default is 1883.'
  )

  # MQTT Username
  listen.add_argument(
    '--mqtt-username',
    type=str,
    default=None,
    help='The username for authenticating with the MQTT broker. Default is None.'
  )

  # MQTT Password
  listen.add_argument(
    '--mqtt-password',
    type=str,
    default=None,
    help='The password for authenticating with the MQTT broker. Default is None.'
  )

  # MQTT Topic
  listen.add_argument(
    '--mqtt-topic',
    type=str,
    default='oremi/ohunerin',
    help='The MQTT topic to publish audio detection events to. Default is "oremi/ohunerin".'
  )

  return parser.parse_args()
