"""OCEAN Mining Pool DataUpdateCoordinator."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    API_STATSNAP,
    API_USERINFO_FULL,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_DATA = {
    "username": None,
    "snap_ts": None,
    "hashrate_60s": 0,
    "hashrate_300s": 0,
    "shares_60s": 0,
    "shares_300s": 0,
    "shares_in_tides": 0,
    "estimated_earn_next_block": 0.0,
    "estimated_bonus_next_block": 0.0,
    "estimated_total_earn_next_block": 0.0,
    "estimated_payout_next_block": 0.0,
    "unpaid": 0.0,
    "last_share_ts": None,
    "active_workers": 0,
    "workers": {},
}


class OceanAPI:
    """API client for OCEAN Mining Pool."""

    def __init__(self, username: str, session: aiohttp.ClientSession):
        """Initialize API."""
        self.username = username
        self.session = session

    async def fetch_statsnap(self) -> dict[str, Any] | None:
        """Fetch account stats snapshot."""
        url = API_STATSNAP.format(username=self.username)
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    _LOGGER.error(f"HTTP {response.status} from {url}")
                    return None
                data = await response.json()
                return data.get("result")
        except asyncio.TimeoutError:
            _LOGGER.error(f"Timeout fetching {url}")
            return None
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Client error fetching {url}: {err}")
            return None
        except Exception as err:
            _LOGGER.exception(f"Unexpected error fetching {url}: {err}")
            return None

    async def fetch_userinfo_full(self) -> dict[str, Any] | None:
        """Fetch full user info including workers."""
        url = API_USERINFO_FULL.format(username=self.username)
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    _LOGGER.error(f"HTTP {response.status} from {url}")
                    return None
                data = await response.json()
                return data.get("result")
        except asyncio.TimeoutError:
            _LOGGER.error(f"Timeout fetching {url}")
            return None
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Client error fetching {url}: {err}")
            return None
        except Exception as err:
            _LOGGER.exception(f"Unexpected error fetching {url}: {err}")
            return None


class OceanCoordinator(DataUpdateCoordinator):
    """Class to manage fetching OCEAN Mining Pool data."""

    def __init__(
        self,
        hass: HomeAssistant,
        username: str,
        scan_interval: int,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize coordinator."""
        self.username = username
        self.api = OceanAPI(username, session)
        self._failure_count = 0
        
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=f"OCEAN {username}",
            update_interval=timedelta(seconds=scan_interval),
        )

    def _parse_account_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse account-level stats from statsnap or userinfo_full."""
        result = {}
        
        if not data:
            return result
        
        result["snap_ts"] = data.get("snap_ts")
        result["shares_60s"] = int(data.get("shares_60s", 0))
        result["shares_300s"] = int(data.get("shares_300s", 0))
        
        # Convert hashrate to TH/s (API returns H/s)
        result["hashrate_60s"] = float(data.get("hashrate_60s", 0)) / 1_000_000_000_000
        result["hashrate_300s"] = float(data.get("hashrate_300s", 0)) / 1_000_000_000_000
        
        result["last_share_ts"] = data.get("lastest_share_ts")
        result["shares_in_tides"] = int(data.get("shares_in_tides", 0))
        result["estimated_earn_next_block"] = float(data.get("estimated_earn_next_block", 0))
        result["estimated_bonus_next_block"] = float(data.get("estimated_bonus_earn_next_block", 0))
        result["estimated_total_earn_next_block"] = float(data.get("estimated_total_earn_next_block", 0))
        result["estimated_payout_next_block"] = float(data.get("estimated_payout_next_block", 0))
        result["unpaid"] = float(data.get("unpaid", 0))
        
        return result

    def _parse_workers(self, workers_list: list) -> dict[str, dict[str, Any]]:
        """Parse worker data from userinfo_full."""
        workers = {}
        
        if not workers_list:
            return workers
        
        for worker_dict in workers_list:
            # Each worker is a dict with one key (worker name) and value (worker data)
            for worker_name, worker_data in worker_dict.items():
                # Convert hashrate to TH/s
                hashrate_60s = float(worker_data.get("hashrate_60s", 0)) / 1_000_000_000_000
                hashrate_300s = float(worker_data.get("hashrate_300s", 0)) / 1_000_000_000_000
                
                workers[worker_name] = {
                    "hashrate_60s": hashrate_60s,
                    "hashrate_300s": hashrate_300s,
                    "shares_60s": int(worker_data.get("shares_60s", 0)),
                    "shares_300s": int(worker_data.get("shares_300s", 0)),
                    "last_share_ts": worker_data.get("lastest_share_ts"),
                    "shares_in_tides": int(worker_data.get("shares_in_tides", 0)),
                    "estimated_earn_next_block": float(worker_data.get("estimated_earn_next_block", 0)),
                    "estimated_bonus_next_block": float(worker_data.get("estimated_bonus_earn_next_block", 0)),
                    "estimated_total_earn_next_block": float(worker_data.get("estimated_total_earn_next_block", 0)),
                    "is_active": int(worker_data.get("shares_60s", 0)) > 0,
                }
        
        return workers

    async def _async_update_data(self):
        """Fetch data from OCEAN API."""
        try:
            _LOGGER.debug(f"Fetching data for OCEAN user {self.username}")
            
            # Fetch userinfo_full (includes everything we need)
            userinfo = await self.api.fetch_userinfo_full()
            
            if not userinfo:
                self._failure_count += 1
                
                if self._failure_count == 1:
                    _LOGGER.warning(f"OCEAN API returned no data for {self.username}")
                    return DEFAULT_DATA.copy()
                
                raise UpdateFailed(f"OCEAN API failed for {self.username}")
            
            # Parse data
            data = DEFAULT_DATA.copy()
            data["username"] = self.username
            
            # Get account-level data from user_full section
            if "user_full" in userinfo:
                data.update(self._parse_account_data(userinfo["user_full"]))
            
            # Parse workers
            if "workers" in userinfo:
                data["workers"] = self._parse_workers(userinfo["workers"])
                # Count active workers
                data["active_workers"] = sum(1 for w in data["workers"].values() if w["is_active"])
            
            # Reset failure count on success
            self._failure_count = 0
            
            _LOGGER.debug(
                f"Got data from OCEAN for {self.username}: "
                f"hashrate_60s={data.get('hashrate_60s', 0):.2f} TH/s, "
                f"hashrate_300s={data.get('hashrate_300s', 0):.2f} TH/s, "
                f"unpaid={data.get('unpaid', 0):.8f} BTC, "
                f"workers={len(data.get('workers', {}))}, "
                f"active={data.get('active_workers', 0)}"
            )
            
            return data
            
        except Exception as err:
            self._failure_count += 1
            
            if self._failure_count == 1:
                _LOGGER.warning(f"Error fetching data from OCEAN for {self.username}: {err}")
                return DEFAULT_DATA.copy()
            
            _LOGGER.exception(f"Failed to fetch data from OCEAN for {self.username}")
            raise UpdateFailed(f"Error communicating with OCEAN API: {err}")

    @property
    def available(self) -> bool:
        """Return if OCEAN API is available."""
        return self._failure_count < 2
