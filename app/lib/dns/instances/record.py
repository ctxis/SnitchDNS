from app.lib.dns.base_instance import BaseDNSInstance


class DNSRecord(BaseDNSInstance):
    @property
    def dns_zone_id(self):
        return self.item.dns_zone_id

    @dns_zone_id.setter
    def dns_zone_id(self, value):
        self.item.dns_zone_id = value

    @property
    def ttl(self):
        return self.item.ttl

    @ttl.setter
    def ttl(self, value):
        self.item.ttl = value

    @property
    def rclass(self):
        return self.item.rclass

    @rclass.setter
    def rclass(self, value):
        self.item.rclass = value

    @property
    def type(self):
        return self.item.type

    @type.setter
    def type(self, value):
        self.item.type = value

    @property
    def data(self):
        return self.item.data

    @data.setter
    def data(self, value):
        self.item.data = value

    @property
    def active(self):
        return self.item.active

    @active.setter
    def active(self, value):
        self.item.active = value
