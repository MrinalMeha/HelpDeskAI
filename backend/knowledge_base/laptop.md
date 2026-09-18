# Slow Laptop / Performance Troubleshooting Guide

## Overview
This document covers performance issues including slow startup, application lag, and freezing.

## Issue: Laptop Running Slowly

### Symptoms
- Applications take a long time to open
- System feels generally sluggish
- High CPU or memory usage shown in Task Manager

### Diagnostic Procedure
1. Open Task Manager (Ctrl+Shift+Esc) and check the CPU, Memory, and Disk columns.
2. Identify any processes consuming excessive resources. Note the process names.
3. Check available disk space: open File Explorer → right-click C: drive → Properties. If free space is less than 10%, this could cause slowness.
4. Restart the laptop — this clears temporary files and often resolves temporary slowdowns.
5. Run Windows Disk Cleanup (search "Disk Cleanup" in Start menu) to free disk space.
6. Check for pending Windows updates that may be installing in the background.
7. Disable unnecessary startup programs: Task Manager → Startup tab → disable non-essential programs.

### Resolution
A restart combined with disk cleanup resolves most performance issues. If not, continue diagnosis.

**Default Priority:** Medium

---

## Issue: High CPU Usage

### Symptoms
- Fan running loudly and constantly
- CPU in Task Manager consistently above 80%
- Applications respond slowly or freeze

### Diagnostic Procedure
1. Open Task Manager and sort by CPU usage.
2. Check for Windows Update or antivirus scans running (these are normal but temporary).
3. Check for unknown processes — if a process with an unfamiliar name is using high CPU, note the name.
4. Restart the laptop to see if the high CPU usage clears.
5. If a specific application is always causing high CPU, check whether an update is available for it.
6. Run a malware scan using Windows Defender.

### Resolution
If CPU usage remains high after restart and antivirus scan, escalate with Task Manager screenshot.

**Default Priority:** Medium

---

## Issue: Laptop Freezing or Crashing

### Symptoms
- Blue screen of death (BSOD)
- System completely freezes and requires hard restart
- Applications crash frequently

### Diagnostic Procedure
1. Note the error code on the Blue Screen if possible (example: IRQL_NOT_LESS_OR_EQUAL).
2. Check Windows Event Viewer for recent critical errors (search "Event Viewer" → Windows Logs → System).
3. Run Windows Memory Diagnostic (search "Windows Memory Diagnostic" in Start menu) to check RAM.
4. Check if the laptop gets physically hot — overheating causes BSOD and freezes.
5. Ensure all drivers are up to date, especially display and chipset drivers.
6. Check disk health: open Command Prompt as admin and run `chkdsk /f`.

### Resolution
BSODs after memory diagnostic failure indicate failing RAM. Hardware replacement required. Escalate immediately.

**Default Priority:** High

---

## Issue: Slow Startup

### Symptoms
- Laptop takes more than 3-5 minutes to be usable after power-on
- Login screen takes very long to appear

### Diagnostic Procedure
1. Disable unnecessary startup programs: Task Manager → Startup tab.
2. Ensure BitLocker (full disk encryption) is not the cause — first boot after update is always slower.
3. Check whether an antivirus full scan is scheduled at startup.
4. Ensure the laptop has at least 15% free disk space.
5. Check if SSD or HDD: HDDs are significantly slower. If the laptop has an HDD, SSD upgrade may be warranted.

### Resolution
Disabling startup programs is the most impactful fix. Hardware upgrade may be needed for aging HDD laptops.

**Default Priority:** Low

---

## Escalation Criteria
- BSOD recurring despite troubleshooting
- Memory diagnostic shows errors (hardware failure)
- Disk drive failure suspected
- Extreme overheating (hardware issue)
- Laptop over 5 years old with multiple issues

**Ticket Category:** Laptop
