# SnitchDNS Documentation

* [Environment Variables](#environment-variables)
* [Configuration Settings](#snitchdns-configuration-settings)
* [DNS Record Properties](#dns-record-properties)
* [IP Restrictions](#ip-restrictions)
* [Bind9 Forwarding](#bind9-forwarding)
* [Cloud Hosting](#cloud-hosting)

## Environment Variables

| Type | Name | Description | Required | Expected Value(s) | Default |
| ---- | ---- | ----------- | -------- | ----------------- | ------- |
| Database | `SNITCHDNS_DBMS` | DBMS | No | `sqlite`, `mysql`, `postgres` | `sqlite` |
| Database | `SNITCHDNS_DB_USER` | DB User | Only for `mysql` and `postgres` | | None |
| Database | `SNITCHDNS_DB_PW` | DB Password | Only for `mysql` and `postgres` | | None |
| Database | `SNITCHDNS_DB_URL` | DB Hostname | Only for `mysql` and `postgres` | | None |
| Database | `SNITCHDNS_DB_DB` | DB Name | Only for `mysql` and `postgres` | | None |
| Data | `SNITCHDNS_DATA_PATH` | Data path to store user files, must be writable by the user running the server. | No | Absolute path to location | `./data` folder within this repo. |
| Session | `SNITCHDNS_SECRET_KEY` | Secret Key used to encrypt sessions | Yes | Random value | | |

## Configuration Settings

To configure SnitchDNS settings, use CLI:

```
./venv.sh flask settings set --name <setting_name> --value <setting_value>
```

### Supported Settings

**DNS Settings**

| Name | Description |
| ---- | ----------- |
| `dns_base_domain` | The base domain under which log privileged users will be restricted to (_%USERNAME%.basedomain.com_). This is required even if you don't plan to have low-privileged users. |
| `dns_daemon_bind_ip` | The IP address where the daemon will bind to - If in doubt use `0.0.0.0` |
| `dns_daemon_bind_port` | The port the daemon will bind to - Only unprivileged ports are allowed (`>= 1024`) in order to prevent users running SnitchDNS under `root` |
| `dns_daemon_start_everyone` | Whether to allow low privileged users to start (not stop) the daemon if it's not running |
| `forward_dns_address` | Comma-separated list of third party DNS server. For example, in order to use Google's DNS servers use `8.8.8.8,8.8.4.4` |
| `forward_dns_enabled` | Whether DNS forwarding is enabled / `true/false` |

**LDAP Settings**

| Name | Description |
| ---- | ----------- |
| `ldap_enabled` | Whether the LDAP authentication is enabled / `true/false` |
| `ldap_ssl` | Whether to use SSL to connect to the LDAP server / `true/false` |
| `ldap_host` | Host |
| `ldap_base_dn` | Base Domain |
| `ldap_domain` | Domain |
| `ldap_bind_user` | Read-only service account username |
| `ldap_bind_pass` | Read-only service account password |
| `ldap_mapping_username` | Which attribute to use as the username / `sAMAccountName` (Required) |
| `ldap_mapping_fullname` | Which attribute to use as the full name / `givenName` (Required) |
| `ldap_mapping_email` | Which attribute to use as the e-mail / `mail` (Optional) |

**Notifications**

| Name | Description |
| ---- | ----------- |
| `slack_enabled` | Whether Slack Webhook notifications are enabled / `true/false` |
| `teams_enabled` | Whether Teams Webhook notifications are enabled / `true/false` |
| `smtp_enabled` | Whether e-mail notifications are enabled / `true/false` |
| `smtp_host` | Host |
| `smtp_port` | Port |
| `smtp_tls` | SMTP TLS / SMTP  |
| `smtp_user` | Username |
| `smtp_pass` | Password |
| `smtp_sender` | Sender's e-mail address |
| `webpush_enabled` | Whether Web Push notifications are enabled / `true/false`  |
| `vapid_private` | VAPID Private Key - https://web-push-codelab.glitch.me/ |
| `vapid_public` | Vapid Public Key - https://web-push-codelab.glitch.me/ |

**Password Complexity**

| Name | Description |
| ---- | ----------- |
| `pwd_min_length` | Minimum Length |
| `pwd_min_lower` | Minimum Lower Characters |
| `pwd_min_upper` | Minimum Upper Characters |
| `pwd_min_digits` | Minimum Digit Characters |
| `pwd_min_special` | Minimum Special Characters |

**CSV Logging**

| Name | Description |
| ---- | ----------- |
| `csv_logging_enabled` | Whether CSV logging is enabled / `true/false` |
| `csv_logging_file` | Absolute path of the output CSV file |

**MISC**

| Name | Description |
| ---- | ----------- |
| `update_url` | Location of `version.py` to check against - default value is `https://api.github.com/repos/ctxis/SnitchDNS/contents/app/version.py` |

## DNS Record Properties

Below are the supported DNS Records and their properties, for usage in CLI and/or API.

Properties per Type

| DNS Type | Properties | Property Type |
| -------- | ---------- | ------------- |
| `A` | | |
| | `address` | `string` |
| `AAAA` | | |
| | `address` | `string` |
| `AFSDB` | | |
| | `hostname` | `string` |
| | `subtype` | `integer` |
| `CNAME` | | |
| | `name` | `string` |
| `DNAME` | | |
| | `name` | `string` |
| `HINFO` | | |
| | `cpu` | `string` |
| | `os` | `string` |
| `MX` | | |
| | `name` | `string` |
| | `preference` | `integer` |
| `NAPTR` | | |
| | `order` | `integer` |
| | `preference` | `integer` |
| | `flags` | `string` |
| | `service` | `string` |
| | `regexp` | `string` |
| | `replacement` | `string` |
| `NS` | | |
| | `name` | `string` |
| `PTR` | | |
| | `name` | `string` |
| `RP` | | |
| | `mbox` | `string` |
| | `txt` | `string` |
| `SOA` | | |
| | `mname` | `string` |
| | `rname` | `string` |
| | `serial` | `integer` |
| | `refresh` | `integer` |
| | `retry` | `integer` |
| | `expire` | `integer` |
| | `minimum` | `integer` |
| `SPF` | | |
| | `data` | `string` |
| `SRV` | | |
| | `target` | `string` |
| | `port` | `integer` |
| | `priority` | `integer` |
| | `weight` | `integer` |
| `SSHFP` | | |
| | `algorithm` | `integer` |
| | `fingerprint_type` | `integer` |
| | `fingerprint` | `string` |
| `TSIG` | | |
| | `algorithm` | `string` |
| | `timesigned` | `integer` |
| | `fudge` | `integer` |
| | `original_id` | `integer` |
| | `mac` | `string` |
| | `other_data` | `string` |
| `TXT` | | |
| | `data` | `string` |

## IP Restrictions

Below is an explanation on how the record IP restrictions work:

* No restrictions exist.
  * Allow all traffic.
* Only Allow rules exist.
  * Source IP must be within the allowed range in order to be allowed.
* Only Block rules exist.
  * All traffic is allowed except IPs within the block range.
* Both Allow and Block rules exist.
  * If Source IP is within the Block rules, query is blocked (Block takes precedence over Allow).
  * If Source IP is not within the Block rules, it must be within the Allow rules in order to be allowed.

## Bind9 Forwarding

**Warning** - If you use Bind9to forward DNS queries you will lose the originating IP address and all the source IPs will be `127.0.0.1`.

If you don't want to expose SnitchDNS directly to the internet, you can put it behind Bind9 using the following configuration:

```
options {
        directory "/var/cache/bind";

        forwarders {
           SNITCH_DNS_IP_ADDRESS port 2024; # If it's listening on 53 you can ommit "port 2024".
        };
        forward only;

        dnssec-validation no;

        auth-nxdomain no;    # conform to RFC1035

        allow-transfer {
            none;
        };
};
```

## Cloud Hosting

If you wish to host SnitchDNS on the cloud or a dedicated server (any provider), simply point the nameserver of your (sub)domain to the instance running SnitchDNS.