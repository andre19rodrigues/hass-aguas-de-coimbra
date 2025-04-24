import logging
from datetime import date

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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

        today_str = date.today().strftime("%Y-%m-%d")
        if self._last_update != today_str:
            _LOGGER.debug("Fetching new yesterday_consumption")
            self._cached_meter_reading = await self.client.get_last_meter_reading()
            self._cached_yesterday = await self.client.get_consumption(today=False)
            self._last_update = today_str
        else:
            _LOGGER.debug("Using cached yesterday_consumption and meter_reading")

        # Calculate the estimated meter reading
        # based on the cached meter reading and today's consumption
        # Convert today's consumption from liters to cubic meters
        today_cubic_meters = today_consumption / 1000
        meter_reading_estimated = self._cached_meter_reading + today_cubic_meters
        # Round to 2 decimal places
        meter_reading_estimated = round(meter_reading_estimated, 2)
        return {
            "today_consumption": today_consumption,
            "yesterday_consumption": self._cached_yesterday,
            "meter_reading_official": self._cached_meter_reading,
            "meter_reading_estimated": meter_reading_estimated,
        }
