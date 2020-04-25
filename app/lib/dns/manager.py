import ipaddress
import re
from app.lib.models.dns import DNSZoneModel, DNSQueryLogModel
from app.lib.dns.instances.zone import DNSZone
from app.lib.dns.instances.query_log import DNSQueryLog
from app import db
from sqlalchemy import func


class DNSManager:
    def __init__(self, settings):
        self.settings = settings

    @property
    def forwarders(self):
        return self.settings.get_list('forward_dns_address')

    @property
    def is_forwarding_enabled(self):
        return True if int(self.settings.get('forward_dns_enabled', 0)) == 1 else False

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

    def __get(self, id=None, domain=None, ttl=None, rclass=None, type=None, address=None, active=None, exact_match=None,
              user_id=None, full_domain=None, base_domain=None):
        query = DNSZoneModel.query

        if id is not None:
            query = query.filter(DNSZoneModel.id == id)

        if domain is not None:
            query = query.filter(func.lower(DNSZoneModel.domain) == domain.lower())

        if ttl is not None:
            query = query.filter(DNSZoneModel.ttl == ttl)

        if rclass is not None:
            query = query.filter(DNSZoneModel.rclass == rclass)

        if type is not None:
            query = query.filter(DNSZoneModel.type == type)

        if address is not None:
            query = query.filter(DNSZoneModel.address == address)

        if active is not None:
            query = query.filter(DNSZoneModel.active == active)

        if exact_match is not None:
            query = query.filter(DNSZoneModel.exact_match == exact_match)

        if user_id is not None:
            query = query.filter(DNSZoneModel.user_id == user_id)

        if full_domain is not None:
            query = query.filter(func.lower(DNSZoneModel.full_domain) == full_domain.lower())

        if base_domain is not None:
            query = query.filter(func.lower(DNSZoneModel.base_domain) == base_domain.lower())

        return query.first()

    def get_zone(self, dns_zone_id):
        item = self.__get(id=dns_zone_id)
        if not item:
            return False

        return self.__load_zone(item)

    def __load_zone(self, item):
        zone = DNSZone(item)
        return zone

    def create_zone(self):
        item = DNSZone(DNSZoneModel())
        item.save()
        return item

    def create_query_log(self):
        item = DNSQueryLog(DNSQueryLogModel())
        item.save()
        return item

    def save(self, user_id, zone, domain, base_domain, ttl, rclass, type, address, active, exact_match):
        zone.domain = self.__fix_domain(domain)
        zone.base_domain = self.__fix_base_domain(base_domain)
        zone.full_domain = zone.domain + zone.base_domain
        zone.ttl = ttl
        zone.rclass = rclass
        zone.type = type
        zone.address = address
        zone.active = active
        zone.exact_match = exact_match
        zone.user_id = user_id
        zone.save()

        return True

    def __fix_domain(self, domain):
        return domain.rstrip('.')

    def __fix_base_domain(self, domain):
        return domain.rstrip('.') + '.'

    def get_all_zones(self):
        results = DNSZoneModel.query.order_by(DNSZoneModel.domain).all()

        zones = []
        for result in results:
            zones.append(self.__load_zone(result))

        return zones

    def get_user_zones(self, user_id):
        results = DNSZoneModel.query.filter(DNSZoneModel.user_id == user_id).order_by(DNSZoneModel.domain).all()

        zones = []
        for result in results:
            zones.append(self.__load_zone(result))

        return zones

    def find_zone(self, domain=None, type=None, rclass=None):
        item = self.__get(full_domain=domain, type=type, rclass=rclass, active=True)
        if not item:
            return False

        return self.__load_zone(item)

    def get_all_logs(self):
        results = DNSQueryLogModel.query.order_by(DNSQueryLogModel.id).all()

        logs = []
        for result in results:
            logs.append(DNSQueryLog(result))

        return logs

    def get_log_filters(self):
        classes = db.session.query(DNSQueryLogModel.rclass).group_by(DNSQueryLogModel.rclass).order_by(DNSQueryLogModel.rclass)
        types = db.session.query(DNSQueryLogModel.type).group_by(DNSQueryLogModel.type).order_by(DNSQueryLogModel.type)
        source_ips = db.session.query(DNSQueryLogModel.source_ip).group_by(DNSQueryLogModel.source_ip).order_by(DNSQueryLogModel.source_ip)

        return {
            'classes': classes,
            'types': types,
            'source_ips': source_ips
        }

    def get_base_domain(self):
        return self.settings.get('dns_base_domain', '')

    def get_user_base_domain(self, username):
        dns_base_domain = self.__fix_domain(self.get_base_domain()).lstrip('.')
        # Keep only letters, digits, underscore.
        username = re.sub(r'\W+', '', username)
        return '.' + username + '.' + dns_base_domain

    def duplicate_domain_exists(self, dns_zone_id, domain, base_domain):
        return DNSZoneModel.query.filter(
            DNSZoneModel.id != dns_zone_id,
            DNSZoneModel.domain == domain,
            DNSZoneModel.base_domain == base_domain
        ).count() > 0

    def can_access_zone(self, dns_zone_id, user_id, is_admin=False):
        if is_admin:
            # SuperUser
            return True
        return self.__get(id=dns_zone_id, user_id=user_id) is not None
