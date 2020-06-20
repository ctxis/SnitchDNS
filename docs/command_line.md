# Command Line

## How to run

All commands have to be executed within the virtual environment (venv). For this reason `venv.sh` was created, so commands can be executed as:

```
./<path-to-snitch>/venv.sh flask <your-command>
```

## Snitch Environment

### cron

The cron runs every minute and is responsible for tasks such as sending notifications. If you need to trigger it manually, simply run:

```
cron
```

### crontab

The crontab is responsible for executing the `cron` command (see above) every minute. This is added via https://github.com/frostming/flask-crontab

### env

This command is used by the front-end to determine if it is running under a virtual environment. This command simply returns `OK`

### snitch_daemon

Start SnitchDNS daemon.

```
snitch_daemon --bind-ip <ip> --bind-port <port>
```

If you need to bind a privileged port `< 1024` you'll need to run this as sudo.

### snitch_start

This simply invokes the `snitch_daemon` command without having to pass IP/Port arguments, and is used in the `systemd` startup.

### snitchdb

Runs migration/seeding functions, like populating the notification types. This command must be executed after every installation/upgrade.

## Snitch Management

### settings

#### list

Will list all current settings:

```
settings list
```

#### set

Set a configuration setting:

```
settings set --name <setting_name> --value <setting_value>
```

##### Supported Settings

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

#### get

Retrieve a setting.

```
settings get --name <setting_name> --default <default_value>
```

The `--default` parameter is optional, if not defined unmatched settings will return an empty string.

### users

#### list

List all users

```
users list
```

#### add

Add a new user

```
users add <options>
```

Supported parameters

```
--username TEXT               Username  [required]
--password TEXT               Password - If defined in the CLI it should be a bcrypt hash, otherwise you will be prompted to enter it.
--full_name TEXT              Full Name  [required]
--email TEXT                  E-Mail  [required]
--active [yes|no|true|false]  User will be active  [required]
--admin [yes|no|true|false]   User will be an administrator  [required]
--ldap [yes|no|true|false]    User will be authenticated against the LDAP
                              server (if configured)  [required]
--create_zone                 Whether a master zone fill be created for the user
```

#### update

Update existing user. Only the passed parameters will be updated, for instance if you only defined `--admin` and not `--active` only the former will be updated.

```
users update <options>
```

Supported parameters

```
--username TEXT               Username  [required]
--update_password             Whether to update the password. This is used in combination with --password.
--password TEXT               Password - If defined in the CLI it should be a bcrypt hash, otherwise you will be prompted to enter it.
--full_name TEXT              Full Name
--email TEXT                  E-Mail
--active [yes|no|true|false]  User will be active
--admin [yes|no|true|false]   User will be an administrator
--ldap [yes|no|true|false]    User will be authenticated against the LDAP server (if configured)
```

### zones

#### list

List all existing zones

```
zones list
```

#### add

Create a new zone

```
zones add <parameters>
```

Supported parameters

```
--domain TEXT      Domain  [required]
--user_id INTEGER  User ID to own the domain  [required]
--active           Domain will be active
--exact_match      Domain will have to be exact match to respond to queries
--forwarding       Unmatched records will be forwarded (if forwarding is enabled)
```

#### update

Update existing zone. Only passed parameters will be updated.

```
zones update <parameters>
```

Supported parameters

```
--domain TEXT                     Domain  [required]
--active [yes|no|true|false]      Domain will be active
--exact_match [yes|no|true|false] Domain will have to be exact match to respond to queries
--forwarding [yes|no|true|false]  Unmatched records will be forwarded (if forwarding is enabled)
```

#### delete

Delete existing zone.

```
zones delete --domain <domain>
```

### records

#### list

List all records for a domain.

```
records list --domain <domain>
```

#### add

Create new record.

```
records add <parameters>
```

Supported parameters

```
--domain TEXT                   Domain  [required]
--type                          Record Type  [required]
--cls [ANY|CH|CS|HS|IN]         Record Class
--ttl INTEGER                   Record Type  [required]
--active                        Record will be active
--property <name/value>...      [required]
```

The `--property` parameter can appear multiple times, depending on the supported properties. For example, to add an `MX` record you would use the following command:

```
records add --type MX --cls IN --ttl 3600 --active --property name mail.example.com --property preference 10
```

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

#### update

Update existing record.

```
records update <parameters>
```

Supported parameters

```
--domain TEXT                   Domain  [required]
--id INTEGER                    Record ID to update.  [required]
--type                          Record Type
--cls [ANY|CH|CS|HS|IN]         Record Class
--ttl INTEGER                   Record Type
--active [yes|no|true|false]    Record will be active
--property <name/value>...
```

#### delete

Delete domain record

```
records delete --domain <domain> --type <type> --id <record-id>
```

You only have to specify either `--type` or `--id`, not both.

### restrictions

#### list

List IP restrictions for a domain

```
restrictions list --domain <domain>
```

#### add

Add an IP restriction

```
restrictions add <parameters>
```

Supported parameters

```
--domain TEXT         Domain  [required]
--iprange TEXT        Restriction IP or Range. Use 0.0.0.0 to match all addresses  [required]
--type [allow|block]  Restriction Type  [required]
--enabled             Restriction will be enabled
```

#### update

Update an existing restriction

```
restrictions update <parameters>
```

Supported parameters:

```
--domain TEXT                  Domain  [required]
--id INTEGER                   Restriction ID to update.  [required]
--iprange TEXT                 Restriction IP or Range. Use 0.0.0.0 to match all addresses
--type [allow|block]           Restriction Type
--enabled [yes|no|true|false]  Restriction will be enabled
```

#### delete

Delete a restriction

```
restrictiond delete --domain <domain> --iprange <range> --id <restriction-id>
```

You only have to specify either `--iprange` or `--id`, not both.