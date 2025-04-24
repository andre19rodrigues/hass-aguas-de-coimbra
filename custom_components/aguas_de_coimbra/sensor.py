from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfVolume
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AdCCoordinator

SENSOR_TYPES = {
    "today_consumption": {
        "name": "Today's Consumption",
        "unit": UnitOfVolume.LITERS,
        "icon": "mdi:water",
        "device_class": "water",
    },
    "yesterday_consumption": {
        "name": "Yesterday's Consumption",
        "unit": UnitOfVolume.LITERS,
        "icon": "mdi:water",
        "device_class": "water",
    },
    "meter_reading_official": {
        "name": "Official Meter Reading",
        "unit": UnitOfVolume.CUBIC_METERS,
        "icon": "mdi:gauge",
        "device_class": "water",
        "state_class": "total_increasing",
    },
    "meter_reading_estimated": {
        "name": "Estimated Meter Reading",
        "unit": UnitOfVolume.CUBIC_METERS,
        "icon": "mdi:gauge",
        "device_class": "water",
        "state_class": "total_increasing",
    },
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up ADC sensors based on a config entry."""
    coordinator: AdCCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [ADCSensor(coordinator, key, entry.entry_id) for key in SENSOR_TYPES]
    async_add_entities(sensors)


class ADCSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Águas de Coimbra data."""

    def __init__(self, coordinator: AdCCoordinator, sensor_type: str, entry_id: str):
        super().__init__(coordinator)
        self.type = sensor_type
        self.entry_id = entry_id
        self._attr_name = f"{SENSOR_TYPES[sensor_type]['name']}"
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type]["unit"]
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        self._attr_has_entity_name = True
        self._attr_device_class = SENSOR_TYPES[sensor_type].get("device_class")
        self._attr_state_class = SENSOR_TYPES[sensor_type].get("state_class")

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "aguas_de_coimbra")},
            name="Águas de Coimbra",
            manufacturer="Águas de Coimbra",
            entry_type="service",
        )

    @property
    def unique_id(self) -> str:
        return f"{self.entry_id}_{self.type}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self.type)
