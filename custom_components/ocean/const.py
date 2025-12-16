"""Constants for the OCEAN Mining Pool integration."""
from homeassistant.const import Platform

DOMAIN = "ocean"

# Platforms
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

# Configuration
CONF_USERNAME = "username"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 60  # seconds (matches OCEAN's 60s window)

# API URLs
API_BASE_URL = "https://api.ocean.xyz/v1"
API_STATSNAP = f"{API_BASE_URL}/statsnap/{{username}}"
API_USERINFO_FULL = f"{API_BASE_URL}/userinfo_full/{{username}}"

# Units
TERA_HASH_PER_SECOND = "TH/s"
BITCOIN = "BTC"

# Account-level sensor keys
SENSOR_HASHRATE_60S = "hashrate_60s"
SENSOR_HASHRATE_300S = "hashrate_300s"
SENSOR_SHARES_60S = "shares_60s"
SENSOR_SHARES_300S = "shares_300s"
SENSOR_SHARES_IN_TIDES = "shares_in_tides"
SENSOR_ESTIMATED_EARN_NEXT_BLOCK = "estimated_earn_next_block"
SENSOR_ESTIMATED_BONUS_NEXT_BLOCK = "estimated_bonus_next_block"
SENSOR_ESTIMATED_TOTAL_EARN_NEXT_BLOCK = "estimated_total_earn_next_block"
SENSOR_ESTIMATED_PAYOUT_NEXT_BLOCK = "estimated_payout_next_block"
SENSOR_UNPAID_BALANCE = "unpaid_balance"
SENSOR_LAST_SHARE_TIMESTAMP = "last_share_timestamp"
SENSOR_ACTIVE_WORKERS = "active_workers"

# Worker sensor keys
WORKER_HASHRATE_60S = "hashrate_60s"
WORKER_HASHRATE_300S = "hashrate_300s"
WORKER_LAST_SHARE = "last_share"
WORKER_ESTIMATED_EARN = "estimated_earn_next_block"

# Binary sensor keys
BINARY_SENSOR_WORKER_STATUS = "status"

# Exchange rate sensor entity ID
EXCHANGE_RATE_ENTITY = "sensor.exchange_rate_1_btc"
