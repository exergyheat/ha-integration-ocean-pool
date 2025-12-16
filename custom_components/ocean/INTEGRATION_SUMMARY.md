[[Home Assistant]]
# OCEAN Mining Pool Integration - Complete Summary

## 🎯 Integration Overview

**Name**: OCEAN Mining Pool  
**Domain**: `ocean`  
**Version**: 0.1.0  
**Type**: Cloud Polling  
**Update Interval**: 60 seconds (configurable)

## 📁 File Structure

```
custom_components/ocean/
├── __init__.py              # Integration setup and config entry handling
├── config_flow.py           # UI configuration flow
├── const.py                 # Constants and configuration
├── coordinator.py           # API client and data coordinator
├── sensor.py                # Account and worker sensors
├── binary_sensor.py         # Worker status binary sensors
├── manifest.json            # Integration metadata
├── strings.json             # UI strings
├── README.md                # User documentation
├── INSTALLATION.md          # Installation guide
└── translations/
    └── en.json              # English translations
```

## 🏗️ Architecture

### Data Flow
```
OCEAN API (api.ocean.xyz)
    ↓
OceanCoordinator (polls every 60s)
    ↓
Parsed Data (account + workers)
    ↓
Entities (sensors + binary_sensors)
    ↓
Home Assistant
```

### Key Components

1. **OceanAPI** (`coordinator.py`)
   - Fetches data from OCEAN's public API
   - Endpoints: `/v1/userinfo_full/{username}`
   - No authentication required

2. **OceanCoordinator** (`coordinator.py`)
   - Manages data updates
   - Converts hashrate from H/s to TH/s
   - Parses account and worker data
   - Handles API failures gracefully

3. **Sensors** (`sensor.py`)
   - Account-level: 13 sensors
   - Worker-level: 4 sensors per worker
   - USD conversion sensor (uses `sensor.exchange_rate_1_btc`)

4. **Binary Sensors** (`binary_sensor.py`)
   - 1 status sensor per worker
   - ON = shares in last 60s > 0
   - OFF = no recent shares

## 📊 Entity List

### Account Sensors (13)
| Key | Name | Unit | Type |
|-----|------|------|------|
| `hashrate_60s` | Hashrate (60s) | TH/s | Measurement |
| `hashrate_300s` | Hashrate (300s) | TH/s | Measurement |
| `shares_60s` | Shares (60s) | - | Measurement |
| `shares_300s` | Shares (300s) | - | Measurement |
| `shares_in_tides` | Shares in Tides | - | Total |
| `estimated_earn_next_block` | Est. Earnings Next Block | BTC | Measurement |
| `estimated_bonus_next_block` | Est. Bonus Next Block | BTC | Measurement |
| `estimated_total_earn_next_block` | Est. Total Earnings | BTC | Measurement |
| `estimated_payout_next_block` | Est. Payout Next Block | BTC | Measurement |
| `unpaid` | Unpaid Balance | BTC | Total |
| `unpaid_usd` | Unpaid Balance USD | $ | Total |
| `last_share_ts` | Last Share Timestamp | - | Timestamp |
| `active_workers` | Active Workers | - | Measurement |

### Worker Sensors (4 per worker)
| Key | Name | Unit | Type |
|-----|------|------|------|
| `hashrate_60s` | Hashrate (60s) | TH/s | Measurement |
| `hashrate_300s` | Hashrate (300s) | TH/s | Measurement |
| `last_share_ts` | Last Share | - | Timestamp |
| `estimated_earn_next_block` | Est. Earnings | BTC | Measurement |

### Worker Binary Sensors (1 per worker)
| Key | Name | Device Class |
|-----|------|--------------|
| `status` | Status | Connectivity |

## 🔧 Configuration

### Via UI (Recommended)
1. Settings → Devices & Services
2. Add Integration → "OCEAN Mining Pool"
3. Enter username and scan interval

### Config Entry Data
```python
{
    "username": "bc1qcnpuc5scg0n4hpwpvalntmg6n0c0349x9jfgcj",
    "scan_interval": 60
}
```

## 🚀 Features

### ✅ Implemented
- [x] Account-level monitoring
- [x] Per-worker monitoring
- [x] Dynamic worker discovery
- [x] USD conversion (via exchange rate sensor)
- [x] UI configuration flow
- [x] Proper device grouping
- [x] Timestamp sensors
- [x] Binary status sensors
- [x] Entity attributes (additional worker data)

### 🎯 Design Decisions

1. **Single Device Per Account**
   - All entities grouped under one device
   - Easy to manage and visualize
   - Clean organization

2. **Dynamic Worker Creation**
   - Workers added/removed automatically
   - No manual configuration needed
   - Updates on each coordinator refresh

3. **Hashrate in TH/s**
   - API returns H/s (hash per second)
   - Converted to TH/s for readability
   - Calculation: `api_value / 1_000_000_000_000`

4. **Worker Names Preserved**
   - Underscores kept in entity IDs
   - Matches your naming convention
   - Examples: `S19kPro001`, `Living_Room_Mini3`

5. **60s Update Interval**
   - Matches OCEAN's 60s stat window
   - Balances freshness vs. API load
   - Configurable by user

## 📦 Dependencies

- Home Assistant 2023.1+
- `aiohttp` (included in HA)
- `voluptuous` (included in HA)

## 🧪 Testing Checklist

### Initial Setup
- [ ] Integration appears in UI
- [ ] Username validation works
- [ ] Invalid username shows error
- [ ] Config entry created successfully

### Entity Creation
- [ ] 13 account sensors created
- [ ] Worker sensors created for active workers
- [ ] Binary sensors created for workers
- [ ] USD sensor created (if exchange rate available)

### Data Updates
- [ ] Coordinator fetches data every 60s
- [ ] Hashrates update correctly
- [ ] Worker status reflects activity
- [ ] Timestamps convert properly

### Edge Cases
- [ ] Offline workers handled gracefully
- [ ] New workers discovered automatically
- [ ] Missing exchange rate handled
- [ ] API failures don't crash integration

## 🐛 Known Issues

None currently! This is a fresh build.

## 🔮 Future Enhancements

### Potential Features
- [ ] Historical data tracking
- [ ] Earnings predictions
- [ ] Worker efficiency metrics
- [ ] Pool statistics (global hashrate, difficulty)
- [ ] Payout history integration
- [ ] Notifications for worker offline events
- [ ] Dashboard card template

### API Limitations
- Public API only (no write operations)
- No payout history endpoint
- Worker data limited to current stats

## 📝 Example Usage

### Dashboard Card
```yaml
type: entities
title: OCEAN Mining
entities:
  - entity: sensor.ocean_bc1q_hashrate_60s
    name: Total Hashrate
  - entity: sensor.ocean_bc1q_active_workers
    name: Active Workers
  - entity: sensor.ocean_bc1q_unpaid_usd
    name: Unpaid Balance
```

### Automation: Worker Offline Alert
```yaml
automation:
  - alias: "Alert: OCEAN Worker Offline"
    trigger:
      - platform: state
        entity_id: binary_sensor.ocean_s19kpro001_status
        to: 'off'
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          title: "Mining Worker Offline"
          message: "S19kPro001 has been offline for 5 minutes"
```

### Template Sensor: Daily Earnings Estimate
```yaml
sensor:
  - platform: template
    sensors:
      ocean_daily_earnings:
        friendly_name: "Estimated Daily Earnings"
        unit_of_measurement: "BTC"
        value_template: >
          {{ (states('sensor.ocean_bc1q_estimated_total_earn_next_block') | float * 144) | round(8) }}
```

## 🎓 Learning Resources

### API Documentation
- Base URL: `https://api.ocean.xyz/v1`
- Endpoints:
  - `/statsnap/{username}` - Account snapshot
  - `/userinfo_full/{username}` - Full user info with workers

### Example API Response
```json
{
  "result": {
    "snap_ts": "1764884940",
    "workers": [
      {
        "S19kPro001": {
          "hashrate_60s": "225179981368525",
          "shares_60s": "3145728",
          "is_active": true
        }
      }
    ],
    "user_full": {
      "hashrate_60s": "356534970500164",
      "unpaid": "0.00003992"
    }
  }
}
```

## 👨‍💻 Developer Notes

### Code Style
- Follows Home Assistant conventions
- Type hints throughout
- Proper error handling
- Comprehensive logging

### Testing Commands
```bash
# Check for import errors
python3 -m py_compile custom_components/ocean/*.py

# Validate manifest
cat custom_components/ocean/manifest.json | jq

# Check translations
cat custom_components/ocean/translations/en.json | jq
```

### Debugging
```yaml
# Add to configuration.yaml
logger:
  default: warning
  logs:
    custom_components.ocean: debug
```

## 📞 Support

For issues or questions:
1. Check Home Assistant logs
2. Verify API is accessible
3. Test with curl: `curl https://api.ocean.xyz/v1/userinfo_full/YOUR_USERNAME`
4. Review entity states in Developer Tools

## ✨ Summary

This integration provides **comprehensive monitoring** of your OCEAN mining account with:
- Real-time hashrate tracking
- Per-worker visibility
- Earnings estimates
- Automatic worker discovery
- Clean UI configuration
- USD value conversion

Perfect for monitoring Bitcoin mining operations through Home Assistant! 🎉
