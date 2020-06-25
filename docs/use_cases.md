# SnitchDNS Use Cases

# DNS Server

Use it as a basic DNS Server to respond or forward queries in your local network.

# DNS Forwarding

I never thought I'd write this sentence, but have you ever wondered what DNS queries your oven is making? Using SnitchDNS as a DNS Forwarder you can easily monitor all requests, and block them with a single click.

# Ad-Blocking

SnitchDNS is not here to replace, or even compete with existing ad-blocking solutions. But if you wanted to, it can also be used to block requests against specific domains. Using the CSV import functionality you can easily import all the domains and records you wish to block. 

# Let's Encrypt DNS-01 Challenge

With the Swagger 2.0 API (or CLI), use the DNS-01 Challenge type to re-new your Let's Encrypt certificate - https://letsencrypt.org/docs/challenge-types/#dns-01-challenge

# DNS Tunnel

As all the DNS queries are logged, it can also be used as a DNS Tunnel and assist with egress of data.

This was actually how SnitchDNS was born and the reason why it supports low privileged users.

When you install SnitchDNS, you will have to set the `base domain`. This is effectively the base domain that the low privileged users will use. It's easier to explain with an example.

* Install SnitchDNS and set its base domain to `snitch.example.com`
  * This means that SnitchDNS **must** be listening for queries on that domain.
* You create a low privileged user with the username `peter.parker`
* Automatically, they will be assigned `peterparker.snitch.example.com` as their `base` (or parent) domain.
  * Now, this user has total control over any subdomains under that parent domain.
  * This means that if they ping `hello.world.peterparker.snitch.example.com` it will appear in their logs. 
  
If you are a security consultancy that wishes to offer your employees a DNS Tunnel, SnitchDNS is ideal for you.

It is very similar to Burp Collaborator, but is self-hosted and you have user segregation/management.

# Red Teams

It can also be used for Red Team engagements:

* Phishing / Sandboxes
  * Before an e-mail lands into an inbox it may be scanned by sandboxes and usually those resolve a domain but never visit it. You can now log all those IP addresses and block them from resolving your C2 domain.
* Restrict domain resolutions only to the IP range of your client, minimising the risk of accidentally serving payloads to third-parties.
* Use it as a [DNS Tunnel](#dns-tunnel) and egress data. 
* Easily deploy using Ansible, and manage it via CLI (or API):

    ```
    # Create a domain
    ./venv.sh flask zones add --domain www.myc2domain.com --user_id 1 --active
    
    # Create an A record for 123.123.123.123
    ./venv.sh flask records add --domain www.myc2domain.com --type A --cls IN --ttl 60 --active --property address 123.123.123.123
  
    # Only allow requests from 88.88.88.0/24
    ./venv.sh flask restrictions add --domain www.myc2domain.com --iprange 88.88.88.0/24 --type allow --enabled
    ```
* Integrate with SIEM solutions.

It's currently on the roadmap to enable different responses depending on the source IP, for example "Region X resolves to A" and "Region Y resolved to B". 

# Misc

Try adding a domain served by SnitchDNS as a link into an e-mail and see how many times it is scanned before/after it reaches an inbox (spoiler alert: a lot!).