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
        # Keeping this just in case.
        return super().handleQuery(message, protocol, address)

    def sendReply(self, protocol, message, address):
        # When the reply is ready to be sent, we need to look in the answers for the 'Record_SNITCH' object.
        # This object is added for the sole purpose of keeping the database query log primary key (id) in its TTL
        # property. This is to keep the correlation between the resolver and the factory, as it's not possible to get
        # the Source IP within the resolver. So we have to try and update the query log in here.

        with self.__app.app_context():
            snitch_index = self.__find_snitch_record(message.answers)
            log = None
            zone_id = 0
            if snitch_index is not None:
                # Retrieve the record and remove it from the messages.
                snitch_record = message.answers.pop(snitch_index)
                log = self.__logging.get(snitch_record.ttl)

            # If the snitch_index doesn't exist, or if the log retrieval above didn't work, try to find it here.
            if not log:
                log = self.__logging.find(
                    message.queries[0].name.name.decode('utf-8'),
                    dns.QUERY_CLASSES.get(message.queries[0].cls, ''),
                    dns.QUERY_TYPES.get(message.queries[0].type, ''),
                    False
                )

            if log:
                zone_id = log.dns_zone_id
                log.source_ip = str(address[0])
                log.completed = True
                log.data = str(message.answers)
                log.save()

            # We need to check if the IP address is blocked for that specific domain. The reason why this is happening
            # here is because I couldn't find a way to get the 'address' variable in the resolved. Therefore we need to
            # check if the IP is restricted and remove all answers from it if that's the case.
            if zone_id > 0:
                if not self.__restrictions.allow(zone_id, str(address[0])):
                    message.answers = []
                    if log:
                        log.blocked = True
                        log.save()

        return super(DatabaseDNSFactory, self).sendReply(protocol, message, address)

    def __find_snitch_record(self, answers):
        index = None
        for i, answer in enumerate(answers):
            if answer.__class__.__name__ == 'Record_SNITCH':
                index = i
                break

        return index
