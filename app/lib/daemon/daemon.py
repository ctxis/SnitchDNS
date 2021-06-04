from app.lib.base.provider import Provider
from app import create_app
from twisted.internet import reactor
from twisted.names.dns import DNSDatagramProtocol
from twisted.names import client
from app.lib.daemon.server.resolver import DatabaseDNSResolver
from app.lib.daemon.server.factory import DatabaseDNSFactory
from app.lib.daemon.server.logging import DatabaseDNSLogging
from app.lib.daemon.server.cache import DNSCache
from twisted.python import log
import logging


class SnitchDaemon:
    def __init__(self, host, port, forwarding_enabled, forwarders, csv_location, cache_enabled):
        self.__host = host
        self.__port = port
        self.__forwarding_enabled = forwarding_enabled
        self.__forwarders = forwarders
        self.__csv_location = csv_location
        self.__cache_enabled = cache_enabled

    def start(self):
        app_for_context = create_app()
        dns_logging = DatabaseDNSLogging(app_for_context)
        dns_cache = DNSCache(self.__cache_enabled, Provider().settings())

        clients = [DatabaseDNSResolver(app_for_context, Provider().dns_manager(), dns_logging, dns_cache)]
        if self.__forwarding_enabled and len(self.__forwarders) > 0:
            clients.append(client.Resolver(servers=self.__forwarders))

        factory = DatabaseDNSFactory(clients=clients, verbose=2)
        factory.app = app_for_context
        factory.logging = dns_logging
        factory.restrictions = Provider().dns_restrictions()
        factory.csv_location = self.__csv_location

        observer = log.PythonLoggingObserver()
        observer.start()

        logging.basicConfig()
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        reactor.listenUDP(self.__port, DNSDatagramProtocol(factory), interface=self.__host)
        reactor.listenTCP(self.__port, factory, interface=self.__host)
        reactor.run()
