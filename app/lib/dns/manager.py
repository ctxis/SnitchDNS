import ipaddress


class DNSManager:
    def __init__(self, zones, records, logs, settings):
        self.zone_manager = zones
        self.record_manager = records
        self.logs_manager = logs
        self.settings = settings

    @property
    def forwarders(self):
        return self.settings.get_list('forward_dns_address')

    @property
    def is_forwarding_enabled(self):
        return True if int(self.settings.get('forward_dns_enabled', 0)) == 1 else False

    def is_valid_ip_address(self, ip):
        try:
            obj = ipaddress.ip_address(ip)
        except ValueError:
            return False

        return True

    def find_zone(self, domain, original_domain):
        zone = self.zone_manager.find(domain)
        if zone is False:
            return False
        elif not zone.active:
            return False

        # Check if it's marked as an 'exact match'.
        # If it is, in order for it to be used here the query.qname (the DNS request that came in) must match the
        # 'full domain' of this result. Because the returned value could be 'hi.bye.contextis.com' and set as
        # 'exact match' but the original query could be for 'greeting.hi.bye.contextis.com'
        if zone.exact_match:
            if zone.full_domain != original_domain:
                return False

        return zone

    def find_all_records(self, zone, cls, type):
        records = self.record_manager.find(zone.id, cls, type)
        if records is False:
            return []
        return records if len(records) > 0 else []
