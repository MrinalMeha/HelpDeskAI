# Application Access and Software Troubleshooting Guide

## Overview
This document covers issues related to accessing business applications, software errors, and permission problems.

## Issue: Cannot Access a Business Application

### Symptoms
- "Access Denied" or "403 Forbidden" error
- Application not visible in software catalog
- Cannot log in to a specific business tool

### Diagnostic Procedure
1. Confirm the employee has requested access through the standard access request process (ServiceDesk portal or manager approval).
2. Check whether the employee's manager has approved the access request.
3. Try logging out and logging back in to refresh permissions.
4. Clear the browser cache and cookies if the application is web-based.
5. Try accessing from a different browser.
6. Check whether colleagues in the same role have access (to determine if it's a permission issue or software configuration).

### Resolution
If access was never requested, guide the employee through the access request process. If access was approved but not provisioned, escalate.

**Default Priority:** Medium

---

## Issue: Application Not Installing

### Symptoms
- Installation fails with error code
- "You don't have permission to install software" message
- Installation appears to complete but app does not appear

### Diagnostic Procedure
1. Check whether the application is available in the company software catalog (Company Portal / Self Service).
2. If available in the catalog, install it from there rather than downloading directly — this ensures proper licensing.
3. If the employee does not have admin rights, they must install from the company catalog only.
4. If the installation from the catalog fails, note the error code.
5. Ensure there is sufficient disk space (at least 5 GB free for most applications).
6. Restart the laptop and try again.

### Resolution
Most application installations are resolved by using the company catalog. If the catalog fails, escalate.

**Default Priority:** Medium

---

## Issue: Application Crashing or Not Loading

### Symptoms
- Application crashes immediately on launch
- Application loads then freezes
- Error messages when opening the application

### Diagnostic Procedure
1. Close and reopen the application.
2. Restart the laptop.
3. Check whether an update is available for the application (Help → Check for Updates).
4. Uninstall and reinstall the application from the company catalog.
5. Check Windows Event Viewer for application-specific errors (Event Viewer → Windows Logs → Application).
6. Check if the issue occurs for other users on the same machine.

### Resolution
Reinstallation resolves most application crash issues.

**Default Priority:** Medium

---

## Issue: Missing Software License / License Expired

### Symptoms
- "License expired" or "Activation required" message
- Application enters read-only mode
- Warning about subscription expiry

### Diagnostic Procedure
1. Check when the license was last renewed.
2. Confirm the employee's role still requires that software (license may have been intentionally removed).
3. Contact IT for license re-assignment or renewal.

### Resolution
License assignment is managed by IT. Escalate with the software name and employee details.

**Default Priority:** Medium

---

## Issue: Cannot Access Shared Drive / Network Drive

### Symptoms
- Shared drive not appearing in File Explorer
- "Network path not found" error
- Drive visible but shows as disconnected

### Diagnostic Procedure
1. Check that the VPN is connected if working remotely.
2. Try accessing the drive by its UNC path directly (e.g., \\server\share in the address bar).
3. Disconnect and reconnect to the network drive: right-click the drive → Disconnect, then reconnect.
4. Restart the laptop.
5. If drive never appeared, the employee may not have been granted access to it.

### Resolution
If the drive is simply not mapped, IT can push the mapping. If access was never granted, follow the access request process.

**Default Priority:** Medium

---

## Escalation Criteria
- Access request approved but not provisioned after 24 hours
- Application consistently crashes after reinstallation
- License issues affecting business-critical software
- Multiple employees cannot access the same application (systemic issue)

**Ticket Category:** Application
