"""Support for OCEAN Mining Pool binary sensors."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OCEAN Mining Pool binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # Add worker status binary sensors dynamically
    workers = coordinator.data.get("workers", {})
    for worker_name in workers:
        entities.append(
            OceanWorkerStatusSensor(
                coordinator=coordinator,
                worker_name=worker_name,
            )
        )
    
    async_add_entities(entities)
    
    # Listen for coordinator updates to add new workers
    @callback
    def _async_add_new_workers():
        """Add binary sensors for newly discovered workers."""
        new_entities = []
        current_workers = coordinator.data.get("workers", {})
        
        # Find workers that don't have entities yet
        existing_workers = {
            entity.worker_name
            for entity in entities
            if isinstance(entity, OceanWorkerStatusSensor)
        }
        
        new_workers = set(current_workers.keys()) - existing_workers
        
        for worker_name in new_workers:
            new_entity = OceanWorkerStatusSensor(
                coordinator=coordinator,
                worker_name=worker_name,
            )
            new_entities.append(new_entity)
            entities.append(new_entity)
        
        if new_entities:
            _LOGGER.info(f"Adding {len(new_entities)} binary sensors for new workers")
            async_add_entities(new_entities)
    
    # Subscribe to coordinator updates
    entry.async_on_unload(
        coordinator.async_add_listener(_async_add_new_workers)
    )


class OceanWorkerStatusSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for OCEAN worker online/offline status."""

    def __init__(self, coordinator, worker_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.worker_name = worker_name
        
        # Sanitize worker name for entity ID (keep underscores)
        safe_worker_name = worker_name.replace(" ", "_").replace("-", "_")
        
        self._attr_unique_id = f"{coordinator.username}_{safe_worker_name}_status"
        # Remove "OCEAN" prefix from entity names
        self._attr_name = f"{worker_name} Status"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_icon = "mdi:server-network"

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return device info - each worker is its own device."""
        return entity.DeviceInfo(
            identifiers={(DOMAIN, f"{self.coordinator.username}_{self.worker_name}")},
            name=f"{self.worker_name}",
            manufacturer="OCEAN Mining Pool",
            model="Worker",
            configuration_url="https://ocean.xyz",
            via_device=(DOMAIN, self.coordinator.username),
        )

    @property
    def is_on(self) -> bool:
        """Return true if the worker is active (has shares in last 60s)."""
        workers = self.coordinator.data.get("workers", {})
        worker_data = workers.get(self.worker_name)
        
        if not worker_data:
            return False
        
        return worker_data.get("is_active", False)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.available or not self.coordinator.last_update_success:
            return False
        
        # Worker is available if it exists in the data
        workers = self.coordinator.data.get("workers", {})
        return self.worker_name in workers

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional attributes."""
        workers = self.coordinator.data.get("workers", {})
        worker_data = workers.get(self.worker_name, {})
        
        return {
            "hashrate_60s": worker_data.get("hashrate_60s", 0),
            "hashrate_300s": worker_data.get("hashrate_300s", 0),
            "shares_60s": worker_data.get("shares_60s", 0),
        }
