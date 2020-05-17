from app.lib.daemon.daemon import SnitchDaemon


class DNSDaemonCLI:
    def daemon(self, bind_ip, bind_port, forwarding_enabled, forwarders):
        print("Starting DNS...")
        daemon = SnitchDaemon(bind_ip, bind_port, forwarding_enabled, self.__get_forwarding_servers(forwarders))

        daemon.start()

        return True

    def __get_forwarding_servers(self, forwarders):
        servers = []

        if len(forwarders) == 0:
            return servers

        for forwarder in forwarders:
            servers.append((forwarder, 53))

        return servers
