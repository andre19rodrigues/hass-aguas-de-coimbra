import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .adc_client import AdCClient
from .const import DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AdCCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch water usage data from Aguas de Coimbra."""

    def __init__(self, hass: HomeAssistant, client: AdCClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Aguas de Coimbra Coordinator",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )
        self.client = client
        self._cached_meter_reading = 0
        self._cached_yesterday = 0
        self._last_update = None

    async def _async_update_data(self) -> dict:
        """Fetch updated data from the API."""

        # Get today's water usage
        today_consumption = await self.client.get_consumption(today=True)

        now = dt_util.now()
        today_str = now.strftime("%Y-%m-%d")
        if self._last_update != today_str:
            # Only fetch yesterday's consumption and meter reading if the date has changed
            # This is to avoid unnecessary API calls
            _LOGGER.debug("Fetching new yesterday_consumption and meter_reading")
            self._cached_meter_reading = await self.client.get_last_meter_reading()
            self._cached_yesterday = await self.client.get_consumption(today=False)
            # Since the meter reading is usually updated around midnight,
            # it's better to cache it only after 1 AM to allow some buffer time for the update
            if now.hour >= 1:
                self._last_update = today_str
        else:
            _LOGGER.debug("Using cached yesterday_consumption and meter_reading")

        return {
            "today_consumption": today_consumption,
            "yesterday_consumption": self._cached_yesterday,
            "meter_reading": self._cached_meter_reading,
        }
