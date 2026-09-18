# Email / Outlook Troubleshooting Guide

## Overview
This document covers common Microsoft Outlook and email-related issues.

## Issue: Outlook Not Syncing / Emails Not Receiving

### Symptoms
- New emails not appearing
- Send/Receive button shows error
- Outlook stuck on "Updating Inbox"

### Diagnostic Procedure
1. Check internet connectivity (browse to a website).
2. Check whether Outlook is in Offline Mode: look for "Working Offline" in the status bar; if present, click Send/Receive → Work Offline to toggle it off.
3. Click Send/Receive All (F9) to force a manual sync.
4. Check the status bar at the bottom of Outlook for error messages.
5. Restart Outlook.
6. If issue persists, check whether the same account works on webmail (outlook.office.com).
7. If webmail works but Outlook does not, the issue is with the desktop client.

### Resolution
If webmail works but Outlook does not sync after restart, rebuild the Outlook profile.

**Default Priority:** Medium

---

## Issue: Cannot Send Emails

### Symptoms
- Emails stuck in Outbox
- "Message could not be sent" error
- Send button grayed out

### Diagnostic Procedure
1. Check that the email is not stuck due to a large attachment (over 25 MB limit).
2. Verify the recipient email address is typed correctly.
3. Check the Outbox folder for stuck messages.
4. Delete the stuck message and try again with a smaller test message.
5. Check whether internet connectivity is working.
6. Ensure Outlook is not in Offline Mode.
7. Restart Outlook and try again.

### Resolution
If small test messages also fail to send, check SMTP settings with IT.

**Default Priority:** High

---

## Issue: Outlook Not Opening / Crashing

### Symptoms
- Outlook crashes on startup
- "Cannot start Microsoft Outlook" error
- Outlook freezes immediately after launch

### Diagnostic Procedure
1. Start Outlook in Safe Mode: hold Ctrl while clicking the Outlook icon, or run `outlook.exe /safe` from Run dialog.
2. If Safe Mode works, a plugin is likely causing the crash. Disable all add-ins via File → Options → Add-ins.
3. If Safe Mode also fails, repair the Office installation: Control Panel → Programs → Microsoft Office → Change → Repair.
4. Check whether the OST/PST data file is corrupted using the Inbox Repair Tool (scanpst.exe).

### Resolution
If repair does not fix the issue, the Outlook profile may need to be recreated.

**Default Priority:** High

---

## Issue: Calendar Not Syncing

### Symptoms
- Meeting invites not appearing
- Calendar shows wrong times
- Free/Busy information not updating

### Diagnostic Procedure
1. Check whether the calendar issue is also visible on the Outlook web version.
2. Restart Outlook.
3. Check time zone settings (File → Options → Calendar).
4. Verify the calendar is not accidentally hidden (check the Calendars panel on the left).

### Resolution
If the calendar issue exists on webmail too, it may be a server-side issue.

**Default Priority:** Medium

---

## Escalation Criteria
- Cannot send or receive email despite troubleshooting
- Outlook crashes in Safe Mode
- Issue affects multiple users (server-side problem)
- Password has expired and reset is not possible

**Ticket Category:** Email
