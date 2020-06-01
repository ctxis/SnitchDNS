from app.lib.base.instance.base_instance import BaseInstance


class ApiKey(BaseInstance):
    @property
    def user_id(self):
        return self.item.user_id

    @user_id.setter
    def user_id(self, value):
        self.item.user_id = value

    @property
    def name(self):
        return self.item.name

    @name.setter
    def name(self, value):
        self.item.name = value

    @property
    def apikey(self):
        return self.item.apikey

    @apikey.setter
    def apikey(self, value):
        self.item.apikey = value

    @property
    def enabled(self):
        return self.item.enabled

    @enabled.setter
    def enabled(self, value):
        self.item.enabled = value
