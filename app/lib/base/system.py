import sys
import psutil
import datetime
from packaging import version


class SystemManager:
    def __init__(self, shell, settings):
        self.shell = shell
        self.settings = settings

    def is_virtual_environment(self):
        # https://stackoverflow.com/questions/1871549/determine-if-python-is-running-inside-virtualenv/42580137#42580137
        return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

    def can_run_flask(self):
        output = self.shell.execute(['flask', 'env'], venv=True)
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

    def run_updates(self):
        self.__update_git_hash_version()
        self.__set_update_url('https://api.github.com/repos/ctxis/SnitchDNS/git/refs/heads/master')

    def __update_git_hash_version(self):
        git_binary = self.shell.execute(['which', 'git'])
        if len(git_binary) == 0:
            return False

        # Save latest commit short hash.
        version = self.shell.execute(['git', 'rev-parse', '--short', 'HEAD'])
        self.settings.save('git_hash_version', version)

        # Save commit count on the master branch (like a version tracker).
        try:
            count = int(self.shell.execute(['git', 'rev-list', '--count', 'master']))
        except ValueError:
            count = 0
        self.settings.save('git_commit_count', count)

        # Save last commit date.
        try:
            last_commit_timestamp = int(self.shell.execute(['git', 'log', '-1', '--format=%at']))
        except ValueError:
            last_commit_timestamp = 0

        last_commit_date = ''
        if last_commit_timestamp > 0:
            last_commit_date = datetime.datetime.fromtimestamp(last_commit_timestamp).strftime('%Y-%m-%d %H:%M')
        self.settings.save('last_commit_date', last_commit_date)

        return True

    def __set_update_url(self, url):
        update_url = self.settings.get('update_url', None)
        if update_url is None:
            self.settings.save('update_url', url)
        return True
