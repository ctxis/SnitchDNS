from app.lib.base.instance.base_instance import BaseInstance


class AuthType(BaseInstance):
    @property
    def name(self):
        return self.item.name

    @name.setter
    def name(self, value):
        self.item.name = value
