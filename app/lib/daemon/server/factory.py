from twisted.names.server import DNSServerFactory


class DatabaseDNSFactory(DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        # TODO - Log incoming request.
        source_ip = address[0]
        source_port = address[1]

        return super().handleQuery(message, protocol, address)

    def sendReply(self, protocol, message, address):
        # TODO - Log outgoing request.
        return super(DatabaseDNSFactory, self).sendReply(protocol, message, address)
