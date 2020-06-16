from app.lib.dns.log_manager import DNSLogManager


class DatabaseDNSLogging:
    def __init__(self, app):
        self.__app = app
        self.__log_manager = DNSLogManager()

    def create(self, domain=None, cls=None, type=None):
        # This should be called from within the app context.
        item = self.__log_manager.create()
        if domain is not None:
            item.domain = domain

        if cls is not None:
            item.cls = cls

        if type is not None:
            item.type = type

        item.save()
        return item

    def get(self, log_id):
        return self.__log_manager.get(log_id)

    def find(self, domain, cls, type, completed):
        # When this is called, we should already be within an app_context().
        return self.__log_manager.find(domain, cls, type, completed)
