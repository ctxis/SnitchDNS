from dnslib.server import DNSLogger, DNSServer
from app.lib.daemon.resolver import DatabaseResolver
import time
from app.lib.base.provider import Provider


class SnitchDaemon:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

    def start(self):
        dns_logger = DNSLogger()
        dns_resolver = DatabaseResolver(Provider().dns())
        dns_server = DNSServer(dns_resolver, address=self.__host, port=self.__port, logger=dns_logger)

        dns_server.start_thread()

        try:
            while dns_server.isAlive():
                time.sleep(1)
        except KeyboardInterrupt:
            dns_server.stop()
