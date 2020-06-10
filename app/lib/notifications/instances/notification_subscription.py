from app.lib.base.instance.base_instance import BaseInstance


class NotificationSubscription(BaseInstance):
    @property
    def zone_id(self):
        return self.item.zone_id

    @zone_id.setter
    def zone_id(self, value):
        self.item.zone_id = value

    @property
    def type_id(self):
        return self.item.type_id

    @type_id.setter
    def type_id(self, value):
        self.item.type_id = value

    @property
    def enabled(self):
        return self.item.enabled

    @enabled.setter
    def enabled(self, value):
        self.item.enabled = value

    @property
    def data(self):
        return self.item.data

    @data.setter
    def data(self, value):
        self.item.data = value
