from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .adc_client import AdCClient, CannotConnect, InvalidAuth
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
            client = AdCClient(
                user_input["username"],
                user_input["password"],
                user_input["billing_cycle_start_day"],
                user_input["social_tariff"],
                session=session,
            )

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
                    data={},
                    options={
                        "username": user_input["username"],
                        "password": user_input["password"],
                        "billing_cycle_start_day": user_input[
                            "billing_cycle_start_day"
                        ],
                        "social_tariff": user_input.get("social_tariff", False),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("username"): str,
                    vol.Required("password"): str,
                    vol.Required("billing_cycle_start_day", default=1): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=28)
                    ),
                    vol.Optional("social_tariff", default=False): bool,
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return ADCOptionsFlowHandler(config_entry)


class ADCOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle config options for Águas de Coimbra."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "username",
                        default=self.config_entry.options.get(
                            "username", self.config_entry.data.get("username", "")
                        ),
                    ): str,
                    vol.Required("password", description={"suggested_value": ""}): str,
                    vol.Required(
                        "billing_cycle_start_day",
                        default=self.config_entry.options.get(
                            "billing_cycle_start_day",
                            self.config_entry.data.get("billing_cycle_start_day", 1),
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=28)),
                    vol.Optional(
                        "social_tariff",
                        default=self.config_entry.options.get(
                            "social_tariff",
                            self.config_entry.data.get("social_tariff", False),
                        ),
                    ): bool,
                }
            ),
        )
