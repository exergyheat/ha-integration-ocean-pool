#!/usr/bin/env python3
"""Test script for OCEAN API connectivity and data parsing.

Run this script to verify API access and see what data will be available.

Usage:
    python TEST_API.py bc1qcnpuc5scg0n4hpwpvalntmg6n0c0349x9jfgcj
"""

import asyncio
import json
import sys
from typing import Any

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp not installed. Install with: pip install aiohttp")
    sys.exit(1)


API_BASE_URL = "https://api.ocean.xyz/v1"


async def test_api(username: str):
    """Test OCEAN API endpoints."""
    
    print(f"\n{'='*60}")
    print(f"Testing OCEAN API for user: {username}")
    print(f"{'='*60}\n")
    
    async with aiohttp.ClientSession() as session:
        # Test userinfo_full endpoint
        url = f"{API_BASE_URL}/userinfo_full/{username}"
        print(f"📡 Fetching: {url}")
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"✅ Status: {response.status}")
                
                if response.status != 200:
                    print(f"❌ Error: HTTP {response.status}")
                    return
                
                data = await response.json()
                result = data.get("result")
                
                if not result:
                    print("❌ No result data found")
                    return
                
                # Parse account data
                print(f"\n{'='*60}")
                print("ACCOUNT DATA")
                print(f"{'='*60}")
                
                user_full = result.get("user_full", {})
                
                hashrate_60s = float(user_full.get("hashrate_60s", 0)) / 1_000_000_000_000
                hashrate_300s = float(user_full.get("hashrate_300s", 0)) / 1_000_000_000_000
                
                print(f"  Hashrate (60s):      {hashrate_60s:.2f} TH/s")
                print(f"  Hashrate (300s):     {hashrate_300s:.2f} TH/s")
                print(f"  Shares (60s):        {user_full.get('shares_60s', 0):,}")
                print(f"  Shares (300s):       {user_full.get('shares_300s', 0):,}")
                print(f"  Shares in Tides:     {user_full.get('shares_in_tides', 0):,}")
                print(f"  Estimated Earnings:  {float(user_full.get('estimated_earn_next_block', 0)):.8f} BTC")
                print(f"  Unpaid Balance:      {float(user_full.get('unpaid', 0)):.8f} BTC")
                print(f"  Last Share:          {user_full.get('lastest_share_ts', 'N/A')}")
                
                # Parse workers
                workers = result.get("workers", [])
                
                print(f"\n{'='*60}")
                print(f"WORKERS ({len(workers)} total)")
                print(f"{'='*60}\n")
                
                active_count = 0
                
                for worker_dict in workers:
                    for worker_name, worker_data in worker_dict.items():
                        hashrate = float(worker_data.get("hashrate_60s", 0)) / 1_000_000_000_000
                        shares = int(worker_data.get("shares_60s", 0))
                        is_active = shares > 0
                        
                        if is_active:
                            active_count += 1
                        
                        status = "🟢 ACTIVE" if is_active else "🔴 OFFLINE"
                        
                        print(f"  {status} {worker_name}")
                        print(f"    Hashrate (60s):  {hashrate:.2f} TH/s")
                        print(f"    Shares (60s):    {shares:,}")
                        print(f"    Last Share:      {worker_data.get('lastest_share_ts', 'N/A')}")
                        print()
                
                print(f"{'='*60}")
                print(f"SUMMARY")
                print(f"{'='*60}")
                print(f"  Total Workers:       {len(workers)}")
                print(f"  Active Workers:      {active_count}")
                print(f"  Offline Workers:     {len(workers) - active_count}")
                print(f"  Total Hashrate:      {hashrate_60s:.2f} TH/s")
                print(f"{'='*60}\n")
                
                # Estimate entity count
                account_sensors = 13
                worker_sensors = len(workers) * 4
                worker_binary_sensors = len(workers) * 1
                total_entities = account_sensors + worker_sensors + worker_binary_sensors
                
                print("📊 ESTIMATED ENTITIES IN HOME ASSISTANT:")
                print(f"  Account Sensors:     {account_sensors}")
                print(f"  Worker Sensors:      {worker_sensors} ({len(workers)} workers × 4)")
                print(f"  Worker Binary:       {worker_binary_sensors} ({len(workers)} workers × 1)")
                print(f"  TOTAL:               {total_entities} entities")
                print()
                
                # Save raw data for debugging
                with open("ocean_api_response.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("💾 Raw API response saved to: ocean_api_response.json")
                
        except asyncio.TimeoutError:
            print("❌ Timeout connecting to OCEAN API")
        except aiohttp.ClientError as err:
            print(f"❌ Client error: {err}")
        except Exception as err:
            print(f"❌ Unexpected error: {err}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python TEST_API.py <username>")
        print("Example: python TEST_API.py bc1qcnpuc5scg0n4hpwpvalntmg6n0c0349x9jfgcj")
        sys.exit(1)
    
    username = sys.argv[1]
    asyncio.run(test_api(username))
