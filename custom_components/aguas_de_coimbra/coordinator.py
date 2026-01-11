import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .adc_client import AdCClient
from .const import DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AdCCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch water usage data from Aguas de Coimbra."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Aguas de Coimbra Coordinator",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )

        username = config_entry.options.get(
            "username", config_entry.data.get("username")
        )
        password = config_entry.options.get(
            "password", config_entry.data.get("password")
        )
        billing_day = config_entry.options.get(
            "billing_cycle_start_day",
            config_entry.data.get("billing_cycle_start_day", 1),
        )
        social_tariff = config_entry.options.get(
            "social_tariff", config_entry.data.get("social_tariff", False)
        )
        session = async_get_clientsession(hass)

        self.client = AdCClient(username, password, billing_day, social_tariff, session)
        self._cached_meter_reading = 0
        self._cached_yesterday = 0
        self._last_update = None

        self._data = {
            "today_consumption": 0,
            "yesterday_consumption": 0,
            "meter_reading": 0,
            "billing_cycle_consumption": 0,
            "billing_cycle_cost": 0,
            "last_successful_refresh": None,
        }

    async def _async_update_data(self) -> dict:
        """Fetch updated data from the API."""

        now = dt_util.now()
        today_str = now.strftime("%Y-%m-%d")
        self._data["last_successful_refresh"] = now

        # Try to get today's consumption
        try:
            today_consumption = await self.client.get_consumption_day(today=True)
            self._data["today_consumption"] = today_consumption
        except Exception as err:
            _LOGGER.warning("Failed to fetch today's consumption: %s", err)

        # Try to get billing cycle consumption
        try:
            billing_cycle = await self.client.get_consumption_billing_cycle()
            self._data["billing_cycle_consumption"] = billing_cycle
        except Exception as err:
            _LOGGER.warning("Failed to fetch billing cycle consumption: %s", err)

        # Try to calculate billing cycle cost
        try:
            billing_cycle_cost = self.client.calculate_cost(
                self._data["billing_cycle_consumption"]
            )
            self._data["billing_cycle_cost"] = billing_cycle_cost
        except Exception as err:
            _LOGGER.warning("Failed to calculate billing cycle cost: %s", err)

        # Only update meter reading and yesterday if it's a new day
        if self._last_update != today_str:
            # Only fetch yesterday's consumption and meter reading if the date has changed
            # This is to avoid unnecessary API calls
            _LOGGER.debug("Fetching new yesterday_consumption and meter_reading")

            try:
                self._cached_meter_reading = await self.client.get_last_meter_reading()
                self._data["meter_reading"] = self._cached_meter_reading
            except Exception as err:
                _LOGGER.warning("Failed to fetch last meter reading: %s", err)

            try:
                self._cached_yesterday = await self.client.get_consumption_day(
                    today=False
                )
                self._data["yesterday_consumption"] = self._cached_yesterday
            except Exception as err:
                _LOGGER.warning("Failed to fetch yesterday's consumption: %s", err)

            if now.hour >= 5:
                # Meter reading is usually updated around midnight. 
                # "Yesterday" might take a few hours to be fully updated.
                # Cache it only after 5 AM to allow some buffer time for the update
                self._last_update = today_str
        else:
            _LOGGER.debug("Using cached yesterday_consumption and meter_reading")

        return self._data
