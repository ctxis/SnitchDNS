from app.lib.base.users import UserManager
from app.lib.base.settings import SettingsManager
from app.lib.dns.manager import DNSManager
from app.lib.dns.zone_manager import DNSZoneManager
from app.lib.dns.record_manager import DNSRecordManager
from app.lib.dns.log_manager import DNSLogManager
from app.lib.dns.search_manager import SearchManager
from app.lib.base.password_complexity import PasswordComplexityManager
from app.lib.base.email import EmailManager
from app.lib.base.shell import ShellManager
from app.lib.base.system import SystemManager
from app.lib.daemon.manager import DaemonManager


class Provider:
    def users(self):
        return UserManager(self.password_complexity())

    def settings(self):
        return SettingsManager()

    def dns_manager(self):
        return DNSManager(
            self.dns_zones(),
            self.dns_records(),
            self.dns_logs(),
            self.settings()
        )

    def dns_zones(self):
        return DNSZoneManager(self.settings())

    def dns_records(self):
        return DNSRecordManager()

    def dns_logs(self):
        return DNSLogManager()

    def search(self):
        return SearchManager()

    def password_complexity(self):
        settings = self.settings()
        return PasswordComplexityManager(
            settings.get('pwd_min_length', 12),
            settings.get('pwd_min_lower', 2),
            settings.get('pwd_min_upper', 2),
            settings.get('pwd_min_digits', 2),
            settings.get('pwd_min_special', 2)
        )

    def emails(self):
        settings = self.settings()
        return EmailManager(
            settings.get('smtp_host', 'localhost'),
            int(settings.get('smtp_port', 25)),
            settings.get('smtp_user', ''),
            settings.get('smtp_pass', ''),
            settings.get('smtp_sender', ''),
            True if int(settings.get('smtp_tls', '0')) == 1 else False
        )

    def shell(self):
        return ShellManager()

    def system(self):
        return SystemManager(self.shell())

    def daemon(self):
        settings = self.settings()
        return DaemonManager(
            settings.get('dns_daemon_bind_ip', ''),
            settings.get('dns_daemon_bind_port', 0),
            self.system(),
            self.shell()
        )
