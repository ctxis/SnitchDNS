from app.lib.base.provider import Provider
from app import create_app
from twisted.internet import reactor
from twisted.names.dns import DNSDatagramProtocol
from twisted.names import client
from app.lib.daemon.server.resolver import DatabaseDNSResolver
from app.lib.daemon.server.factory import DatabaseDNSFactory
from app.lib.daemon.server.logging import DatabaseDNSLogging


class SnitchDaemon:
    def __init__(self, host, port, forwarding_enabled, forwarders):
        self.__host = host
        self.__port = port
        self.__forwarding_enabled = forwarding_enabled
        self.__forwarders = forwarders

    def start(self):
        app_for_context = create_app()
        logging = DatabaseDNSLogging(app_for_context)

        clients = [DatabaseDNSResolver(app_for_context, Provider().dns_manager(), logging)]
        if self.__forwarding_enabled and len(self.__forwarders) > 0:
            clients.append(client.Resolver(servers=self.__forwarders))

        factory = DatabaseDNSFactory(clients=clients)
        factory.app = app_for_context
        factory.logging = logging

        reactor.listenUDP(self.__port, DNSDatagramProtocol(factory), interface=self.__host)
        reactor.listenTCP(self.__port, factory, interface=self.__host)
        reactor.run()
