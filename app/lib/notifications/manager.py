from app.lib.notifications.managers.type_manager import NotificationTypeManager
from app.lib.notifications.managers.subscription_manager import NotificationSubscriptionManager
from app.lib.notifications.managers.log_manager import NotificationLogManager
from app.lib.notifications.managers.provider_manager import NotificationProviderManager
from app.lib.notifications.managers.webpush_manager import WebPushManager
from app.lib.notifications.instances.subscriptions import NotificationSubscriptionCollection


class NotificationManager:
    def __init__(self):
        self.types = NotificationTypeManager()
        self.subscriptions = NotificationSubscriptionManager()
        self.logs = NotificationLogManager()
        self.providers = NotificationProviderManager()
        self.webpush = WebPushManager()

    def save_zone_subscription(self, zone_id, type_name, enabled=None, data=None, last_query_log_id=None):
        type = self.types.get(name=type_name)
        if not type:
            raise Exception("Coding Error: Invalid `type_name` parameter: {0}".format(type_name))

        subscription = self.subscriptions.get(zone_id=zone_id, type_id=type.id)
        if not subscription:
            # Create one.
            subscription = self.subscriptions.create(zone_id=zone_id, type_id=type.id)

        if enabled is not None:
            subscription.enabled = True if enabled else False

        if data is not None:
            subscription.data = data

        if last_query_log_id is not None:
            subscription.last_query_log_id = last_query_log_id

        subscription.save()
        return subscription

    def get_zone_subscriptions(self, zone_id):
        self.create_missing_subscriptions(zone_id)

        collection = NotificationSubscriptionCollection()

        subscriptions = self.subscriptions.all(zone_id=zone_id)
        for subscription in subscriptions:
            type_name = self.types.get_type_name(subscription.type_id)
            if type_name is False:
                continue

            collection.add(type_name, subscription)

        return collection

    def create_missing_subscriptions(self, zone_id):
        # Get all types.
        types = self.types.all()

        # Find types that don't exist.
        for type in types:
            subscription = self.subscriptions.get(zone_id=zone_id, type_id=type.id)
            if subscription:
                continue

            # Create them.
            subscription = self.subscriptions.create(zone_id=zone_id, type_id=type.id)
            subscription.enabled = False
            subscription.data = ''
            subscription.last_query_log_id = 0
            subscription.save()

        return True
