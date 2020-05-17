from app.lib.base.provider import Provider
from app import create_app
from twisted.internet import reactor
from twisted.names.dns import DNSDatagramProtocol
from app.lib.daemon.server.resolver import DatabaseDNSResolver
from app.lib.daemon.server.factory import DatabaseDNSFactory


class SnitchDaemon:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

    def start(self):
        resolver = DatabaseDNSResolver(create_app(), Provider().dns_manager())
        factory = DatabaseDNSFactory(clients=[resolver])

        reactor.listenUDP(self.__port, DNSDatagramProtocol(factory), interface=self.__host)
        reactor.listenTCP(self.__port, factory, interface=self.__host)
        reactor.run()
