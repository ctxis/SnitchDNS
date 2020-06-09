from app.lib.base.instance.base_instance import BaseInstance


class DNSNotification(BaseInstance):
    @property
    def dns_zone_id(self):
        return self.item.dns_zone_id

    @dns_zone_id.setter
    def dns_zone_id(self, value):
        self.item.dns_zone_id = value

    @property
    def email(self):
        return self.item.email

    @email.setter
    def email(self, value):
        self.item.email = value

    @property
    def webpush(self):
        return self.item.webpush

    @webpush.setter
    def webpush(self, value):
        self.item.webpush = value

    def has(self, type):
        if type in ['email', 'emails']:
            return self.email
        elif type == 'webpush':
            return self.webpush
        return False
