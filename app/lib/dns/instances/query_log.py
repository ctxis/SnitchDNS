from app.lib.dns.base_instance import BaseDNSInstance


class DNSQueryLog(BaseDNSInstance):
    @property
    def source_ip(self):
        return self.item.source_ip

    @source_ip.setter
    def source_ip(self, value):
        self.item.source_ip = value

    @property
    def domain(self):
        return self.item.domain

    @domain.setter
    def domain(self, value):
        self.item.domain = value

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
    def forwarded(self):
        return self.item.forwarded

    @forwarded.setter
    def forwarded(self, value):
        self.item.forwarded = value

    @property
    def found(self):
        return self.item.found

    @found.setter
    def found(self, value):
        self.item.found = value

    @property
    def resolved_to(self):
        return self.item.resolved_to

    @resolved_to.setter
    def resolved_to(self, value):
        self.item.resolved_to = value

    @property
    def dns_zone_id(self):
        return self.item.dns_zone_id

    @dns_zone_id.setter
    def dns_zone_id(self, value):
        self.item.dns_zone_id = value
