from app.lib.daemon.daemon import SnitchDaemon


class DNSDaemonCLI:
    def daemon(self, bind_ip, bind_port):
        print("Starting DNS...")
        daemon = SnitchDaemon(bind_ip, bind_port)

        daemon.start()

        return True
