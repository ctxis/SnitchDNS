import sys
import psutil
from packaging import version


class SystemManager:
    def __init__(self, shell):
        self.shell = shell

    def is_virtual_environment(self):
        # https://stackoverflow.com/questions/1871549/determine-if-python-is-running-inside-virtualenv/42580137#42580137
        return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

    def can_run_flask(self):
        output = self.shell.execute(['flask', 'snitch_env'])
        return True if output == 'OK' else False

    def get_python_version(self):
        return str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.' + str(sys.version_info.micro)

    def check_version(self, current_version, minimum_version):
        return version.parse(current_version) >= version.parse(minimum_version)

    def process_list(self):
        processes = []
        for proc in psutil.process_iter():
            processes.append(
                {
                    'id': proc.pid,
                    'cmdline': proc.cmdline()
                }
            )
        return processes

    def process_kill(self, pid):
        for proc in psutil.process_iter():
            if proc.pid == pid:
                proc.kill()
                return True
        return False
