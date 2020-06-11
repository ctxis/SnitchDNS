from app.lib.base.provider import Provider
from app.lib.api.base import ApiBase
from app.lib.api.definitions.notification_type import NotificationType
from app.lib.api.definitions.notification_subscription import NotificationSubscription
import re


class ApiNotifications(ApiBase):
    def providers(self):
        provider = Provider()
        notifications = provider.notifications()

        results = []
        for name, prov in notifications.providers.all().items():
            type = NotificationType()
            type.id = prov.type_id
            type.name = name
            type.enabled = prov.enabled

            results.append(type)

        return self.send_valid_response(results)

    def all(self, zone_id, user_id):
        provider = Provider()
        zones = provider.dns_zones()

        if not zones.can_access(zone_id, user_id):
            return self.send_access_denied_response()

        zone = zones.get(zone_id)
        if not zone:
            return self.send_access_denied_response()

        results = []
        for name, subscription in zone.notifications.all().items():
            results.append(self.__load_subscription(name, subscription))

        return self.send_valid_response(results)

    def get(self, zone_id, type_name, user_id):
        provider = Provider()
        zones = provider.dns_zones()
        notifications = provider.notifications()

        if not zones.can_access(zone_id, user_id):
            return self.send_access_denied_response()

        zone = zones.get(zone_id)
        if not zone:
            return self.send_access_denied_response()

        type = notifications.types.get(name=type_name)
        if not type:
            return self.send_error_response(5006, 'Invalid type: {0}'.format(type_name), '')

        subscription = zone.notifications.get(type.name)
        if not subscription:
            return self.send_error_response(5007, 'Invalid notification subscription', '')

        item = self.__load_subscription(type.name, subscription)
        return self.send_valid_response(item)

    def __load_subscription(self, name, item):
        subscription = NotificationSubscription()
        subscription.type_id = item.type_id
        subscription.type = name
        subscription.zone_id = item.zone_id
        subscription.data = item.get_data_object()
        subscription.enabled = item.enabled

        return subscription

    def update(self, zone_id, type_name, user_id):
        provider = Provider()
        zones = provider.dns_zones()
        notifications = provider.notifications()
        logs = provider.dns_logs()

        if not zones.can_access(zone_id, user_id):
            return self.send_access_denied_response()

        zone = zones.get(zone_id)
        if not zone:
            return self.send_access_denied_response()

        type = notifications.types.get(name=type_name)
        if not type:
            return self.send_error_response(5006, 'Invalid type: {0}'.format(type_name), '')

        notification_provider = notifications.providers.get(type_name)
        if not notification_provider:
            return self.send_error_response(5006, 'Internal Error: Invalid provider', '')
        elif not notification_provider.enabled:
            return self.send_error_response(5009, 'Notification provider is disabled', '')

        subscription = zone.notifications.get(type.name)
        if not subscription:
            return self.send_error_response(5007, 'Invalid notification subscription', '')

        data = self.get_json([])
        if not data:
            return self.send_error_response(5008, 'No data sent', '')

        if 'enabled' in data:
            subscription.enabled = True if data['enabled'] else False

            # We need to set the last query log id as well.
            subscription.last_query_log_id = logs.get_last_log_id(zone.id)

        if 'data' in data:
            if type.name == 'email':
                subscription.data = self.__get_valid_emails(data['data'])
            else:
                subscription.data = data['data'].strip()

        subscription.save()

        return self.get(zone.id, type.name, user_id)

    def __get_valid_emails(self, recipients):
        if not isinstance(recipients, list):
            return []

        valid_recipients = []
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        for recipient in recipients:
            recipient = recipient.strip().lower()
            if len(recipient) > 0 and email_regex.match(recipient):
                valid_recipients.append(recipient)

        # Remove duplicates.
        valid_recipients = list(dict.fromkeys(valid_recipients))

        return valid_recipients
