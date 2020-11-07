# ![](docs/images/icon32.png) SnitchDNS

SnitchDNS is database driven (basic) DNS server built using [Twisted](https://github.com/twisted/twisted)

Ideal for Red Team infrastructure, bug bounties, ad-blocking, DNS tunnels, and more.

* [Basic Feature](#basic-features)
* [Use Cases](#use-cases)
* [Installation](#installation)
* [Documentation](#documentation)
  * [Screenshots](docs/general/screenshots.md)
* [Limitations](#limitations)
* [Contributing](#contributing)
* [Security](#security)
* [Credits](#credits)

## Basic Features

* Database Driven.
  * Changes are reflected immediately on each DNS request.
  * Supported DBMS:
    * SQLite
    * MySQL / MariaDB
    * Postgres
* DNS Server
  * Support for common DNS Records.
    * `A, AAAA, AFSDB, CNAME, DNAME, HINFO, MX, NAPTR, NS, PTR, RP, SOA, SPF, SRV, SSHFP, TSIG, TXT`.
  * Catch-All Domains.
    * Ability to match any subdomain (no matter the depth) to a specific parent domain, for instance *.hello.example.com.
  * Unmatched Record Forwarding.
    * Functionality to intercept specific queries (ie only `A` and `CNAME`) and forward all other records to a third-party DNS server (ie Google).
* IP Rules
  * Configure Allow/Block rules per domain.
* Notifications. Receive a notification when a domain is resolved, via:
  * E-mail
  * Web Push
  * Slack Webhooks
  * Microsoft Teams Webhooks
* User Management
  * Multi-User support
    * Each user is given their own subdomain to use.
  * LDAP Support
  * Two Factor Authentication
  * Password Complexity Management
* Logging
  * All DNS queries are logged, whether they have been matched or not.
* Swagger 2.0 API
* Deployment
  * Ansible scripts for Ubuntu 18.04 / 20.04
  * Docker
  * CLI support for zone, record, user, and settings management.
  * CSV Export/Import 
  
## Use Cases

SnitchDNS can be used for:

* A DNS Forwarding Server - Allowing you to monitor all requests via a Web GUI.
* Red Teams - Implement IP restrictions to block sandboxes, monitor phishing domain resolutions and e-mails, and restrict access to known IP ranges.
* DNS Tunnel - Log all DNS requests and egress data.
* Let's Encrypt DNS Challenge, using the API or the CLI interface.
* Ad-blocking
* Canary Tokens

For more details on scenarios please see the [Use Cases Document](docs/use_cases.md)

## Dependencies

* Python 3.6+

## Installation

* [The Ansible Way](docs/setup/ansible.md)
* [The Manual Way](docs/setup/manual.md)
* [The Docker Way](docs/setup/docker.md)

## Documentation

For general documentation [see here](docs/general/index.md)

### Screenshots

For screenshots [see here](docs/general/screenshots.md)

## Limitations

* Caching has not been implemented, which means this isn't suitable for environments with hundreds of DNS requests per minute.

## Contributing

If you wish to contribute pull requests, feature requests, and bug reports - feel free to raise an issue (especially before you start writing code). 

## Security

If you identify any security vulnerabilities within SnitchDNS, for the time being please contact me on twitter - [@sadreck](https://twitter.com/sadreck)

## Credits

**UI**
* Theme from [Bootswatch](https://bootswatch.com/)
* Images from [Freepik](http://www.freepik.com/)

**Development**
* Lambros Zannettos | [@\_C960\_](https://twitter.com/_C960_) - For his help with writing the Dockerfile.