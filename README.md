# Oremi Ohunerin MQTT

[![Buy me a beer](https://img.shields.io/badge/Buy%20me-a%20beer-1f425f.svg)](https://www.buymeacoffee.com/demsking)

Oremi Ohunerin MQTT is an MQTT implementation of **[Oremi Ohunerin](https://gitlab.com/demsking/oremi-ohunerin)**,
the real-time audio detection component of the **Oremi Personal Assistant**
project. It connects to the Oremi Ohunerin WebSocket server, detects
environmental sounds and wake words, and publishes the results to an MQTT
broker.

This project is designed to integrate seamlessly with home automation systems
like **Home Assistant**, IoT platforms, or any application that uses MQTT for
communication. It is available as a Docker image for both `linux/amd64` and
`linux/arm64` architectures.

## Overview

### What is Oremi Ohunerin?

[Oremi Ohunerin](https://gitlab.com/demsking/oremi-ohunerin) is the real-time
audio detection component of the **Oremi Personal Assistant** project. It
operates as a WebSocket server and is capable of identifying environmental
sounds and specific wake words to activate Oremi. It leverages cutting-edge
technologies such as:

- **Tensorflow YAMNet**: For comprehensive audio detection.
- **PocketSphinx**: For precise wake word identification.

It can recognize various sound categories, including but not limited to:
- Shouts
- Laughter
- Crying
- Snoring
- Coughing
- And more.

### What is Oremi Ohunerin MQTT?

Oremi Ohunerin MQTT bridges the gap between Oremi Ohunerin and MQTT-based
systems. It:

1. Connects to the Oremi Ohunerin WebSocket server.
2. Listens for detected sounds and wake words.
3. Publishes the results to an MQTT topic.

This allows you to integrate Oremi Ohunerin's audio detection capabilities into
your MQTT-enabled ecosystem, such as **Home Assistant**, for advanced home
automation and monitoring.

## Features

- **Real-Time Audio Detection**: Detects environmental sounds and wake words in
  real time.
- **MQTT Integration**: Publishes detected sounds and wake words to an MQTT
  broker.
- **Home Assistant Compatibility**: Easily integrates with Home Assistant for
  automations, notifications, and dashboards.
- **Customizable Threshold**: Set a confidence score threshold for sound
  detection.
- **Cooldown Period**: Avoids publishing the same sound repeatedly within a
  specified delay.
- **Docker Support**: Available as a Docker image for easy deployment.
- **Cross-Platform**: Supports both `linux/amd64` and `linux/arm64`
  architectures.

## Quick Start

### Prerequisites

1. **Docker**: Ensure Docker is installed on your system.
2. **MQTT Broker**: An MQTT broker (e.g., Mosquitto) must be running and
   accessible.
3. **Home Assistant**: For integration and automation (optional but
   recommended).

### Docker Compose Example

Here’s a quick example of how to use Oremi Ohunerin MQTT with Docker Compose:

```yaml
services:
  detector:
    image: demsking/oremi-ohunerin

  listener:
    image: demsking/oremi-ohunerin-mqtt
    devices:
      - /dev/snd:/dev/snd # Mount the microphone device
    volumes:
      - $XDG_RUNTIME_DIR/pulse/native:/var/config/pulse/native
      - ~/.config/pulse/cookie:/var/config/pulse/cookie
    env_file:
      - .env
    command: listen --host detector --mqtt-broker mqtt.eclipseprojects.io --mqtt-port 1883
```

### Explanation

- **`detector`**: The Oremi Ohunerin WebSocket server.
- **`listener`**: The Oremi Ohunerin MQTT client.
  - Mounts the microphone device for audio input.
  - Connects to the MQTT broker at `mqtt.eclipseprojects.io:1883`.
  - Publishes detected sounds and wake words to the MQTT topic `oremi/ohunerin`.

## Command-Line Arguments

### General Usage

To see the general usage and available commands, run:

```bash
docker run -it --rm demsking/oremi-ohunerin-mqtt -h
```

Output:

```
usage: oremi-ohunerin-mqtt [-h] [-v] {listen} ...

Real-time ambient sound and wake word detection

positional arguments:
  {listen}
    listen       Start listening

options:
  -h, --help     show this help message and exit
  -v, --version  Show the version of the application.
  --list-devices List available input devices.
```

### Listen Command

To see the options for the `listen` command, run:

```bash
docker run -it --rm demsking/oremi-ohunerin-mqtt listen -h
```

Output:

```
usage: oremi-ohunerin-mqtt listen [-h] [-l LANGUAGE] [-i DEVICE_INDEX] [-d DEVICE] [-t THRESHOLD] [--delay DELAY] [--host HOST]
                                  [-p PORT] [--cert-file CERT_FILE] --mqtt-broker MQTT_BROKER [--mqtt-port MQTT_PORT]
                                  [--mqtt-username MQTT_USERNAME] [--mqtt-password MQTT_PASSWORD] [--mqtt-topic MQTT_TOPIC]

options:
  -h, --help            show this help message and exit
  -l LANGUAGE, --language LANGUAGE
                        The language to use for wake word detection and audio processing. Default is "fr" (French).
  -i DEVICE_INDEX, --device-index DEVICE_INDEX
                        Index of the audio device to be used for recording audio.
  -d DEVICE, --device DEVICE
                        Name of the device.
  -t THRESHOLD, --threshold THRESHOLD
                        The minimum confidence score required to process a sound event (default: 0.85).
  --delay DELAY         The cooldown period (in seconds) to wait before sending the same sound event again (default: 3).
  --host HOST           Host address to connect to.
  -p PORT, --port PORT  Port number to connect to (default: 5023).
  --cert-file CERT_FILE
                        Path to the certificate file for secure connection.
  --mqtt-broker MQTT_BROKER
                        The address of the MQTT broker.
  --mqtt-port MQTT_PORT
                        The port of the MQTT broker. Default is 1883.
  --mqtt-username MQTT_USERNAME
                        The username for authenticating with the MQTT broker. Default is None.
  --mqtt-password MQTT_PASSWORD
                        The password for authenticating with the MQTT broker. Default is None.
  --mqtt-topic MQTT_TOPIC
                        The MQTT topic to publish audio detection events to. Default is "oremi/ohunerin".
```

## MQTT Topics

Oremi Ohunerin MQTT publishes detected sounds and wake words to the following MQTT topics:

- **`oremi/ohunerin/sound`**: For environmental sound detection events.
- **`oremi/ohunerin/wakeword`**: For wake word detection events.
- **`oremi/ohunerin/available`**: For availability status (`online` or `offline`).

Each message is published as a JSON object with the following structure:

```json
{
  "type": "sound" | "wakeword",
  "sound": "detected_sound",
  "score": 0.85,
  "date": "2023-10-05T12:34:56Z"
}
```

## Home Assistant Integration

Oremi Ohunerin MQTT is an excellent tool for integrating real-time audio
detection into **Home Assistant**. By publishing detected sounds and wake words
to MQTT topics, you can create automations, notifications, and dashboards in
Home Assistant based on audio events.

### Example Use Case

Imagine you want to:
1. Detect when someone is snoring in a room.
2. Trigger a notification if a baby is crying.
3. Activate a wake word to start a specific automation.

With Oremi Ohunerin MQTT and Home Assistant, you can achieve this seamlessly.

### Home Assistant Configuration

Here’s an example of how to configure Home Assistant to work with Oremi Ohunerin
MQTT:

#### `configuration.yaml`

```yaml
mqtt:
  sensor:
    - name: "Wakeword"
      unique_id: "oremi_ohunerin_wakeword"
      state_topic: "oremi/ohunerin/wakeword"
      enabled_by_default: true
      icon: "mdi:waveform"
      device_class: "enum"
      options:
        - detected
        - 💤
      value_template: >-
        {% if value_json.sound == '...' %}
          💤
        {% else %}
          detected
        {% endif %}
      availability: &oremi-ohunerin-availability
        - topic: "oremi/ohunerin/available"
          payload_available: "online"
          payload_not_available: "offline"
      device: &oremi-ohunerin-device
        name: "Oremi Ohunerin"
        manufacturer: "Sébastien Demanou"
        configuration_url: "https://gitlab.com/demsking/oremi-ohunerin"
        identifiers: "oremi-ohunerin-1.0.0"
        sw_version: "1.0.0"

    - name: "Sound Detector"
      unique_id: "oremi_ohunerin_sound"
      state_topic: "oremi/ohunerin/sound"
      enabled_by_default: true
      icon: "mdi:waveform"
      device_class: "enum"
      options:
        - shout
        - bellows
        - children-shouting
        - laughter
        - baby-laughter
        - crying-sobbing
        - baby-cry-infant-cry
        - whistling
        - wheeze
        - snoring
        - cough
        - sneeze
        - burping
        - hiccup
        - 💤
      value_template: >-
        {% if value_json.sound == '...' %}
          💤
        {% else %}
          {{ value_json.sound }}
        {% endif %}
      availability: *oremi-ohunerin-availability
      device: *oremi-ohunerin-device
```

### Example Automations

#### 1. Snoring Detection

Send a notification when snoring is detected:

```yaml
automation:
  - alias: "Notify on Snoring"
    description: Sends a notification when snoring is detected.
    triggers:
      - trigger: state
        entity_id:
          - sensor.oremi_ohunerin_snoring_detector
    action:
      service: notify.notify
      data:
        message: "Snoring detected!"
```

#### 2. Baby Cry Alert

Send an urgent notification when a baby cry is detected:

```yaml
automation:
  - alias: Notify on Baby Cry
    description: Sends an urgent notification when a baby cry is detected.
    triggers:
      - trigger: state
        entity_id:
          - sensor.oremi_ohunerin_baby_cry_infant_cry_detector
    actions:
      - action: notify.notify
        data:
          message: Baby is crying! Check immediately.
```

#### 3. Wake Word Activation

Trigger an automation when the wake word is detected:

```yaml
automation:
  - alias: Wake Word Detected
    description: Triggered when the wake word is detected. Activates the Oremi Assistant script.
    triggers:
      - trigger: state
        entity_id:
          - sensor.oremi_ohunerin_wake_word
        to: detected
    actions:
      - target:
          entity_id: script.start_oremi_assistant
        action: script.turn_on
        data: {}
    mode: single
```

### Benefits of This Integration

- **Real-Time Alerts**: Get instant notifications for specific sounds.
- **Automations**: Trigger actions based on detected sounds or wake words.
- **Dashboards**: Display sound detection states on your Home Assistant
  dashboard.
- **Customizable**: Easily adapt to your specific needs by modifying the
  configuration.

This integration makes Oremi Ohunerin MQTT a powerful tool for enhancing your
smart home with advanced audio detection capabilities.

## Contribute

Please follow [CONTRIBUTING.md](https://gitlab.com/demsking/oremi-ohunerin-mqtt/blob/main/CONTRIBUTING.md).

## Versioning

Given a version number `MAJOR.MINOR.PATCH`, increment the:

- `MAJOR` version when you make incompatible API changes,
- `MINOR` version when you add functionality in a backwards-compatible manner,
  and
- `PATCH` version when you make backwards-compatible bug fixes.

Additional labels for pre-release and build metadata are available as extensions
to the `MAJOR.MINOR.PATCH` format.

See [SemVer.org](https://semver.org/) for more details.

## License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.
You may obtain a copy of the License at [LICENSE](https://gitlab.com/demsking/oremi-ohunerin-mqtt/blob/main/LICENSE).
