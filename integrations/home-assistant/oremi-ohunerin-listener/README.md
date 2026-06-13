# Oremi Ohunerin Listener - Home Assistant Integration

This custom component integrates the **Oremi Ohunerin Listener** into Home Assistant, automatically registering the MQTT sensors for wake word and sound detection.

## Installation

1. Copy the `oremi-ohunerin-listener` folder to your Home Assistant configuration directory under `custom_components/oremi_ohunerin_listener`.
2. Restart Home Assistant.

## Configuration

1. Navigate to **Settings** -> **Devices & Services** -> **Integrations**.
2. Click **Add Integration** and search for **Oremi Ohunerin Listener**.
3. Enter the MQTT topic prefix configured on your Oremi Ohunerin Listener (default: `oremi/ohunerin`).
