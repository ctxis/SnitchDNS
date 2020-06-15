from app.lib.base.instance.base_instance import BaseInstance


class DNSZoneRestriction(BaseInstance):
    @property
    def zone_id(self):
        return self.item.zone_id

    @zone_id.setter
    def zone_id(self, value):
        self.item.zone_id = value

    @property
    def ip_range(self):
        return self.item.ip_range

    @ip_range.setter
    def ip_range(self, value):
        self.item.ip_range = value

    @property
    def type(self):
        return self.item.type

    @type.setter
    def type(self, value):
        self.item.type = value

    @property
    def enabled(self):
        return self.item.enabled

    @enabled.setter
    def enabled(self, value):
        self.item.enabled = value
