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
"""The Oremi Ohunerin Listener integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_TOPIC_PREFIX

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass
class OhunerinListenerRuntimeData:
  """Runtime data stored in ConfigEntry."""

  topic_prefix: str


# ConfigEntry type alias
OhunerinListenerConfigEntry = ConfigEntry[OhunerinListenerRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: OhunerinListenerConfigEntry) -> bool:
  """Set up Oremi Ohunerin Listener from a config entry."""
  topic_prefix = entry.options.get(CONF_TOPIC_PREFIX, entry.data.get(CONF_TOPIC_PREFIX, "oremi/ohunerin"))

  # Store runtime data directly on entry
  entry.runtime_data = OhunerinListenerRuntimeData(
    topic_prefix=topic_prefix,
  )

  # Register listener to handle option updates
  entry.async_on_unload(entry.add_update_listener(async_update_options))

  await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
  return True


async def async_unload_entry(hass: HomeAssistant, entry: OhunerinListenerConfigEntry) -> bool:
  """Unload a config entry."""
  return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_options(hass: HomeAssistant, entry: OhunerinListenerConfigEntry) -> None:
  """Handle options update."""
  # Reload the platforms to apply option changes
  await hass.config_entries.async_reload(entry.entry_id)
