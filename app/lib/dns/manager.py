import ipaddress
from app.lib.models.dns import DNSZoneModel
from app.lib.dns.instances.zone import DNSZone


class DNSManager:
    def get_classes(self):
        # These are taken from dnslib -> /dnslib/dns.py
        data = {1: 'IN', 2: 'CS', 3: 'CH', 4: 'Hesiod', 254: 'None', 255: '*'}
        items = list(data.values())
        items.sort()
        return items
    
    def get_types(self):
        # These are taken from dnslib -> /dnslib/dns.py
        data = {1: 'A', 2: 'NS', 5: 'CNAME', 6: 'SOA', 12: 'PTR', 13: 'HINFO', 15: 'MX', 16: 'TXT', 17: 'RP',
                18: 'AFSDB', 24: 'SIG', 25: 'KEY', 28: 'AAAA', 29: 'LOC', 33: 'SRV', 35: 'NAPTR', 36: 'KX', 37: 'CERT',
                38: 'A6', 39: 'DNAME', 41: 'OPT', 42: 'APL', 43: 'DS', 44: 'SSHFP', 45: 'IPSECKEY', 46: 'RRSIG',
                47: 'NSEC', 48: 'DNSKEY', 49: 'DHCID', 50: 'NSEC3', 51: 'NSEC3PARAM', 52: 'TLSA', 55: 'HIP', 59: 'CDS',
                60: 'CDNSKEY', 61: 'OPENPGPKEY',99: 'SPF', 249: 'TKEY', 250: 'TSIG', 251: 'IXFR', 252: 'AXFR',
                255: 'ANY', 256: 'URI', 257: 'CAA', 32768: 'TA', 32769: 'DLV'}
        items = list(data.values())
        items.sort()
        return items

    def is_valid_ip_address(self, ip):
        try:
            obj = ipaddress.ip_address(ip)
        except ValueError:
            return False

        return True

    def __get(self, id=None, domain=None, ttl=None, rclass=None, type=None, address=None):
        query = DNSZoneModel.query

        if id is not None:
            query = query.filter(DNSZoneModel.id == id)

        if domain is not None:
            query = query.filter(DNSZoneModel.domain == domain)

        if ttl is not None:
            query = query.filter(DNSZoneModel.ttl == ttl)

        if rclass is not None:
            query = query.filter(DNSZoneModel.rclass == rclass)

        if type is not None:
            query = query.filter(DNSZoneModel.type == type)

        if address is not None:
            query = query.filter(DNSZoneModel.address == address)

        return query.first()

    def get_zone(self, dns_zone_id):
        item = self.__get(id=dns_zone_id)
        if not item:
            return False

        return DNSZone(item)

    def create_zone(self):
        item = DNSZone(DNSZoneModel())
        item.save()
        return item

    def save(self, zone, domain, ttl, rclass, type, address):
        zone.domain = self.__fix_domain(domain)
        zone.ttl = ttl
        zone.rclass = rclass
        zone.type = type
        zone.address = address
        zone.save()

        return True

    def __fix_domain(self, domain):
        return domain.rstrip('.') + '.'

    def get_all_zones(self):
        results = DNSZoneModel.query.order_by(DNSZoneModel.domain).all()

        zones = []
        for result in results:
            zones.append(DNSZone(result))

        return zones

    def find_zone(self, domain=None, type=None, rclass=None):
        item = self.__get(domain=domain, type=type, rclass=rclass)
        if not item:
            return False

        return DNSZone(item)
