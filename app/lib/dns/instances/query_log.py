from app.lib.base.instance.base_instance import BaseInstance


class DNSQueryLog(BaseInstance):
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
    def cls(self):
        return self.item.cls

    @cls.setter
    def cls(self, value):
        self.item.cls = value

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
    def completed(self):
        return self.item.completed

    @completed.setter
    def completed(self, value):
        self.item.completed = value

    @property
    def data(self):
        return self.item.data

    @data.setter
    def data(self, value):
        self.item.data = value

    @property
    def dns_zone_id(self):
        return self.item.dns_zone_id

    @dns_zone_id.setter
    def dns_zone_id(self, value):
        self.item.dns_zone_id = value

    @property
    def dns_record_id(self):
        return self.item.dns_record_id

    @dns_record_id.setter
    def dns_record_id(self, value):
        self.item.dns_record_id = value

    @property
    def blocked(self):
        return self.item.blocked

    @blocked.setter
    def blocked(self, value):
        self.item.blocked = value
