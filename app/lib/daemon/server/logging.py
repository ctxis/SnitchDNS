from app.lib.dns.log_manager import DNSLogManager


class DatabaseDNSLogging:
    def __init__(self, app):
        self.__app = app
        self.__log_manager = DNSLogManager()

    def new(self, source_ip, domain, cls, type):
        with self.__app.app_context():
            item = self.__log_manager.create()
            item.source_ip = source_ip
            item.domain = domain
            item.cls = cls
            item.type = type
            item.save()

    def find(self, source_ip, domain, cls, type, completed):
        # When this is called, we should already be within an app_context().
        return self.__log_manager.find(domain, cls, type, completed, source_ip)

    def finalise_query(self, source_ip, domain, cls, type, data):
        with self.__app.app_context():
            item = self.__log_manager.find(domain, cls, type, False, source_ip)
            if item:
                item.completed = True
                item.found = False
                if data is not None:
                    item.data = data
                    item.forwarded = True
                else:
                    item.forwarded = False
                item.save()
