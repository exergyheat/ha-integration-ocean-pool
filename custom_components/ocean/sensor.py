"""Support for OCEAN Mining Pool sensors."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_DOLLAR, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    BITCOIN,
    DOMAIN,
    EXCHANGE_RATE_ENTITY,
    TERA_HASH_PER_SECOND,
)

_LOGGER = logging.getLogger(__name__)

# Account-level sensor descriptions
ACCOUNT_SENSOR_TYPES: dict[str, SensorEntityDescription] = {
    "hashrate_60s": SensorEntityDescription(
        key="hashrate_60s",
        name="Hashrate (60s)",
        native_unit_of_measurement=TERA_HASH_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
    ),
    "hashrate_300s": SensorEntityDescription(
        key="hashrate_300s",
        name="Hashrate (300s)",
        native_unit_of_measurement=TERA_HASH_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
    ),
    "shares_60s": SensorEntityDescription(
        key="shares_60s",
        name="Shares (60s)",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
    ),
    "shares_300s": SensorEntityDescription(
        key="shares_300s",
        name="Shares (300s)",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
    ),
    "shares_in_tides": SensorEntityDescription(
        key="shares_in_tides",
        name="Shares in Tides",
        state_class=SensorStateClass.TOTAL,
        icon="mdi:counter",
    ),
    "estimated_earn_next_block": SensorEntityDescription(
        key="estimated_earn_next_block",
        name="Estimated Earnings Next Block",
        native_unit_of_measurement=BITCOIN,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bitcoin",
        suggested_display_precision=8,
    ),
    "estimated_bonus_next_block": SensorEntityDescription(
        key="estimated_bonus_next_block",
        name="Estimated Bonus Next Block",
        native_unit_of_measurement=BITCOIN,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bitcoin",
        suggested_display_precision=8,
    ),
    "estimated_total_earn_next_block": SensorEntityDescription(
        key="estimated_total_earn_next_block",
        name="Estimated Total Earnings Next Block",
        native_unit_of_measurement=BITCOIN,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bitcoin",
        suggested_display_precision=8,
    ),
    "estimated_payout_next_block": SensorEntityDescription(
        key="estimated_payout_next_block",
        name="Estimated Payout Next Block",
        native_unit_of_measurement=BITCOIN,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cash",
        suggested_display_precision=8,
    ),
    "unpaid": SensorEntityDescription(
        key="unpaid",
        name="Unpaid Balance",
        native_unit_of_measurement=BITCOIN,
        state_class=SensorStateClass.TOTAL,
        device_class=SensorDeviceClass.MONETARY,
        icon="mdi:wallet",
        suggested_display_precision=8,
    ),
    "last_share_ts": SensorEntityDescription(
        key="last_share_ts",
        name="Last Share Timestamp",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock",
    ),
    "active_workers": SensorEntityDescription(
        key="active_workers",
        name="Active Workers",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:laptop",
    ),
}

# Worker sensor descriptions
WORKER_SENSOR_TYPES: dict[str, SensorEntityDescription] = {
    "hashrate_60s": SensorEntityDescription(
        key="hashrate_60s",
        name="Hashrate (60s)",
        native_unit_of_measurement=TERA_HASH_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
    ),
    "hashrate_300s": SensorEntityDescription(
        key="hashrate_300s",
        name="Hashrate (300s)",
        native_unit_of_measurement=TERA_HASH_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
    ),
    "last_share_ts": SensorEntityDescription(
        key="last_share_ts",
        name="Last Share",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock",
    ),
    "estimated_earn_next_block": SensorEntityDescription(
        key="estimated_earn_next_block",
        name="Estimated Earnings Next Block",
        native_unit_of_measurement=BITCOIN,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bitcoin",
        suggested_display_precision=8,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OCEAN Mining Pool sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # Add account-level sensors
    for sensor_key, description in ACCOUNT_SENSOR_TYPES.items():
        entities.append(
            OceanAccountSensor(
                coordinator=coordinator,
                description=description,
                sensor_key=sensor_key,
            )
        )
    
    # Add USD value sensor for unpaid balance
    entities.append(
        OceanUnpaidUSDSensor(
            coordinator=coordinator,
        )
    )
    
    # Add lifetime earnings scrape sensor for main account
    entities.append(
        OceanAccountLifetimeEarningsSensor(
            hass=hass,
            username=coordinator.username,
            scan_interval=coordinator.update_interval,
        )
    )
    
    # Add worker sensors dynamically
    workers = coordinator.data.get("workers", {})
    for worker_name in workers:
        for sensor_key, description in WORKER_SENSOR_TYPES.items():
            entities.append(
                OceanWorkerSensor(
                    coordinator=coordinator,
                    description=description,
                    sensor_key=sensor_key,
                    worker_name=worker_name,
                )
            )
        
        # Add lifetime earnings scrape sensor for each worker
        entities.append(
            OceanWorkerLifetimeEarningsSensor(
                hass=hass,
                username=coordinator.username,
                worker_name=worker_name,
                scan_interval=coordinator.update_interval,
            )
        )
    
    async_add_entities(entities)
    
    # Listen for coordinator updates to add new workers
    @callback
    def _async_add_new_workers():
        """Add sensors for newly discovered workers."""
        new_entities = []
        current_workers = coordinator.data.get("workers", {})
        
        # Find workers that don't have entities yet
        existing_workers = {
            entity.worker_name
            for entity in entities
            if isinstance(entity, OceanWorkerSensor)
        }
        
        new_workers = set(current_workers.keys()) - existing_workers
        
        for worker_name in new_workers:
            for sensor_key, description in WORKER_SENSOR_TYPES.items():
                new_entity = OceanWorkerSensor(
                    coordinator=coordinator,
                    description=description,
                    sensor_key=sensor_key,
                    worker_name=worker_name,
                )
                new_entities.append(new_entity)
                entities.append(new_entity)
            
            # Add lifetime earnings scrape sensor for new worker
            lifetime_entity = OceanWorkerLifetimeEarningsSensor(
                hass=hass,
                username=coordinator.username,
                worker_name=worker_name,
                scan_interval=coordinator.update_interval,
            )
            new_entities.append(lifetime_entity)
            entities.append(lifetime_entity)
        
        if new_entities:
            _LOGGER.info(f"Adding {len(new_entities)} sensors for new workers")
            async_add_entities(new_entities)
    
    # Subscribe to coordinator updates
    entry.async_on_unload(
        coordinator.async_add_listener(_async_add_new_workers)
    )


class OceanAccountSensor(CoordinatorEntity, SensorEntity):
    """Representation of an OCEAN account-level sensor."""

    def __init__(
        self,
        coordinator,
        description: SensorEntityDescription,
        sensor_key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._sensor_key = sensor_key
        self._attr_unique_id = f"{coordinator.username}_{sensor_key}"
        # Remove address from entity names - just use description
        self._attr_name = f"Mining Account {description.name}"

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return device info."""
        return entity.DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.username)},
            name="Mining Account",
            manufacturer="OCEAN Mining Pool",
            model="Mining Account",
            configuration_url="https://ocean.xyz",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._sensor_key)
        
        # Convert timestamp to datetime if this is a timestamp sensor
        if self._sensor_key == "last_share_ts" and value:
            try:
                # Handle both string and int timestamps
                timestamp = int(value) if isinstance(value, str) else value
                if timestamp and timestamp > 0:
                    # Return timezone-aware datetime (UTC)
                    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            except (ValueError, TypeError) as err:
                _LOGGER.debug(f"Error converting account timestamp: {value} - {err}")
                return None
        
        return value

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.available and self.coordinator.last_update_success


class OceanUnpaidUSDSensor(CoordinatorEntity, SensorEntity):
    """Sensor for unpaid balance in USD."""

    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.username}_unpaid_usd"
        # Remove address from entity names
        self._attr_name = "Mining Account Unpaid Balance USD"
        self._attr_native_unit_of_measurement = CURRENCY_DOLLAR
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_icon = "mdi:currency-usd"
        self._attr_suggested_display_precision = 2

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return device info."""
        return entity.DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.username)},
            name="Mining Account",
            manufacturer="OCEAN Mining Pool",
            model="Mining Account",
            configuration_url="https://ocean.xyz",
        )

    @property
    def native_value(self):
        """Return the state of the sensor in USD."""
        unpaid_btc = self.coordinator.data.get("unpaid", 0)
        
        # Get exchange rate from sensor
        exchange_rate_state = self.hass.states.get(EXCHANGE_RATE_ENTITY)
        if not exchange_rate_state:
            _LOGGER.warning(f"Exchange rate sensor {EXCHANGE_RATE_ENTITY} not found")
            return None
        
        try:
            exchange_rate = float(exchange_rate_state.state)
            return unpaid_btc * exchange_rate
        except (ValueError, TypeError):
            _LOGGER.error(f"Invalid exchange rate: {exchange_rate_state.state}")
            return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.available
            and self.coordinator.last_update_success
            and self.hass.states.get(EXCHANGE_RATE_ENTITY) is not None
        )


class OceanAccountLifetimeEarningsSensor(SensorEntity):
    """Sensor for account lifetime earnings scraped from OCEAN website."""

    def __init__(
        self,
        hass: HomeAssistant,
        username: str,
        scan_interval: timedelta,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._username = username
        
        self._attr_unique_id = f"{username}_lifetime_earnings"
        self._attr_name = "Mining Account Lifetime Earnings"
        self._attr_native_unit_of_measurement = BITCOIN
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:bitcoin"
        self._attr_suggested_display_precision = 8
        self._attr_native_value = None
        
        # Create a dedicated coordinator for scraping - uses same interval as API
        self._coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"OCEAN Account Lifetime Earnings",
            update_method=self._async_update_data,
            update_interval=scan_interval,
        )

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return device info - belongs to main account device."""
        return entity.DeviceInfo(
            identifiers={(DOMAIN, self._username)},
            name="Mining Account",
            manufacturer="OCEAN Mining Pool",
            model="Mining Account",
            configuration_url="https://ocean.xyz",
        )

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        await self._coordinator.async_refresh()

    async def async_update(self) -> None:
        """Update the sensor."""
        await self._coordinator.async_request_refresh()
        if self._coordinator.data is not None:
            self._attr_native_value = self._coordinator.data

    async def _async_update_data(self) -> float | None:
        """Fetch lifetime earnings from OCEAN website."""
        url = f"https://ocean.xyz/stats/{self._username}"
        
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status != 200:
                    _LOGGER.warning(f"HTTP {response.status} from {url}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the Lifetime Earnings label and get the next span
                labels = soup.find_all('div', class_='blocks-label')
                for label in labels:
                    if 'Lifetime Earnings' in label.get_text():
                        # Get the sibling span that contains the value
                        value_span = label.find_next_sibling('span')
                        if value_span:
                            value_text = value_span.get_text()
                            # Clean the value: remove ' BTC', commas, newlines, and whitespace
                            clean_value = value_text.replace(' BTC', '').replace(',', '').replace('\n', '').strip()
                            try:
                                return float(clean_value)
                            except ValueError:
                                _LOGGER.warning(f"Could not parse account lifetime earnings value: {clean_value}")
                                return None
                
                _LOGGER.warning(f"Could not find Lifetime Earnings on account page: {url}")
                return None
                
        except Exception as err:
            _LOGGER.error(f"Error fetching account lifetime earnings: {err}")
            return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.last_update_success


class OceanWorkerSensor(CoordinatorEntity, SensorEntity):
    """Representation of an OCEAN worker sensor."""

    def __init__(
        self,
        coordinator,
        description: SensorEntityDescription,
        sensor_key: str,
        worker_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._sensor_key = sensor_key
        self.worker_name = worker_name
        
        # Sanitize worker name for entity ID (keep underscores)
        safe_worker_name = worker_name.replace(" ", "_").replace("-", "_")
        
        self._attr_unique_id = f"{coordinator.username}_{safe_worker_name}_{sensor_key}"
        # Remove "OCEAN" prefix from entity names
        self._attr_name = f"{worker_name} {description.name}"

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
    def native_value(self):
        """Return the state of the sensor."""
        workers = self.coordinator.data.get("workers", {})
        worker_data = workers.get(self.worker_name)
        
        if not worker_data:
            return None
        
        value = worker_data.get(self._sensor_key)
        
        # Convert timestamp to datetime if this is a timestamp sensor
        if self._sensor_key == "last_share_ts" and value:
            try:
                # Handle both string and int timestamps
                timestamp = int(value) if isinstance(value, str) else value
                if timestamp and timestamp > 0:
                    # Return timezone-aware datetime (UTC)
                    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            except (ValueError, TypeError) as err:
                _LOGGER.debug(f"Error converting timestamp for {self.worker_name}: {value} - {err}")
                return None
        
        return value

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.available or not self.coordinator.last_update_success:
            return False
        
        # Worker is available if it exists in the data
        workers = self.coordinator.data.get("workers", {})
        return self.worker_name in workers

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        workers = self.coordinator.data.get("workers", {})
        worker_data = workers.get(self.worker_name, {})
        
        return {
            "shares_60s": worker_data.get("shares_60s", 0),
            "shares_300s": worker_data.get("shares_300s", 0),
            "shares_in_tides": worker_data.get("shares_in_tides", 0),
            "is_active": worker_data.get("is_active", False),
        }


class OceanWorkerLifetimeEarningsSensor(SensorEntity):
    """Sensor for worker lifetime earnings scraped from OCEAN website."""

    def __init__(
        self,
        hass: HomeAssistant,
        username: str,
        worker_name: str,
        scan_interval: timedelta,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._username = username
        self.worker_name = worker_name
        
        # Sanitize worker name for entity ID
        safe_worker_name = worker_name.replace(" ", "_").replace("-", "_")
        
        self._attr_unique_id = f"{username}_{safe_worker_name}_lifetime_earnings"
        self._attr_name = f"{worker_name} Lifetime Earnings"
        self._attr_native_unit_of_measurement = BITCOIN
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:bitcoin"
        self._attr_suggested_display_precision = 8
        self._attr_native_value = None
        
        # Create a dedicated coordinator for scraping - uses same interval as API
        self._coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"OCEAN Lifetime Earnings {worker_name}",
            update_method=self._async_update_data,
            update_interval=scan_interval,
        )

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return device info - each worker is its own device."""
        return entity.DeviceInfo(
            identifiers={(DOMAIN, f"{self._username}_{self.worker_name}")},
            name=f"{self.worker_name}",
            manufacturer="OCEAN Mining Pool",
            model="Worker",
            configuration_url="https://ocean.xyz",
            via_device=(DOMAIN, self._username),
        )

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        await self._coordinator.async_refresh()

    async def async_update(self) -> None:
        """Update the sensor."""
        await self._coordinator.async_request_refresh()
        if self._coordinator.data is not None:
            self._attr_native_value = self._coordinator.data

    async def _async_update_data(self) -> float | None:
        """Fetch lifetime earnings from OCEAN website."""
        url = f"https://ocean.xyz/stats/{self._username}.{self.worker_name}"
        
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status != 200:
                    _LOGGER.warning(f"HTTP {response.status} from {url}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the Lifetime Earnings label and get the next span
                labels = soup.find_all('div', class_='blocks-label')
                for label in labels:
                    if 'Lifetime Earnings' in label.get_text():
                        # Get the sibling span that contains the value
                        value_span = label.find_next_sibling('span')
                        if value_span:
                            value_text = value_span.get_text()
                            # Clean the value: remove ' BTC', commas, newlines, and whitespace
                            clean_value = value_text.replace(' BTC', '').replace(',', '').replace('\n', '').strip()
                            try:
                                return float(clean_value)
                            except ValueError:
                                _LOGGER.warning(f"Could not parse lifetime earnings value: {clean_value}")
                                return None
                
                _LOGGER.warning(f"Could not find Lifetime Earnings on page: {url}")
                return None
                
        except Exception as err:
            _LOGGER.error(f"Error fetching lifetime earnings for {self.worker_name}: {err}")
            return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.last_update_success
