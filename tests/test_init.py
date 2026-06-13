# Copyright 2026 Sébastien Demanou. All Rights Reserved.
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
import json
import urllib.parse

from ohunerin import build_connection_uri


def test_build_connection_uri_default() -> None:
  args = argparse.Namespace(
    features_file=None,
    language='fr',
    host='localhost',
    port=5023,
    cert_file=None,
  )
  uri = build_connection_uri(args)
  assert uri.startswith('ws://localhost:5023/ws?')

  # Parse the query params to verify
  parsed = urllib.parse.urlparse(uri)
  params = urllib.parse.parse_qs(parsed.query)
  assert params['features'] == ['wakeword-detection,sound-detection']
  assert params['language'] == ['fr']


def test_build_connection_uri_secure() -> None:
  args = argparse.Namespace(
    features_file=None,
    language='en',
    host='127.0.0.1',
    port=8000,
    cert_file='cert.pem',
  )
  uri = build_connection_uri(args)
  assert uri.startswith('wss://127.0.0.1:8000/ws?')

  parsed = urllib.parse.urlparse(uri)
  params = urllib.parse.parse_qs(parsed.query)
  assert params['features'] == ['wakeword-detection,sound-detection']
  assert params['language'] == ['en']


def test_build_connection_uri_with_features_file(tmp_path) -> None:
  features_content = [
    {
      'name': 'wakeword-detection',
      'language': 'en',
      'wakewords': [{'word': 'hey assistant', 'phones': ['hh ey aa ss ih ss t ah n t']}],
      'discriminants': [{'word': 'assistant', 'phones': ['aa ss ih ss t ah n t']}],
    },
    {'name': 'sound-detection', 'allowlist': ['Cough', 'Snoring']},
  ]
  features_file = tmp_path / 'features.json'
  features_file.write_text(json.dumps(features_content))

  args = argparse.Namespace(
    features_file=str(features_file),
    language='fr',  # should be overridden by features file for wakeword-detection
    host='localhost',
    port=5023,
    cert_file=None,
  )
  uri = build_connection_uri(args)
  assert uri.startswith('ws://localhost:5023/ws?')

  parsed = urllib.parse.urlparse(uri)
  params = urllib.parse.parse_qs(parsed.query)
  assert params['features'] == ['wakeword-detection,sound-detection']
  assert params['language'] == ['en']

  wakewords = json.loads(params['wakewords'][0])
  assert wakewords[0]['word'] == 'hey assistant'

  discriminants = json.loads(params['discriminants'][0])
  assert discriminants[0]['word'] == 'assistant'

  assert params['allowlist'] == ['Cough,Snoring']
