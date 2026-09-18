# Wi-Fi Connectivity Troubleshooting Guide

## Overview
This document covers common Wi-Fi connectivity issues in the office and remote environments.

## Issue: Cannot Connect to Wi-Fi

### Symptoms
- Wi-Fi network not appearing in available networks
- Unable to connect to a visible network
- "Cannot connect to this network" error

### Diagnostic Procedure
1. Check whether Wi-Fi is turned on (not in airplane mode).
2. Restart Wi-Fi by turning it off and on again.
3. Check whether the correct network name (SSID) is visible in the list.
4. If at the office, check whether colleagues can connect (may be access point issue).
5. Forget the network and reconnect: go to Wi-Fi settings, forget the network, then reconnect.
6. Restart the laptop/device.
7. If none of the above work, update Wi-Fi drivers.

### Resolution
If reconnecting and driver updates do not resolve the issue, escalate.

**Default Priority:** High (if in office), Medium (if remote/home)

---

## Issue: Wi-Fi Connected but No Internet

### Symptoms
- Shows "Connected" but no internet access
- Browser shows DNS errors or timeouts
- Wi-Fi indicator shows connected but with warning sign

### Diagnostic Procedure
1. Confirm the device shows "Connected" to the Wi-Fi network.
2. Try opening multiple websites to rule out single site issues.
3. Run the Windows Network Troubleshooter (right-click Wi-Fi icon → Troubleshoot).
4. Release and renew IP: open Command Prompt and run `ipconfig /release` then `ipconfig /renew`.
5. Flush DNS: `ipconfig /flushdns`.
6. Try connecting to a mobile hotspot to confirm the issue is with the Wi-Fi, not the device.
7. If mobile hotspot works, the issue is with the Wi-Fi network.

### Resolution
If the network itself has no internet, escalate immediately as it may affect multiple users.

**Default Priority:** High

---

## Issue: Slow Wi-Fi

### Symptoms
- Web pages load slowly
- Video calls drop or have poor quality
- Downloads are significantly slower than expected

### Diagnostic Procedure
1. Run a speed test at speedtest.net and record the results.
2. Check how many other devices are connected to the same network.
3. Move closer to the Wi-Fi access point if possible.
4. Disconnect and reconnect to refresh the connection.
5. Check for bandwidth-heavy applications running in the background (updates, backups).
6. Try connecting to 5GHz band instead of 2.4GHz if available.

### Resolution
If speeds are consistently below 10 Mbps despite being close to the access point, escalate.

**Default Priority:** Low

---

## Escalation Criteria
- Multiple users affected (access point issue)
- Wi-Fi network completely absent (infrastructure failure)
- Speed consistently degraded across multiple attempts over multiple days

**Ticket Category:** WiFi
