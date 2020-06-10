from app.lib.base.instance.base_instance import BaseInstance


class NotificationType(BaseInstance):
    @property
    def name(self):
        return self.item.name

    @name.setter
    def name(self, value):
        self.item.name = value

    @property
    def description(self):
        return self.item.description

    @description.setter
    def description(self, value):
        self.item.description = value
