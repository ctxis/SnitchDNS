from app.lib.base.instance.base_instance import BaseInstance


class WebPushSubscription(BaseInstance):
    @property
    def user_id(self):
        return self.item.user_id

    @user_id.setter
    def user_id(self, value):
        self.item.user_id = value

    @property
    def endpoint(self):
        return self.item.endpoint

    @endpoint.setter
    def endpoint(self, value):
        self.item.endpoint = value

    @property
    def key(self):
        return self.item.key

    @key.setter
    def key(self, value):
        self.item.key = value

    @property
    def authsecret(self):
        return self.item.authsecret

    @authsecret.setter
    def authsecret(self, value):
        self.item.authsecret = value
