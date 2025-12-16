# OCEAN Integration Entity Naming Updates

## Summary of Changes

This update cleans up the OCEAN integration entity names and device organization to improve readability in Home Assistant.

## Changes Made

### 1. Removed "OCEAN" Prefix from All Entity Names

**Before:**
- `sensor.ocean_bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv_active_workers`
- `sensor.ocean_bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv_hashrate_60s`
- `sensor.ocean_q_hashrate_60s`
- `binary_sensor.ocean_q_status`

**After:**
- `sensor.0p3qkvv_active_workers` (last 8 chars of address)
- `sensor.0p3qkvv_hashrate_60s` (last 8 chars of address)
- `sensor.q_hashrate_60s`
- `binary_sensor.q_status`

### 2. Shortened Bitcoin Address in Entity Names

The full Bitcoin address `bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv` is now shortened to just the last 8 characters `0p3qkvv` for account-level sensors.

**Modified Files:**
- `sensor.py` - Lines 244-247, 285-286
- Account sensors now use `display_name = coordinator.username[-8:]`

### 3. Separated Each Worker into Its Own Device

Each mining worker (Q, FrankenMini3, Upstairs_Conference_Room, Exergy_Radiant_Floor, hb-trio) now appears as a separate device in Home Assistant, making it easier to organize and view.

**Before:**
```
Device: OCEAN Mining Account (bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv)
  ├─ All account sensors
  ├─ All Q sensors
  ├─ All FrankenMini3 sensors
  └─ All other worker sensors
```

**After:**
```
Device: Mining Account (0p3qkvv)
  ├─ Active Workers
  ├─ Hashrate (60s)
  ├─ Unpaid Balance
  └─ Other account-level sensors

Device: Q (linked to Mining Account)
  ├─ Q Hashrate (60s)
  ├─ Q Hashrate (300s)
  ├─ Q Status
  └─ Q Estimated Earnings

Device: FrankenMini3 (linked to Mining Account)
  ├─ FrankenMini3 Hashrate (60s)
  ├─ FrankenMini3 Hashrate (300s)
  └─ ...

Device: Upstairs_Conference_Room (linked to Mining Account)
  └─ ...
```

**Modified Files:**
- `sensor.py` - Lines 354-363 (OceanWorkerSensor.device_info)
- `binary_sensor.py` - Lines 94-102 (OceanWorkerStatusSensor.device_info)

### 4. Updated Device Names

**Before:**
- `OCEAN Mining Account (bc1qmlmvl0j8ufdtllml65xjl8xf2z06fn40p3qkvv)`

**After:**
- `Mining Account (0p3qkvv)`
- Each worker device: `Q`, `FrankenMini3`, `Upstairs_Conference_Room`, etc.

## How to Apply These Changes

1. **Copy the updated custom component files** to your Home Assistant custom_components directory:
   - `ocean/sensor.py`
   - `ocean/binary_sensor.py`

2. **Restart Home Assistant**

3. **Reload the OCEAN integration** or restart Home Assistant again

4. **Optional: Clean up old entities** if Home Assistant doesn't automatically rename them:
   - Go to Developer Tools → States
   - Search for entities starting with `ocean_`
   - Delete any old entities that weren't automatically migrated
   - The new entities will appear with the updated names

## Files Modified

- ✅ `sensor.py` - Account sensor naming (lines 244-247, 250-260)
- ✅ `sensor.py` - Unpaid USD sensor naming (lines 285-286, 293-301)
- ✅ `sensor.py` - Worker sensor naming (lines 348-352)
- ✅ `sensor.py` - Worker device separation (lines 354-363)
- ✅ `binary_sensor.py` - Worker status naming (lines 88-91)
- ✅ `binary_sensor.py` - Worker device separation (lines 94-102)

## Expected Result

Your OCEAN entities will now be:
- **Cleaner** - No "OCEAN" prefix cluttering the names
- **More readable** - Bitcoin address shortened to last 8 chars
- **Better organized** - Each worker has its own device card
- **Easier to use** - Workers can be added to dashboards individually

## Example Entity Names

### Account-Level Entities (Device: "Mining Account (0p3qkvv)")
- `sensor.0p3qkvv_hashrate_60s`
- `sensor.0p3qkvv_active_workers`
- `sensor.0p3qkvv_unpaid_balance`
- `sensor.0p3qkvv_unpaid_balance_usd`

### Worker Entities (Device: "Q")
- `sensor.q_hashrate_60s`
- `sensor.q_hashrate_300s`
- `sensor.q_estimated_earnings`
- `binary_sensor.q_status`

### Worker Entities (Device: "FrankenMini3")
- `sensor.frankenmini3_hashrate_60s`
- `sensor.frankenmini3_hashrate_300s`
- `binary_sensor.frankenmini3_status`

---

**Date Modified:** December 11, 2025  
**Integration Version:** OCEAN Mining Pool Custom Integration
