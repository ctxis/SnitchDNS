from app.lib.models.notifications import WebPushSubscriptionModel
from app.lib.notifications.instances.webpush_subscription import WebPushSubscription


class WebPushManager:
    def __get(self, id=None, user_id=None):
        query = WebPushSubscriptionModel.query

        if id is not None:
            query = query.filter(WebPushSubscriptionModel.id == id)

        if user_id is not None:
            query = query.filter(WebPushSubscriptionModel.user_id == user_id)

        return query.all()

    def __load(self, item):
        return WebPushSubscription(item)

    def all(self, user_id=None):
        results = self.__get(user_id=user_id)
        items = []
        for result in results:
            items.append(self.__load(result))
        return items

    def get(self, id=None, user_id=None):
        results = self.__get(id=id, user_id=user_id)
        if len(results) == 0:
            return False
        return self.__load(results[0])

    def register(self, user_id, endpoint, key, authsecret):
        subscription = self.create()
        subscription.user_id = user_id
        subscription.endpoint = endpoint
        subscription.key = key
        subscription.authsecret = authsecret
        subscription.save()
        return subscription

    def create(self):
        item = WebPushSubscription(WebPushSubscriptionModel())
        item.save()
        return item
