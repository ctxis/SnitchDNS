from app.lib.models.notifications import NotificationSubscriptionModel
from app.lib.notifications.instances.notification_subscription import NotificationSubscription


class NotificationSubscriptionManager:
    def __get(self, id=None, zone_id=None, type_id=None, enabled=None):
        query = NotificationSubscriptionModel.query

        if id is not None:
            query = query.filter(NotificationSubscriptionModel.id == id)

        if zone_id is not None:
            query = query.filter(NotificationSubscriptionModel.zone_id == zone_id)

        if type_id is not None:
            query = query.filter(NotificationSubscriptionModel.type_id == type_id)

        if enabled is not None:
            query = query.filter(NotificationSubscriptionModel.enabled == enabled)

        return query.all()

    def __load(self, item):
        return NotificationSubscription(item)

    def get(self, id=None, zone_id=None, type_id=None, enabled=None):
        if (id is None) and (zone_id is None) and (type_id is None) and (enabled is None):
            # Must set at least one.
            return False

        results = self.__get(id=id, zone_id=zone_id, type_id=type_id, enabled=enabled)
        return self.__load(results[0]) if len(results) > 0 else False

    def all(self, zone_id=None, type_id=None, enabled=None):
        results = self.__get(zone_id=zone_id, type_id=type_id, enabled=enabled)
        items = []
        for result in results:
            items.append(self.__load(result))
        return items

    def create(self, zone_id=None, type_id=None):
        item = NotificationSubscription(NotificationSubscriptionModel())
        if zone_id is not None:
            item.zone_id = zone_id
        if type_id is not None:
            item.type_id = type_id
        item.save()
        return item
