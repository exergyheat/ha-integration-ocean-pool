# OCEAN Integration - Final Updates

## Summary of Changes

This update completes the OCEAN integration improvements by fixing entity naming and adding lifetime earnings tracking for each worker.

---

## Changes Made

### 1. ✅ Fixed "Estimated Earnings" Name

**Before:**
- `sensor.q_estimated_earnings`

**After:**
- `sensor.q_estimated_earnings_next_block`

**Full entity name:** `Q Estimated Earnings Next Block`

**File Modified:** `sensor.py` line 143

---

### 2. ✅ Added Lifetime Earnings for Each Worker

Each worker now has a **Lifetime Earnings** sensor that scrapes the value from the OCEAN website.

**New Entities Created:**
- `sensor.q_lifetime_earnings`
- `sensor.frankenmini3_lifetime_earnings`
- `sensor.upstairs_conference_room_lifetime_earnings`
- `sensor.exergy_radiant_floor_lifetime_earnings`
- `sensor.hb_trio_lifetime_earnings`

**Display Names:**
- `Q Lifetime Earnings`
- `FrankenMini3 Lifetime Earnings`
- `Upstairs_Conference_Room Lifetime Earnings`
- etc.

**Sensor Details:**
- **Unit:** BTC
- **State Class:** `total_increasing`
- **Update Interval:** 300 seconds (5 minutes)
- **Icon:** `mdi:bitcoin`
- **Precision:** 8 decimal places
- **Source:** Web scraping from `https://ocean.xyz/stats/{username}.{worker_name}`

---

## How It Works

### Lifetime Earnings Scraping

The integration creates a dedicated sensor for each worker that:

1. **Fetches the worker's OCEAN stats page:**
   ```
   https://ocean.xyz/stats/bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv.Q
   ```

2. **Parses the HTML using BeautifulSoup** to find:
   ```html
   <div class="blocks-label">Lifetime Earnings</div>
   <span>0.12345678 BTC</span>
   ```

3. **Cleans the value** by removing:
   - " BTC" suffix
   - Commas
   - Newlines
   - Whitespace

4. **Updates every 5 minutes** to avoid overloading the OCEAN website

5. **Handles errors gracefully:**
   - Logs warnings if the page structure changes
   - Returns `None` if parsing fails
   - Marks sensor as unavailable on repeated failures

---

## Device Structure (Final)

```
📱 Mining Account
   ├─ Mining Account Hashrate (60s)
   ├─ Mining Account Hashrate (300s)
   ├─ Mining Account Active Workers
   ├─ Mining Account Unpaid Balance
   ├─ Mining Account Unpaid Balance USD
   ├─ Mining Account Shares (60s)
   ├─ Mining Account Shares (300s)
   ├─ Mining Account Shares in Tides
   ├─ Mining Account Estimated Earnings Next Block
   ├─ Mining Account Estimated Bonus Next Block
   ├─ Mining Account Estimated Total Earnings Next Block
   ├─ Mining Account Estimated Payout Next Block
   └─ Mining Account Last Share Timestamp

📱 Q (Worker - linked to Mining Account)
   ├─ Q Hashrate (60s)
   ├─ Q Hashrate (300s)
   ├─ Q Estimated Earnings Next Block
   ├─ Q Last Share
   ├─ Q Lifetime Earnings ⭐ NEW
   └─ Q Status

📱 FrankenMini3 (Worker - linked to Mining Account)
   ├─ FrankenMini3 Hashrate (60s)
   ├─ FrankenMini3 Hashrate (300s)
   ├─ FrankenMini3 Estimated Earnings Next Block
   ├─ FrankenMini3 Last Share
   ├─ FrankenMini3 Lifetime Earnings ⭐ NEW
   └─ FrankenMini3 Status

📱 Upstairs_Conference_Room (Worker)
   └─ ... (same sensors)

📱 Exergy_Radiant_Floor (Worker)
   └─ ... (same sensors)

📱 hb-trio (Worker)
   └─ ... (same sensors)
```

---

## Files Modified

### `sensor.py`
1. **Line 3-11:** Added imports for `timedelta`, `re`, `aiohttp`, `BeautifulSoup`
2. **Line 21-24:** Added imports for `async_get_clientsession`, `DataUpdateCoordinator`, `UpdateFailed`
3. **Line 143:** Changed "Estimated Earnings" → "Estimated Earnings Next Block"
4. **Lines 193-202:** Added `OceanWorkerLifetimeEarningsSensor` instantiation for each worker
5. **Lines 229-237:** Added lifetime earnings sensor for newly discovered workers
6. **Lines 439-550:** Added new `OceanWorkerLifetimeEarningsSensor` class with web scraping logic

### `manifest.json`
- **Line 9:** Added `beautifulsoup4==4.12.2` to requirements

---

## Code Architecture

### New Class: `OceanWorkerLifetimeEarningsSensor`

**Purpose:** Scrape lifetime earnings from OCEAN website for each worker

**Key Features:**
- Inherits from `SensorEntity` (not `CoordinatorEntity`)
- Uses its own `DataUpdateCoordinator` for independent scraping
- Each worker sensor scrapes its own page
- 5-minute update interval (respects OCEAN's servers)
- Proper error handling and logging

**Why Not Use the Main Coordinator?**
- API doesn't provide lifetime earnings
- Web scraping is slower and separate concern
- Different update intervals (API: 60s, Scrape: 300s)
- Isolated failures (scrape issues don't affect API sensors)

---

## To Apply Changes

### 1. Restart Home Assistant
```bash
# Restart Home Assistant to load the integration updates
```

### 2. Install BeautifulSoup4
Home Assistant should automatically install `beautifulsoup4` from the manifest requirements. If not:

```bash
# SSH into Home Assistant
# Activate the HA venv
source /srv/homeassistant/bin/activate

# Install beautifulsoup4
pip install beautifulsoup4==4.12.2
```

### 3. Reload the Integration
- Go to **Settings → Devices & Services**
- Find **OCEAN Mining Pool**
- Click **⋮** (three dots) → **Reload**

OR restart Home Assistant again

### 4. Verify New Entities
Go to **Developer Tools → States** and search for:
- `lifetime_earnings`

You should see new sensors like:
- `sensor.q_lifetime_earnings`
- `sensor.frankenmini3_lifetime_earnings`
- etc.

---

## Example Dashboard Card

```yaml
type: entities
title: Q Mining Stats
entities:
  - entity: sensor.q_hashrate_60s
    name: Current Hashrate
  - entity: sensor.q_estimated_earnings_next_block
    name: Next Block Earnings
  - entity: sensor.q_lifetime_earnings
    name: Total Earned (All Time)
  - entity: binary_sensor.q_status
    name: Online Status
```

---

## Troubleshooting

### Lifetime Earnings Shows "Unavailable"

**Possible Causes:**
1. OCEAN website structure changed
2. Worker name doesn't match URL format
3. Network connectivity issues

**Check Logs:**
```bash
# Check Home Assistant logs
Settings → System → Logs

# Search for: "lifetime earnings" or "OCEAN"
```

**Debug URL:**
Manually visit: `https://ocean.xyz/stats/bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv.{worker_name}`

Replace `{worker_name}` with your actual worker name (e.g., `Q`, `FrankenMini3`)

### Worker Sensors Not Grouping Properly

**Solution:** Delete the old device and restart HA
1. Go to **Settings → Devices & Services → OCEAN**
2. Click on the problematic worker device
3. Click **Delete Device**
4. Restart Home Assistant
5. The device will be recreated with correct entity assignments

---

## Comparison: Before vs After

### Before This Update:
```yaml
# Configuration.yaml approach (manual)
scrape:
  - resource: https://ocean.xyz/stats/bc1q...v.Exergy_Office
    scan_interval: 300
    sensor:
      - name: "Exergy Office Lifetime Earnings"
        select: "div.blocks-label:contains('Lifetime Earnings') ~ span"
        value_template: >
          {% set clean = value | replace(' BTC', '') | replace(',', '') | trim %}
          {{ clean }}
```

**Issues:**
- ✗ Manual configuration for each worker
- ✗ Not grouped with worker device
- ✗ Have to update when workers change
- ✗ Inconsistent naming

### After This Update:
```python
# Automatic in custom integration
entities.append(
    OceanWorkerLifetimeEarningsSensor(
        hass=hass,
        username=coordinator.username,
        worker_name=worker_name,
    )
)
```

**Benefits:**
- ✓ Automatic for all workers
- ✓ Grouped with worker device
- ✓ Dynamic (new workers auto-detected)
- ✓ Consistent naming
- ✓ Proper error handling

---

## Technical Notes

### BeautifulSoup vs Regex
We use BeautifulSoup instead of regex for HTML parsing because:
- More robust to HTML structure changes
- Easier to maintain
- Better error handling
- Standard practice for web scraping

### Update Interval (300s)
Why 5 minutes instead of 60 seconds?
- Lifetime earnings changes slowly (only on block finds)
- Reduces load on OCEAN's servers
- Web scraping is slower than API calls
- Avoids potential rate limiting

### State Class: `total_increasing`
Perfect for lifetime earnings because:
- Value only increases over time
- Home Assistant can calculate earnings rate
- Enables long-term statistics
- Works with energy dashboard (if desired)

---

## What's Next?

### Possible Future Enhancements:
1. **Earnings Rate Calculation:** Derivative sensor showing BTC/day
2. **USD Conversion:** Multiply lifetime BTC by current exchange rate
3. **Mining Efficiency:** Earnings per TH/s metric
4. **Notifications:** Alert when new earnings arrive
5. **Historical Charts:** Track lifetime earnings growth over time

---

**Date:** December 12, 2025  
**Integration Version:** 0.1.0  
**Status:** ✅ Complete and Ready to Deploy
