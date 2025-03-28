from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "sportyhq_rating": {
        "name": "SportyHQ Rating",
        "unit_of_measurement": "points",
        "icon": "mdi:racquetball",
    },
    "rating_confidence": {
        "name": "SportyHQ Rating Confidence",
        "unit_of_measurement": "%",
        "icon": "mdi:shield-check",
    },
    "matches_ytd": {
        "name": "SportyHQ Matches YTD",
        "unit_of_measurement": "games",
        "icon": "mdi:calendar",
    },
    "matches_all_time": {
        "name": "SportyHQ Matches All Time",
        "unit_of_measurement": "games",
        "icon": "mdi:history",
    },
}

class SportyHQSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sensor_type, config_entry_id):
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._name = SENSOR_TYPES[sensor_type]["name"]
        self._unit_of_measurement = SENSOR_TYPES[sensor_type]["unit_of_measurement"]
        self._icon = SENSOR_TYPES[sensor_type]["icon"]
        self._config_entry_id = config_entry_id

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        # Log the data being accessed for debugging
        _LOGGER.debug("Accessing state for sensor '%s': %s", self._sensor_type, self.coordinator.data)
        raw_value = self.coordinator.data.get(self._sensor_type)
        # Strip out anything that's not numeric
        return ''.join(filter(str.isdigit, raw_value)) if raw_value else None

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def icon(self):
        return self._icon

    @property
    def device_info(self):
        """Return device information for the SportyHQ device."""
        return {
            "identifiers": {(DOMAIN, self._config_entry_id)},
            "name": "SportyHQ",
            "manufacturer": "SportyHQ",
            "model": "SportyHQ Integration",
            "entry_type": "service",
        }

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._config_entry_id}_{self._sensor_type}"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up SportyHQ sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    if not coordinator.data:
        _LOGGER.error("No data available from coordinator to create sensors")
        return

    # Log the data being used to create sensors
    _LOGGER.debug("Coordinator data for sensors: %s", coordinator.data)

    sensors = [
        SportyHQSensor(coordinator, sensor, config_entry.entry_id)
        for sensor in SENSOR_TYPES
    ]
    async_add_entities(sensors)
