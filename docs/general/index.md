# SnitchDNS Documentation

* [CSV Import](#csv-import)
* [IP Restrictions](#ip-restrictions)
* [Bind9 Forwarding](#bind9-forwarding)
* [Cloud Hosting](#cloud-hosting)

## CSV Import

CSV File Example

```
"type","domain","d_active","d_exact_match","d_forwarding","d_master","r_id","r_ttl","r_cls","r_type","r_active","r_data"
"zone","www.example.com","1","1","0","0"
"record","www.example.com","","","","","1","10","IN","A","1","address=192.168.0.1"
```

Required fields for a `zone` row: `type, domain, d_active, d_exact_match, d_forwarding, d_master`

Required fields for a `record` row: `type, domain, r_id, r_ttl, r_cls, r_type, r_active, r_data`

`r_id` is the internal primary key of the record ID. If the `r_id` exists for that domain, it will be updated - if not, it will be created.

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