from app.lib.base.instance.base_instance import BaseInstance


class NotificationLog(BaseInstance):
    @property
    def subscription_id(self):
        return self.item.subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        self.item.subscription_id = value

    @property
    def sent_at(self):
        return self.item.sent_at

    @sent_at.setter
    def sent_at(self, value):
        self.item.sent_at = value
