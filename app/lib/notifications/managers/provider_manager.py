class NotificationProviderManager:
    def __init__(self):
        self.__providers = {}

    def add(self, name, provider):
        self.__providers[name] = provider

    def has_enabled(self):
        for name, provider in self.__providers.items():
            if provider.enabled:
                return True
        return False

    def get(self, name):
        return self.__providers[name] if name in self.__providers else None

    def get_enabled(self):
        providers = {}
        for name, provider in self.__providers.items():
            if provider.enabled:
                providers[name] = provider
        return providers

    def all(self):
        return self.__providers
