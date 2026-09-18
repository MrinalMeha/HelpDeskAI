# Password and Account Troubleshooting Guide

## Overview
This document covers issues related to passwords, account lockouts, and access credentials.

## Issue: Forgotten Password

### Symptoms
- Employee cannot remember their password
- Login fails with correct-feeling credentials
- "The user name or password is incorrect"

### Diagnostic Procedure
1. Direct the employee to the self-service password reset portal: reset.company.com
2. The employee should enter their company email address and follow the prompts.
3. A reset link will be sent to their personal recovery email or mobile number on file.
4. If the employee has no recovery method on file, IT must verify identity manually.
5. After resetting, test the new password with Outlook Web (outlook.office.com) before using other apps.

### Resolution
The self-service portal resolves most cases. If the portal fails, escalate.

**Default Priority:** High

---

## Issue: Account Locked Out

### Symptoms
- "Your account has been locked" message
- Cannot log in despite knowing the correct password
- Active Directory lockout after multiple failed attempts

### Diagnostic Procedure
1. Wait 15 minutes — accounts auto-unlock after the lockout period in most configurations.
2. If still locked after 15 minutes, use the self-service unlock option at reset.company.com.
3. If the account keeps locking out shortly after being unlocked, check for applications using old cached credentials (e.g., phone syncing with old Outlook password).
4. On Windows, open Credential Manager and remove any saved company credentials, then re-enter.
5. Check mobile devices for old email account passwords.

### Resolution
If the account repeatedly locks out, investigate connected applications with stored credentials.

**Default Priority:** High

---

## Issue: Multi-Factor Authentication (MFA) Problems

### Symptoms
- MFA code not received
- Authenticator app not working
- "Verification failed" during MFA step

### Diagnostic Procedure
1. Ensure the phone has signal/internet if using SMS codes.
2. Check that the authenticator app time is synchronized (open app settings → sync time).
3. Try an alternative MFA method (backup codes, alternate phone, authenticator app vs. SMS).
4. If no alternative methods are available, IT must manually bypass MFA once for re-enrollment.

### Resolution
If all MFA methods are unavailable, the employee cannot log in remotely until IT assists.

**Default Priority:** Critical

---

## Issue: Password Expired

### Symptoms
- "Your password has expired and must be changed"
- Forced to change password at login
- Cannot log in at all after expiry in some configurations

### Diagnostic Procedure
1. If the system prompts for a new password, follow the on-screen instructions to set one.
2. The new password must meet the company policy: at least 12 characters, uppercase, lowercase, number, and special character.
3. If the password change prompt is not appearing, use reset.company.com.
4. Update the new password on all devices (phone, tablet, secondary laptop) to prevent lockouts.

### Resolution
Most cases resolved by following the reset process.

**Default Priority:** High

---

## Escalation Criteria
- Self-service portal not working
- MFA has no available methods
- Account locked out continuously despite resolving old credentials
- Security concern (possible account compromise)

**Ticket Category:** Password
