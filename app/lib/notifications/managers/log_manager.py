from app.lib.models.notifications import NotificationLogModel
from app.lib.notifications.instances.notification_log import NotificationLog
import datetime


class NotificationLogManager:
    def __get(self, id=None, subscription_id=None, sent_at=None):
        query = NotificationLogModel.query

        if id is not None:
            query = query.filter(NotificationLogModel.id == id)

        if subscription_id is not None:
            query = query.filter(NotificationLogModel.subscription_id == subscription_id)

        if sent_at is not None:
            query = query.filter(NotificationLogModel.sent_at == sent_at)

        return query.all()

    def __load(self, item):
        return NotificationLog(item)

    def get(self, id=None, subscription_id=None):
        if (id is None) and (subscription_id is None):
            # At least one must be set.
            return False

        results = self.__get(id=id, subscription_id=subscription_id)
        return self.__load(results[0]) if len(results) > 0 else False

    def create(self):
        item = NotificationLog(NotificationLogModel())
        item.save()
        return item

    def log(self, subscription_id):
        item = self.create()
        item.subscription_id = subscription_id
        item.sent_at = datetime.datetime.now()
        item.save()
        return item
