#!/usr/bin/env python3
"""Check if Chromium CDP is properly configured"""

import subprocess
import requests
import sys

print("=== CDP Connection Diagnostic ===\n")

# Check 1: Is port 9222 listening?
print("1. Checking if port 9222 is listening...")
try:
    result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
    if "9222" in result.stdout:
        print("   ✓ Port 9222 is in use")
        for line in result.stdout.split("\n"):
            if "9222" in line:
                print(f"   {line.strip()}")
    else:
        print("   ✗ Port 9222 is NOT in use")
        print("   → Chromium needs to be started with: chromium --remote-debugging-port=9222 https://chatgpt.com")
except:
    print("   ? Could not check port (ss command not available)")

print()

# Check 2: Can we connect to CDP endpoint?
print("2. Testing CDP HTTP endpoint...")
try:
    response = requests.get("http://localhost:9222/json/version", timeout=2)
    if response.status_code == 200:
        print("   ✓ CDP endpoint is responding!")
        data = response.json()
        print(f"   Browser: {data.get('Browser', 'unknown')}")
        print(f"   Protocol-Version: {data.get('Protocol-Version', 'unknown')}")
    else:
        print(f"   ✗ CDP endpoint returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ✗ Cannot connect to CDP endpoint")
    print("   → Make sure Chromium is running with remote debugging enabled")
except Exception as e:
    print(f"   ✗ Error: {e}")

print()

# Check 3: List available pages
print("3. Checking available pages/tabs...")
try:
    response = requests.get("http://localhost:9222/json", timeout=2)
    if response.status_code == 200:
        pages = response.json()
        print(f"   ✓ Found {len(pages)} page(s):")
        for i, page in enumerate(pages[:3], 1):
            url = page.get('url', 'unknown')
            title = page.get('title', 'unknown')[:50]
            print(f"   {i}. {title} - {url}")
        if len(pages) > 3:
            print(f"   ... and {len(pages) - 3} more")
    else:
        print(f"   ✗ Could not list pages (status {response.status_code})")
except Exception as e:
    print(f"   ✗ Error: {e}")

print()
print("=== Diagnostic Complete ===")
print("\nIf CDP is not working:")
print("  1. Kill any existing Chromium: pkill chromium")
print("  2. Start fresh: ./scripts/start_chromium.sh")
print("  3. Wait 10-15 seconds for Chromium to fully load")
print("  4. Make sure you're logged into ChatGPT")
