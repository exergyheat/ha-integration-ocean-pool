# Exergy - Public Pool

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/exergyheat/ha-integration-ocean-pool.svg)](https://github.com/exergyheat/ha-integration-ocean-pool/releases)
[![License](https://img.shields.io/github/license/exergyheat/ha-integration-ocean-pool.svg)](LICENSE)

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

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add `https://github.com/exergyheat/ha-integration-ocean-pool` as an Integration
5. Search for "Exergy - Public Pool" in HACS
6. Install the integration
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/ocean` folder to your Home Assistant `config/custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Exergy - Public Pool"
4. Enter your OCEAN username (Bitcoin address or worker identifier)
5. Optionally adjust the update interval (default: 60 seconds)

## Entities Created

### Account-Level Sensors

| Entity | Description |
|--------|-------------|
| `sensor.ocean_{username}_hashrate_60s` | Current hashrate (60s average) |
| `sensor.ocean_{username}_hashrate_300s` | Current hashrate (300s average) |
| `sensor.ocean_{username}_shares_60s` | Shares submitted in last 60s |
| `sensor.ocean_{username}_shares_300s` | Shares submitted in last 300s |
| `sensor.ocean_{username}_shares_in_tides` | Total shares in TIDES |
| `sensor.ocean_{username}_estimated_earn_next_block` | Estimated BTC earnings next block |
| `sensor.ocean_{username}_estimated_bonus_next_block` | Estimated bonus BTC next block |
| `sensor.ocean_{username}_estimated_total_earn_next_block` | Total estimated earnings |
| `sensor.ocean_{username}_estimated_payout_next_block` | Estimated payout next block |
| `sensor.ocean_{username}_unpaid_balance` | Unpaid BTC balance |
| `sensor.ocean_{username}_unpaid_usd` | Unpaid balance in USD |
| `sensor.ocean_{username}_last_share_timestamp` | When last share was submitted |
| `sensor.ocean_{username}_active_workers` | Count of active workers |

### Worker-Level Sensors

For each discovered worker:

| Entity | Description |
|--------|-------------|
| `sensor.ocean_{worker}_hashrate_60s` | Worker hashrate (60s) |
| `sensor.ocean_{worker}_hashrate_300s` | Worker hashrate (300s) |
| `sensor.ocean_{worker}_last_share` | Worker's last share timestamp |
| `sensor.ocean_{worker}_estimated_earnings` | Worker's estimated BTC earnings |
| `binary_sensor.ocean_{worker}_status` | Worker online/offline status |

## Requirements

- Home Assistant 2024.1.0 or newer
- An OCEAN Mining Pool account with active workers
- (Optional) Exchange rate sensor at `sensor.exchange_rate_1_btc` for USD conversion

## API Information

This integration uses the public OCEAN Mining Pool API:

- **Endpoint**: `https://api.ocean.xyz/v1/userinfo_full/{username}`
- **Update Interval**: Configurable (default: 60 seconds)
- **Authentication**: None required (public API)

## Troubleshooting

### No Data Showing

1. Verify your username is correct
2. Check that your workers are actively mining
3. Review Home Assistant logs for API errors

### Workers Not Appearing

- Workers are discovered dynamically on each update
- Ensure workers have submitted shares recently
- Check that worker names are valid

### USD Conversion Not Working

- Ensure you have a sensor named `sensor.exchange_rate_1_btc`
- The sensor should report the current USD value of 1 BTC

## Support

- **Issues**: [GitHub Issues](https://github.com/exergyheat/ha-integration-ocean-pool/issues)
- **Discussions**: [GitHub Discussions](https://github.com/exergyheat/ha-integration-ocean-pool/discussions)

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Credits

Created by Exergy for the Home Assistant community.
