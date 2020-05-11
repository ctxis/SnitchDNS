import ipaddress
import time


class DaemonManager:
    @property
    def ip(self):
        return self.__bind_ip

    @property
    def port(self):
        return self.__bind_port

    def __init__(self, bind_ip, bind_port, system, shell):
        self.__bind_ip = bind_ip
        self.__bind_port = int(bind_port)
        self.__system = system
        self.__shell = shell

    def start(self):
        command = [
            'flask',
            'snitch_daemon',
            '--bind-ip',
            self.ip,
            '--bind-port',
            str(self.port)
        ]

        self.__shell.execute(command, wait=False, venv=True)

        # Wait a little while - I'm not using a loop intentionally.
        time.sleep(5)

        return self.is_running()

    def stop(self):
        pids = self.is_running()
        if pids:
            for pid in pids:
                self.__system.process_kill(pid)

        # Wait a bit.
        time.sleep(5)

        return not self.is_running()

    def is_running(self):
        ids = []
        processes = self.__system.process_list()
        for process in processes:
            cmdline = process['cmdline']
            if ('snitch_daemon' in cmdline) and (self.ip in cmdline) and (str(self.port) in cmdline) :
                ids.append(process['id'])

        return ids if len(ids) > 0 else False

    def is_configured(self):
        if self.port < 1024 or self.port > 65535:
            return False
        elif not self.__is_valid_ip_address(self.ip):
            return False

        return True

    def __is_valid_ip_address(self, ip):
        try:
            obj = ipaddress.ip_address(ip)
        except ValueError:
            return False

        return True
