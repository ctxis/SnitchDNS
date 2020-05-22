from twisted.names.server import DNSServerFactory
from twisted.names import dns


class DatabaseDNSFactory(DNSServerFactory):
    @property
    def app(self):
        return self.__app

    @app.setter
    def app(self, value):
        self.__app = value

    @property
    def logging(self):
        return self.__logging

    @logging.setter
    def logging(self, value):
        self.__logging = value

    def handleQuery(self, message, protocol, address):
        # Create a logging placeholder for the incoming request.
        self.__logging.new(
            str(address[0]),
            message.queries[0].name.name.decode('utf-8'),
            dns.QUERY_CLASSES.get(message.queries[0].cls, ''),
            dns.QUERY_TYPES.get(message.queries[0].type, '')
        )

        return super().handleQuery(message, protocol, address)

    def sendReply(self, protocol, message, address):
        self.__logging.finalise_query(
            address[0],
            message.queries[0].name.name.decode('utf-8'),
            dns.QUERY_CLASSES.get(message.queries[0].cls, ''),
            dns.QUERY_TYPES.get(message.queries[0].type, ''),
            str(message.answers[0]) if len(message.answers) > 0 else None
        )

        return super(DatabaseDNSFactory, self).sendReply(protocol, message, address)
