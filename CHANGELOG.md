# Changelog

## v1.1.4

* `[Fix]` Fix issue in API when creating and updating records without defining conditional data.

## v1.1.3

* `[Fix]` Fix issue when auto-creating zone from a log entry.

## v1.1.2

* `[New]` Implement support DNS Cache.
* `[New]` Implement support for CAA records.
* `[Fix]` Return SOA responses the right way.
* `[Fix]` Fix issue to match domains regardless of upper/lower case formats.

## v1.1.1

* `[Fix]` Fix RADIUS password encoding from `ascii` to `utf8`.

## v1.1.0

* `[New]` Implement RADIUS authentication.
* `[New]` Implement Regular Expression matching for zones.
* `[New]` Optional functionality to change user password on Active Directory via LDAP.
* `[Fix]` Update password complexity checks to accept non-7-bit ASCII.
* `[Fix]` Fix 2FA secrets 160-bit key issue.
* `[Fix]` Fix issue with LDAP password change for users that have never logged in before.
