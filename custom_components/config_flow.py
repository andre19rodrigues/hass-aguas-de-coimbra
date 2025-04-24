from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .adc_client import AdCClient
from .adc_client import CannotConnect
from .adc_client import InvalidAuth
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


class ADCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Águas de Coimbra."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            session = aiohttp.ClientSession()
            client = AdCClient(user_input["username"], user_input["password"], session)

            try:
                await client.login()
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as e:
                _LOGGER.exception("Unexpected error: %s", e)
                errors["base"] = "unknown"
            finally:
                await session.close()

            if not errors:
                return self.async_create_entry(
                    title="Águas de Coimbra",
                    data={
                        "username": user_input["username"],
                        "password": user_input["password"],
                    }
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("username"): str,
                vol.Required("password"): str,
            }),
            errors=errors
        )
