from app.lib.models.dns import DNSZoneNotificationModel
from app.lib.notifications.instances.zone_notification import DNSNotification


class NotificationManager:
    @property
    def providers(self):
        return self.__providers

    def __init__(self):
        self.__providers = {}

    def add_provider(self, name, provider):
        self.__providers[name] = provider

    def has_enabled_providers(self):
        for name, provider in self.__providers.items():
            if provider.enabled:
                return True
        return False

    def get_provider(self, name):
        return self.__providers[name] if name in self.__providers else None

    def get_enabled_providers(self):
        providers = {}
        for name, provider in self.__providers.items():
            if provider.enabled:
                providers[name] = provider
        return providers

    def __get_dns_notification(self, id=None, dns_zone_id=None, email=None, webpush=None):
        query = DNSZoneNotificationModel.query

        if id is not None:
            query = query.filter(DNSZoneNotificationModel.id == id)

        if dns_zone_id is not None:
            query = query.filter(DNSZoneNotificationModel.dns_zone_id == dns_zone_id)

        if email is not None:
            query = query.filter(DNSZoneNotificationModel.email == email)

        if webpush is not None:
            query = query.filter(DNSZoneNotificationModel.webpush == webpush)

        return query.all()

    def get_dns_notification(self, id):
        results = self.__get_dns_notification(id=id)
        if len(results) == 0:
            return False

        return self.__load_dns_notification(results[0])

    def get_dns_zone_notifications(self, dns_zone_id):
        results = self.__get_dns_notification(dns_zone_id=dns_zone_id)
        if len(results) == 0:
            return False

        return self.__load_dns_notification(results[0])

    def __load_dns_notification(self, item):
        return DNSNotification(item)

    def create_dns_zone_notification(self, dns_zone_id=None):
        item = DNSNotification(DNSZoneNotificationModel())
        if dns_zone_id is not None:
            item.dns_zone_id = dns_zone_id
        item.save()
        return item

    def get_subscribed(self, email=None, webpush=None):
        results = self.__get_dns_notification(email=email, webpush=webpush)
        items = []
        for result in results:
            items.append(self.__load_dns_notification(result))

        return items
