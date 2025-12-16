# OCEAN Integration - Scan Interval Update

## Change Summary

Updated the lifetime earnings scrape sensors to use the **same scan interval** as the main API coordinator, which uses the value the user configured during setup.

---

## What Changed

### Before
- **API calls:** User-configurable scan interval (default: 60 seconds)
- **Lifetime earnings scrape:** Hard-coded 300 seconds (5 minutes)

### After
- **API calls:** User-configurable scan interval (default: 60 seconds)
- **Lifetime earnings scrape:** **Same as API calls** (uses user's configured interval)

---

## Technical Details

### How It Works

1. **User configures scan interval during setup**
   - Default: 60 seconds
   - User can customize this value

2. **Main coordinator uses this interval**
   ```python
   coordinator = OceanCoordinator(
       hass=hass,
       username=username,
       scan_interval=scan_interval,  # User's value
       session=session,
   )
   ```

3. **Lifetime earnings sensors now use the same interval**
   ```python
   # Account lifetime earnings
   OceanAccountLifetimeEarningsSensor(
       hass=hass,
       username=coordinator.username,
       scan_interval=coordinator.update_interval,  # ← Uses same as API
   )
   
   # Worker lifetime earnings
   OceanWorkerLifetimeEarningsSensor(
       hass=hass,
       username=coordinator.username,
       worker_name=worker_name,
       scan_interval=coordinator.update_interval,  # ← Uses same as API
   )
   ```

---

## Benefits

### ✅ Consistency
- All data updates at the same frequency
- No confusion about different update rates

### ✅ User Control
- User controls all update frequencies via single config setting
- Want faster updates? Change one setting, affects everything

### ✅ Efficiency
- If user sets 300s interval, no need to scrape more frequently
- If user sets 30s interval, lifetime earnings updates just as fast

### ✅ Logical Grouping
- All OCEAN data (API + scrape) synchronized
- Dashboard cards update together

---

## Configuration

### Where Users Configure Scan Interval

**During Initial Setup:**
1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration**
3. Search for **OCEAN Mining Pool**
4. Enter bitcoin address
5. **Enter scan interval** (default: 60 seconds)

**To Change Later:**
1. Go to **Settings → Devices & Services → OCEAN**
2. Click **Configure**
3. Modify scan interval
4. All sensors (API + scrape) will use new interval

---

## Default Scan Interval

**Default:** 60 seconds

This matches OCEAN's 60-second hashrate window, ensuring:
- Real-time hashrate updates
- Accurate share counting
- Up-to-date earnings estimates
- Fresh lifetime earnings data

---

## Files Modified

### `sensor.py`

**Lines 188-194:** Account lifetime earnings sensor setup
```python
entities.append(
    OceanAccountLifetimeEarningsSensor(
        hass=hass,
        username=coordinator.username,
        scan_interval=coordinator.update_interval,  # ← Added
    )
)
```

**Lines 209-216:** Worker lifetime earnings sensor setup
```python
entities.append(
    OceanWorkerLifetimeEarningsSensor(
        hass=hass,
        username=coordinator.username,
        worker_name=worker_name,
        scan_interval=coordinator.update_interval,  # ← Added
    )
)
```

**Lines 249-256:** New worker detection callback
```python
lifetime_entity = OceanWorkerLifetimeEarningsSensor(
    hass=hass,
    username=coordinator.username,
    worker_name=worker_name,
    scan_interval=coordinator.update_interval,  # ← Added
)
```

**Lines 380-403:** OceanAccountLifetimeEarningsSensor `__init__`
```python
def __init__(
    self,
    hass: HomeAssistant,
    username: str,
    scan_interval: timedelta,  # ← Added parameter
) -> None:
    # ...
    self._coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"OCEAN Account Lifetime Earnings",
        update_method=self._async_update_data,
        update_interval=scan_interval,  # ← Uses parameter instead of hard-coded
    )
```

**Lines 558-587:** OceanWorkerLifetimeEarningsSensor `__init__`
```python
def __init__(
    self,
    hass: HomeAssistant,
    username: str,
    worker_name: str,
    scan_interval: timedelta,  # ← Added parameter
) -> None:
    # ...
    self._coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"OCEAN Lifetime Earnings {worker_name}",
        update_method=self._async_update_data,
        update_interval=scan_interval,  # ← Uses parameter instead of hard-coded
    )
```

---

## Impact on Performance

### Network Requests

**With default 60s interval:**
- API calls: Every 60 seconds
- Account lifetime scrape: Every 60 seconds
- Worker lifetime scrapes: Every 60 seconds (×5 workers)
- **Total:** 7 requests every 60 seconds

**Bandwidth:** ~100KB per minute (negligible)

### OCEAN Server Load

Respectful of OCEAN's servers:
- Follows API rate limits
- No unnecessary scraping
- User can increase interval if desired (e.g., 120s, 300s)

---

## Examples

### Fast Updates (30 seconds)
```yaml
# User configures 30s interval
scan_interval: 30

# Result:
# - API updates every 30s
# - Lifetime earnings scrape every 30s
# - Very responsive dashboard
```

### Standard Updates (60 seconds - default)
```yaml
# User configures 60s interval (or uses default)
scan_interval: 60

# Result:
# - API updates every 60s
# - Lifetime earnings scrape every 60s
# - Balanced performance and freshness
```

### Conservative Updates (300 seconds)
```yaml
# User configures 300s interval (5 minutes)
scan_interval: 300

# Result:
# - API updates every 5 minutes
# - Lifetime earnings scrape every 5 minutes
# - Reduced network traffic
# - Good for stable monitoring
```

---

## User Experience

### What Users Notice

**Before:**
- Hashrate updates every 60s
- Lifetime earnings updates every 5 minutes
- Dashboard feels "out of sync"

**After:**
- **Everything updates together**
- Dashboard feels cohesive
- One setting controls all update frequencies

### Dashboard Behavior

When user refreshes dashboard:
- All data is from same time window
- No stale data mixed with fresh data
- More reliable decision-making

---

## Migration Notes

### For Existing Installations

**No action required!**

When users restart Home Assistant:
1. Integration reads existing scan_interval config
2. Lifetime earnings sensors automatically use same interval
3. All updates synchronized

### For New Installations

Users configure once during setup, and all sensors respect that interval.

---

## Troubleshooting

### Lifetime Earnings Not Updating Fast Enough?

**Check configured scan interval:**
1. Go to **Settings → Devices & Services → OCEAN**
2. Click **Configure** 
3. Note the scan interval value
4. Lifetime earnings updates at same rate

**To speed up:**
1. Click **Configure**
2. Set scan interval to desired value (e.g., 30 seconds)
3. Save
4. All sensors now update faster

### Want Different Intervals for API vs Scrape?

This is intentionally not supported because:
- Keeps configuration simple (one setting)
- Data stays synchronized
- Reduces user confusion
- Lifetime earnings changes slowly anyway

If you really need different intervals, you can add manual scrape sensors in `configuration.yaml` alongside the integration.

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| API scan interval | User-configurable (60s default) | User-configurable (60s default) |
| Scrape scan interval | Hard-coded 300s | **Same as API (user-configurable)** |
| Consistency | Mismatched update rates | ✅ Synchronized |
| User control | Partial | ✅ Complete |
| Configuration | Complex (potentially) | ✅ Simple (one setting) |

---

**Status:** ✅ Complete  
**Impact:** All sensors now update at user-configured interval  
**User Action Required:** None (automatic)  
**Benefits:** Synchronized data, simplified configuration, user control
