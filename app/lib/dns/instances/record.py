from app.lib.base.instance.base_instance import BaseInstance
import json


class DNSRecord(BaseInstance):
    def __init__(self, item):
        super().__init__(item)
        self._uses_cache = True

        self.__match_count = 0
        self.__load_properties()
        self.__load_conditional_properties()

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

    @property
    def match_count(self):
        return self.__match_count

    @match_count.setter
    def match_count(self, value):
        self.__match_count = value

    def __load_properties(self):
        self.__data_properties = json.loads(self.data) if self.data is not None else {}

    def conditional_properties(self):
        return self.__conditional_data_properties

    @property
    def has_conditional_responses(self):
        return self.item.has_conditional_responses

    @has_conditional_responses.setter
    def has_conditional_responses(self, value):
        self.item.has_conditional_responses = value

    @property
    def conditional_data(self):
        return self.item.conditional_data

    @conditional_data.setter
    def conditional_data(self, value):
        self.item.conditional_data = value
        self.__load_conditional_properties()

    @property
    def conditional_count(self):
        return self.item.conditional_count

    @conditional_count.setter
    def conditional_count(self, value):
        self.item.conditional_count = value

    @property
    def conditional_limit(self):
        return self.item.conditional_limit

    @conditional_limit.setter
    def conditional_limit(self, value):
        self.item.conditional_limit = value

    @property
    def conditional_reset(self):
        return self.item.conditional_reset

    @conditional_reset.setter
    def conditional_reset(self, value):
        self.item.conditional_reset = value

    def __load_conditional_properties(self):
        self.__conditional_data_properties = json.loads(self.conditional_data) if self.conditional_data is not None else {}

    def conditional_property(self, name, default=None):
        return self.__conditional_data_properties[name] if name in self.__conditional_data_properties else default

    def property(self, name, default=None, conditional=False):
        if conditional:
            return self.__conditional_data_properties[name] if name in self.__conditional_data_properties else default
        return self.__data_properties[name] if name in self.__data_properties else default

    def properties(self):
        return self.__data_properties
