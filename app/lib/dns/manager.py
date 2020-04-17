from dnslib import QTYPE, CLASS


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
