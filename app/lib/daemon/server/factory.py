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

    @property
    def restrictions(self):
        return self.__restrictions

    @restrictions.setter
    def restrictions(self, value):
        self.__restrictions = value

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

        # We need to check if the IP address is blocked for that specific domain. The reason why this is happening here
        # is because I couldn't find a way to get the 'address' variable in the resolved. Therefore we need to check if
        # the IP is restricted and remove all answers from it if that's the case.
        if not self.__allow_ip(message, address):
            message.answers = []

        return super(DatabaseDNSFactory, self).sendReply(protocol, message, address)

    def __allow_ip(self, message, address):
        allow = True
        with self.__app.app_context():
            if len(message.answers) > 0:
                for answer in message.answers:
                    if not self.__restrictions.allow(answer.zone_id, str(address[0])):
                        allow = False
                        break

        return allow
