# Changelog

## v1.1.1

* `[Fix]` Fix RADIUS password encoding from `ascii` to `utf8`.

## v1.1.0

* `[New]` Implement RADIUS authentication.
* `[New]` Implement Regular Expression matching for zones.
* `[New]` Optional functionality to change user password on Active Directory via LDAP.
* `[Fix]` Update password complexity checks to accept non-7-bit ASCII.
* `[Fix]` Fix 2FA secrets 160-bit key issue.
* `[Fix]` Fix issue with LDAP password change for users that have never logged in before.
