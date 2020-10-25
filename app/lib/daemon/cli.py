from app.lib.daemon.daemon import SnitchDaemon
import os
import csv


class DNSDaemonCLI:
    def daemon(self, bind_ip, bind_port, forwarding_enabled, forwarders, csv_location):
        print("Starting DNS...")

        if not self.__prepare_csv_logging(csv_location):
            csv_location = ''

        daemon = SnitchDaemon(
            bind_ip,
            bind_port,
            forwarding_enabled,
            self.__get_forwarding_servers(forwarders),
            csv_location
        )

        daemon.start()

        return True

    def __get_forwarding_servers(self, forwarders):
        servers = []

        if len(forwarders) == 0:
            return servers

        for forwarder in forwarders:
            servers.append((forwarder, 53))

        return servers

    def __prepare_csv_logging(self, file):
        if len(file) == 0:
            # Not enabled.
            return False
        elif not (os.access(file, os.W_OK) if os.path.isfile(file) else os.access(os.path.dirname(file), os.W_OK)):
            # Not writable.
            return False

        if not os.path.isfile(file):
            header = [
                'id',
                'source_ip',
                'domain',
                'class',
                'type',
                'found',
                'forwarded',
                'blocked',
                'date'
            ]

            with open(file, 'w') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow(header)

        return True
