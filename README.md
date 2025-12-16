[[Home Assistant]]
# OCEAN Mining Pool Integration for Home Assistant

Monitor your OCEAN Mining Pool account and workers directly in Home Assistant.

## Features

- **Account-Level Monitoring**:
  - Hashrate (60s and 300s averages) in TH/s
  - Share counts (60s, 300s, and total in tides)
  - Estimated earnings per block (BTC and USD)
  - Unpaid balance (BTC and USD)
  - Last share timestamp
  - Active worker count

- **Per-Worker Monitoring**:
  - Individual worker hashrate (60s and 300s)
  - Worker online/offline status
  - Last share timestamp per worker
  - Estimated earnings per worker

- **Dynamic Worker Detection**: Automatically discovers and creates entities for new workers
- **USD Conversion**: Converts BTC values to USD using your existing exchange rate sensor

## Installation

### HACS (Recommended)
1. Add this repository as a custom repository in HACS
2. Search for "OCEAN Mining Pool" in HACS
3. Install the integration
4. Restart Home Assistant

### Manual Installation
1. Copy the `ocean` folder to your `custom_components` directory
2. Restart Home Assistant

## Configuration

### UI Configuration (Recommended)
1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "OCEAN Mining Pool"
4. Enter your OCEAN username (Bitcoin address or worker identifier)
5. Optionally adjust the update interval (default: 60 seconds)

### Example
- **Username**: `bc1qcnpuc5scg0n4hpwpvalntmg6n0c0349x9jfgcj`
- **Update Interval**: `60` seconds

## Entities Created

### Account-Level Sensors
- `sensor.ocean_{username}_hashrate_60s` - Current hashrate (60s average)
- `sensor.ocean_{username}_hashrate_300s` - Current hashrate (300s average)
- `sensor.ocean_{username}_shares_60s` - Shares submitted in last 60s
- `sensor.ocean_{username}_shares_300s` - Shares submitted in last 300s
- `sensor.ocean_{username}_shares_in_tides` - Total shares in TIDES
- `sensor.ocean_{username}_estimated_earn_next_block` - Estimated BTC earnings next block
- `sensor.ocean_{username}_estimated_bonus_next_block` - Estimated bonus BTC next block
- `sensor.ocean_{username}_estimated_total_earn_next_block` - Total estimated earnings
- `sensor.ocean_{username}_estimated_payout_next_block` - Estimated payout next block
- `sensor.ocean_{username}_unpaid_balance` - Unpaid BTC balance
- `sensor.ocean_{username}_unpaid_usd` - Unpaid balance in USD
- `sensor.ocean_{username}_last_share_timestamp` - When last share was submitted
- `sensor.ocean_{username}_active_workers` - Count of active workers

### Worker-Level Sensors (dynamically created for each worker)
- `sensor.ocean_{worker_name}_hashrate_60s` - Worker hashrate (60s)
- `sensor.ocean_{worker_name}_hashrate_300s` - Worker hashrate (300s)
- `sensor.ocean_{worker_name}_last_share` - Worker's last share timestamp
- `sensor.ocean_{worker_name}_estimated_earnings` - Worker's estimated BTC earnings
- `binary_sensor.ocean_{worker_name}_status` - Worker online/offline status

## Requirements

- Home Assistant 2023.1 or newer
- An OCEAN Mining Pool account with active workers
- Exchange rate sensor at `sensor.exchange_rate_1_btc` for USD conversion

## API Information

This integration uses the public OCEAN Mining Pool API:
- **Endpoint**: `https://api.ocean.xyz/v1/userinfo_full/{username}`
- **Update Interval**: 60 seconds (configurable)
- **Authentication**: None required (public API)

## Device Structure

All entities are grouped under a single device:
- **Device Name**: `OCEAN Mining Account ({username})`
- **Manufacturer**: OCEAN Mining Pool
- **Model**: Mining Account

This allows easy organization and management of all OCEAN-related sensors.

## Multiple Accounts

You can add multiple OCEAN accounts by adding the integration multiple times with different usernames. Each account will create its own device with separate entities.

## Troubleshooting

### No Data Showing
1. Verify your username is correct
2. Check that your workers are actively mining
3. Review Home Assistant logs for API errors

### Workers Not Appearing
- Workers are discovered dynamically on each update
- Ensure workers have submitted shares recently (within API reporting window)
- Check that worker names are valid

### USD Conversion Not Working
- Ensure you have a sensor named `sensor.exchange_rate_1_btc`
- The sensor should report the current USD value of 1 BTC
- Check that the exchange rate sensor is available and has a valid numeric state

## Example Lovelace Card

```yaml
type: entities
title: OCEAN Mining Pool
entities:
  - entity: sensor.ocean_bc1q_hashrate_60s
    name: Current Hashrate
  - entity: sensor.ocean_bc1q_active_workers
    name: Active Workers
  - entity: sensor.ocean_bc1q_unpaid_usd
    name: Unpaid Balance (USD)
  - entity: sensor.ocean_bc1q_estimated_total_earn_next_block
    name: Est. Earnings Next Block
  - type: divider
  - entity: binary_sensor.ocean_s19kpro001_status
    name: S19k Pro Status
  - entity: sensor.ocean_s19kpro001_hashrate_60s
    name: S19k Pro Hashrate
  - entity: binary_sensor.ocean_living_room_mini3_status
    name: Living Room Heater Status
  - entity: sensor.ocean_living_room_mini3_hashrate_60s
    name: Living Room Heater Hashrate
```

## Support

For issues, feature requests, or questions:
- GitHub Issues: [Your Repository URL]
- Home Assistant Community: [Forum Thread URL]

## License

MIT License - See LICENSE file for details

## Credits

Created by Dylan for the Home Assistant community.
