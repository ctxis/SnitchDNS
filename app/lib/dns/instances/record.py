from app.lib.dns.base_instance import BaseDNSInstance
import json


class DNSRecord(BaseDNSInstance):
    def __init__(self, item):
        super().__init__(item)
        self.__load_properties()

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
        self.__load_properties()

    @property
    def active(self):
        return self.item.active

    @active.setter
    def active(self, value):
        self.item.active = value

    def __load_properties(self):
        self.__data_properties = json.loads(self.data) if self.data is not None else {}

    def property(self, name, default=None):
        return self.__data_properties[name] if name in self.__data_properties else default

    def properties(self):
        return self.__data_properties
