from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .adc_client import AdCClient
from .coordinator import AdCCoordinator
from .const import DOMAIN


PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration via config flow."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)

    client = AdCClient(
        username=entry.data["username"],
        password=entry.data["password"],
        session=session
    )

    await client.get_meter_details()

    # Create the coordinator
    coordinator = AdCCoordinator(hass, client)

    # Run the coordinator for the first time to fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator
    }

    # Forward sensor setup to Home Assistant
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload adc config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
