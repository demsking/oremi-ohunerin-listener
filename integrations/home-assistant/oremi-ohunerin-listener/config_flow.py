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
"""Config flow for Oremi Ohunerin Listener integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.config_entries import OptionsFlow
from homeassistant.core import callback

from .const import CONF_TOPIC_PREFIX
from .const import DEFAULT_TOPIC_PREFIX
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OhunerinListenerConfigFlow(ConfigFlow, domain=DOMAIN):
  """Handle a config flow for Oremi Ohunerin Listener."""

  VERSION = 1

  def __init__(self) -> None:
    """Initialize the config flow."""
    self._topic_prefix: str | None = None

  async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
    """Handle the initial step (Topic Prefix configuration)."""
    errors = {}

    # Check if MQTT is configured in Home Assistant
    if not self.hass.config_entries.async_entries("mqtt"):
      errors["base"] = "mqtt_required"

    if user_input is not None and not errors:
      prefix = user_input[CONF_TOPIC_PREFIX].strip("/")
      if not prefix:
        errors[CONF_TOPIC_PREFIX] = "invalid_prefix"
      else:
        await self.async_set_unique_id(prefix)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
          title=f"Oremi Ohunerin Listener ({prefix})",
          data={
            CONF_TOPIC_PREFIX: prefix,
          },
        )

    return self.async_show_form(
      step_id="user",
      data_schema=vol.Schema(
        {
          vol.Required(CONF_TOPIC_PREFIX, default=DEFAULT_TOPIC_PREFIX): str,
        }
      ),
      errors=errors,
    )

  @staticmethod
  @callback
  def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlow:
    """Create the options flow."""
    return OhunerinListenerOptionsFlowHandler(config_entry)


class OhunerinListenerOptionsFlowHandler(OptionsFlow):
  """Handle Options Flow for Oremi Ohunerin Listener."""

  def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
    """Initialize the options flow."""
    self.config_entry = config_entry

  async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
    """Manage the options."""
    errors = {}
    if user_input is not None:
      prefix = user_input[CONF_TOPIC_PREFIX].strip("/")
      if not prefix:
        errors[CONF_TOPIC_PREFIX] = "invalid_prefix"
      else:
        return self.async_create_entry(title="", data={CONF_TOPIC_PREFIX: prefix})

    current_prefix = self.config_entry.options.get(
      CONF_TOPIC_PREFIX, self.config_entry.data.get(CONF_TOPIC_PREFIX, DEFAULT_TOPIC_PREFIX)
    )

    return self.async_show_form(
      step_id="init",
      data_schema=vol.Schema(
        {
          vol.Required(CONF_TOPIC_PREFIX, default=current_prefix): str,
        }
      ),
      errors=errors,
    )
