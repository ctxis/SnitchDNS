from twisted.names import dns


# Adapted from https://github.com/ajxchapman/ReServ/blob/5d95950a26e7d97f387872b6d49db2c3b2a8c57e/servers/dns.py#L17
class Record_CAA:
    TYPE = 257
    fancybasename = 'CAA'

    def __init__(self, value, ttl=None):
        self.flags = 0
        self.tag = 'issue'
        self.value = value
        self.ttl = dns.str2time(ttl)

    def encode(self, strio, compDict=None):
        strio.write(bytes([self.flags, len(self.tag)]))
        strio.write(self.tag.encode())
        strio.write(self.value)

    def decode(self, strio, length=None):
        pass

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return '<CAA record=%d %s "%s" ttl=%s>' % (self.flags, self.tag, self.value.decode(), self.ttl)

    __repr__ = __str__
