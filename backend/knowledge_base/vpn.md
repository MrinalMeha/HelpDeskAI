# VPN Troubleshooting Guide

## Overview
This document covers common VPN connectivity issues and how to resolve them.

## Issue: Cannot Connect to VPN

### Symptoms
- VPN client fails to connect
- Connection times out
- "Unable to reach server" message

### Diagnostic Procedure
1. Check whether normal internet access works (open a browser and visit google.com).
2. If no internet, resolve the internet connectivity issue first.
3. Restart the VPN client application completely.
4. Try connecting again.
5. If still failing, reinstall the VPN client.

### Resolution
If restarting and reinstalling does not help, escalate to IT team.

**Default Priority:** Medium

---

## Issue: Authentication Failure

### Symptoms
- VPN shows "Authentication Failed"
- Credentials are rejected
- "Invalid username or password"

### Diagnostic Procedure
1. Verify the employee is using their current Active Directory/company credentials.
2. Check whether the password has recently expired (employees receive email 7 days before expiry).
3. Try logging in to company email with the same credentials to confirm they work.
4. Restart the VPN client.
5. Attempt connection again with verified credentials.
6. If the password is expired, use the password reset portal at reset.company.com.

### Resolution
If authentication still fails after verifying and potentially resetting the password, escalate to IT.

**Default Priority:** Medium

---

## Issue: VPN Connected but Cannot Access Internal Resources

### Symptoms
- VPN shows as connected
- Cannot reach internal servers, shared drives, or intranet sites
- Getting timeouts accessing internal resources

### Diagnostic Procedure
1. Confirm the VPN shows "Connected" status in the client.
2. Try accessing multiple internal resources to rule out single-server issues.
3. Disconnect and reconnect VPN.
4. Check if split tunneling is enabled (may route only some traffic through VPN).
5. Flush DNS: run `ipconfig /flushdns` on Windows or `sudo dscacheutil -flushcache` on Mac.
6. Restart the network adapter.

### Resolution
If internal resources remain inaccessible, the issue may be server-side. Escalate with details on which resources are unreachable.

**Default Priority:** High

---

## Escalation Criteria
- Authentication failures not resolved by password reset
- VPN client reinstallation does not resolve connectivity
- Multiple employees affected simultaneously (possible server outage)
- VPN connected but resources completely unreachable

**Ticket Category:** VPN
