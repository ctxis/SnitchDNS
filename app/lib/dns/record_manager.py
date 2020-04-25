from app.lib.models.dns import DNSRecordModel
from app.lib.dns.instances.record import DNSRecord


class DNSRecordManager:
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
                60: 'CDNSKEY', 61: 'OPENPGPKEY', 99: 'SPF', 249: 'TKEY', 250: 'TSIG', 251: 'IXFR', 252: 'AXFR',
                255: 'ANY', 256: 'URI', 257: 'CAA', 32768: 'TA', 32769: 'DLV'}
        items = list(data.values())
        items.sort()
        return items

    def __get(self, id=None, dns_zone_id=None, ttl=None, rclass=None, type=None, data=None, active=None):
        query = DNSRecordModel.query

        if id is not None:
            query = query.filter(DNSRecordModel.id == id)

        if dns_zone_id is not None:
            query = query.filter(DNSRecordModel.dns_zone_id == dns_zone_id)

        if ttl is not None:
            query = query.filter(DNSRecordModel.ttl == ttl)

        if rclass is not None:
            query = query.filter(DNSRecordModel.rclass == rclass)

        if type is not None:
            query = query.filter(DNSRecordModel.type == type)

        if data is not None:
            query = query.filter(DNSRecordModel.data == data)

        if active is not None:
            query = query.filter(DNSRecordModel.active == active)

        return query.all()

    def get(self, dns_record_id, dns_zone_id=None):
        results = self.__get(id=dns_record_id, dns_zone_id=dns_zone_id)
        if len(results) == 0:
            return False

        return self.__load(results[0])

    def __load(self, item):
        return DNSRecord(item)

    def create(self):
        item = DNSRecord(DNSRecordModel())
        item.save()
        return item

    def save(self, record, dns_zone_id, ttl, rclass, type, data, active):
        record.dns_zone_id = dns_zone_id
        record.ttl = ttl
        record.rclass = rclass
        record.type = type
        record.data = data
        record.active = active

        record.save()

        return True

    def get_zone_records(self, dns_zone_id):
        results = self.__get(dns_zone_id=dns_zone_id)

        records = []
        for result in results:
            records.append(self.__load(result))

        return records

    def can_access(self, dns_zone_id, dns_record_id, is_admin=False):
        if is_admin:
            return True

        record = self.__get(id=dns_record_id, dns_zone_id=dns_zone_id)
        return len(record) > 0

    def find(self, dns_zone_id, rclass, type):
        results = self.__get(dns_zone_id=dns_zone_id, rclass=rclass, type=type)
        if len(results) == 0:
            return False

        return self.__load(results[0])
