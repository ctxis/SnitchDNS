class NotificationSubscriptionCollection:
    def __init__(self):
        self.__subscriptions = {}

    def add(self, name, subscription):
        self.__subscriptions[name] = subscription

    def get(self, name):
        return self.__subscriptions[name] if name in self.__subscriptions else None

    def is_enabled(self, name):
        subscription = self.get(name)
        if subscription is None:
            return False
        return subscription.enabled

    def has_enabled(self):
        for name, subscription in self.__subscriptions.items():
            if subscription.enabled:
                return True
        return False

    def count(self):
        return len(self.__subscriptions)

    def all(self):
        return self.__subscriptions
