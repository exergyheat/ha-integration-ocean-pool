# OCEAN Integration - Complete Updates Summary

## All Changes Applied

### 1. ✅ Fixed "Estimated Earnings Next Block" Name
- Changed from "Estimated Earnings" to "Estimated Earnings Next Block"
- Applies to both account and worker sensors

### 2. ✅ Fixed Last Share Timestamp Sensors
**Problem:** Sensors were showing as unavailable
**Solution:** Made timestamps timezone-aware using `timezone.utc`

**Entities Fixed:**
- `sensor.mining_account_last_share_timestamp`
- `sensor.q_last_share`
- `sensor.frankenmini3_last_share`
- `sensor.upstairs_conference_room_last_share`
- `sensor.exergy_radiant_floor_last_share`
- `sensor.hb_trio_last_share`

### 3. ✅ Added Lifetime Earnings to Main Account
**NEW Entity:** `sensor.mining_account_lifetime_earnings`

**Display Name:** `Mining Account Lifetime Earnings`

**Details:**
- Scrapes from: `https://ocean.xyz/stats/{username}`
- Updates every 5 minutes
- Unit: BTC
- State Class: `total_increasing`
- Precision: 8 decimals
- Groups with Mining Account device

### 4. ✅ Added Lifetime Earnings to All Workers
**NEW Entities:**
- `sensor.q_lifetime_earnings`
- `sensor.frankenmini3_lifetime_earnings`
- `sensor.upstairs_conference_room_lifetime_earnings`
- `sensor.exergy_radiant_floor_lifetime_earnings`
- `sensor.hb_trio_lifetime_earnings`

---

## Final Device Structure

### 📱 Mining Account
```
Account-Level Sensors:
├─ Mining Account Hashrate (60s)
├─ Mining Account Hashrate (300s)
├─ Mining Account Active Workers
├─ Mining Account Shares (60s)
├─ Mining Account Shares (300s)
├─ Mining Account Shares in Tides
├─ Mining Account Estimated Earnings Next Block
├─ Mining Account Estimated Bonus Next Block
├─ Mining Account Estimated Total Earnings Next Block
├─ Mining Account Estimated Payout Next Block
├─ Mining Account Unpaid Balance
├─ Mining Account Unpaid Balance USD
├─ Mining Account Last Share Timestamp
└─ Mining Account Lifetime Earnings ⭐ NEW
```

### 📱 Q (Worker)
```
├─ Q Hashrate (60s)
├─ Q Hashrate (300s)
├─ Q Estimated Earnings Next Block
├─ Q Last Share ✅ FIXED
├─ Q Lifetime Earnings ⭐ NEW
└─ Q Status
```

### 📱 FrankenMini3 (Worker)
```
├─ FrankenMini3 Hashrate (60s)
├─ FrankenMini3 Hashrate (300s)
├─ FrankenMini3 Estimated Earnings Next Block
├─ FrankenMini3 Last Share ✅ FIXED
├─ FrankenMini3 Lifetime Earnings ⭐ NEW
└─ FrankenMini3 Status
```

### 📱 All Other Workers
Same sensor structure as above.

---

## Files Modified

### `sensor.py`
1. **Line 3:** Added `timezone` import
2. **Line 143:** Changed "Estimated Earnings" → "Estimated Earnings Next Block"
3. **Lines 188-196:** Added account lifetime earnings sensor
4. **Lines 293-299:** Fixed account last_share_ts with timezone-aware datetime
5. **Lines 372-471:** Added `OceanAccountLifetimeEarningsSensor` class
6. **Lines 516-525:** Fixed worker last_share_ts with timezone-aware datetime
7. **Lines 550-660:** Added `OceanWorkerLifetimeEarningsSensor` class

### `manifest.json`
- Added `beautifulsoup4==4.12.2` requirement

---

## How Lifetime Earnings Works

### Account Lifetime Earnings
- **URL:** `https://ocean.xyz/stats/bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv`
- **Scrapes:** Total lifetime earnings for entire account
- **Represents:** Sum of all workers' lifetime earnings
- **Update Interval:** 300 seconds (5 minutes)

### Worker Lifetime Earnings
- **URL:** `https://ocean.xyz/stats/bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv.{worker_name}`
- **Example:** `https://ocean.xyz/stats/...kvv.Q`
- **Scrapes:** Individual worker lifetime earnings
- **Update Interval:** 300 seconds (5 minutes)

### Scraping Logic
Both use identical BeautifulSoup parsing:
1. Fetch HTML from OCEAN stats page
2. Find `<div class="blocks-label">Lifetime Earnings</div>`
3. Extract value from next `<span>` element
4. Clean: Remove " BTC", commas, newlines, whitespace
5. Convert to float with 8 decimal precision

---

## To Apply All Updates

### 1. Restart Home Assistant
```bash
# Restart to load integration changes
# Home Assistant will auto-install beautifulsoup4
```

### 2. Verify New Entities
Go to **Developer Tools → States** and search for:
- `lifetime_earnings` (should show 6 entities)
- `last_share` (should all be working now)
- `estimated_earnings_next_block` (updated names)

### 3. Check Devices
Go to **Settings → Devices & Services → OCEAN**

You should see:
- **Mining Account** device with 14 entities (including lifetime earnings)
- Each **Worker** device with 6 entities each

---

## Example Dashboard Card

### Account Overview
```yaml
type: entities
title: Mining Account Overview
entities:
  - entity: sensor.mining_account_hashrate_60s
    name: Current Hashrate
  - entity: sensor.mining_account_active_workers
    name: Active Workers
  - entity: sensor.mining_account_lifetime_earnings
    name: Total Earned (All Time)
  - entity: sensor.mining_account_unpaid_balance
    name: Unpaid Balance
  - entity: sensor.mining_account_estimated_earnings_next_block
    name: Est. Next Block
  - entity: sensor.mining_account_last_share_timestamp
    name: Last Share
```

### Worker Comparison
```yaml
type: entities
title: Worker Lifetime Earnings
entities:
  - entity: sensor.q_lifetime_earnings
    name: Q
  - entity: sensor.frankenmini3_lifetime_earnings
    name: FrankenMini3
  - entity: sensor.upstairs_conference_room_lifetime_earnings
    name: Upstairs Conference Room
  - entity: sensor.exergy_radiant_floor_lifetime_earnings
    name: Exergy Radiant Floor
  - entity: sensor.hb_trio_lifetime_earnings
    name: hb-trio
  - type: divider
  - entity: sensor.mining_account_lifetime_earnings
    name: Total (All Workers)
    secondary_info: last-updated
```

---

## What You Can Remove

### From `configuration.yaml`
You can now **DELETE** these manual scrape configurations:
```yaml
# DELETE THIS - Now handled by integration
scrape:
  - resource: https://ocean.xyz/stats/bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv.Exergy_Office
    scan_interval: 300
    sensor:
      - name: "Exergy Office Lifetime Earnings"
        select: "div.blocks-label:contains('Lifetime Earnings') ~ span"
        value_template: >
          {% set clean = value | replace(' BTC', '') | replace(',', '') | trim %}
          {{ clean }}
        unit_of_measurement: "BTC"
        state_class: total_increasing
        
  - resource: https://ocean.xyz/stats/bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv.Upstairs_Conference_Room
    scan_interval: 300
    sensor:
      - name: "Upstairs Conference Room Lifetime Earnings"
        # ... same pattern
```

The integration now handles this automatically for **all workers** including new ones!

---

## Troubleshooting

### Last Share Still Not Working?
1. Check Home Assistant logs for timestamp errors
2. Verify the sensor shows a timestamp in Developer Tools → States
3. Entity ID format: `sensor.{worker_name}_last_share`
4. Should display like: "Dec 12, 2025, 3:45 PM"

### Lifetime Earnings Shows "Unavailable"?
1. Check logs for scraping errors
2. Manually visit the OCEAN stats URL in browser
3. Verify "Lifetime Earnings" label exists on page
4. Wait 5 minutes for first update after restart

### Worker Not Showing Lifetime Earnings?
1. Check worker name matches exactly (case-sensitive)
2. Visit: `https://ocean.xyz/stats/{username}.{worker_name}`
3. If page doesn't exist, worker might be named differently
4. Check Home Assistant logs for scraping errors

---

## Summary Statistics

### Total Entities Created
- **Account-level:** 14 sensors (1 new: lifetime earnings)
- **Per Worker:** 6 sensors each (1 new: lifetime earnings)
- **Total for 5 workers:** 30 worker sensors + 14 account = **44 entities**

### Network Impact
- **API calls:** Every 60 seconds (unchanged)
- **Web scraping:** Every 300 seconds (5 minutes)
- **Total requests:** 6 scrape requests every 5 minutes (account + 5 workers)
- **Bandwidth:** Minimal (~50KB total per 5 minutes)

---

**Status:** ✅ All Updates Complete  
**Date:** December 12, 2025  
**Integration Version:** 0.1.0  
**Ready to Deploy:** Yes
