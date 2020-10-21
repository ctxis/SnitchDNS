from app.lib.base.instance.base_instance import BaseInstance


class DNSZoneTag(BaseInstance):
    def __init__(self, item):
        super().__init__(item)

    @property
    def dns_zone_id(self):
        return self.item.dns_zone_id

    @dns_zone_id.setter
    def dns_zone_id(self, value):
        self.item.dns_zone_id = value

    @property
    def tag_id(self):
        return self.item.tag_id

    @tag_id.setter
    def tag_id(self, value):
        self.item.tag_id = value
