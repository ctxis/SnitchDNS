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
from app.lib.base.ldap import LDAPManager
from app.lib.api.manager import ApiManager
from app.lib.base.cron import CronManager
from app.lib.notifications.manager import NotificationManager
from app.lib.notifications.providers.email import EmailNotificationProvider
from app.lib.notifications.providers.webpush import WebPushNotificationProvider
from flask import current_app
import os


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
        return DNSZoneManager(
            self.settings(),
            self.dns_records(),
            self.users(),
            self.notifications()
        )

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
        return ShellManager(self.__get_venv_script())

    def __get_venv_script(self):
        script = os.path.realpath(os.path.join(current_app.root_path, '..', 'venv.sh'))
        if not os.path.isfile(script):
            raise Exception("venv.sh is missing from the root directory")
        elif not os.access(script, os.EX_OK):
            raise Exception("venv.sh in the root directory is not executable")
        return script

    def system(self):
        return SystemManager(self.shell(), self.settings())

    def daemon(self):
        settings = self.settings()
        return DaemonManager(
            settings.get('dns_daemon_bind_ip', ''),
            settings.get('dns_daemon_bind_port', 0),
            self.system(),
            self.shell()
        )

    def ldap(self):
        settings = self.settings()
        manager = LDAPManager()

        manager.enabled = int(settings.get('ldap_enabled', 0)) > 0
        manager.ssl = int(settings.get('ldap_ssl', 0)) > 0
        manager.host = settings.get('ldap_host', '')
        manager.base_dn = settings.get('ldap_base_dn', '')
        manager.domain = settings.get('ldap_domain', '')
        manager.bind_user = settings.get('ldap_bind_user', '')
        manager.bind_pass = settings.get('ldap_bind_pass', '')
        manager.mapping_username = settings.get('ldap_mapping_username', '')
        manager.mapping_fullname = settings.get('ldap_mapping_fullname', '')
        manager.mapping_email = settings.get('ldap_mapping_email', '')

        return manager

    def api(self):
        return ApiManager(self.users())

    def cron(self):
        return CronManager(
            self.notifications(),
            self.dns_zones(),
            self.dns_logs()
        )

    def notifications(self):
        settings = self.settings()

        # Load E-mail Provider.
        email_provider = EmailNotificationProvider(self.emails())
        email_provider.enabled = (int(settings.get('smtp_enabled', 0)) == 1)

        # Load Web Push Provider.
        webpush_provider = WebPushNotificationProvider()
        webpush_provider.enabled = (int(settings.get('webpush_enabled', 0)) == 1)

        # Create manager.
        manager = NotificationManager()
        manager.add_provider('emails', email_provider)
        manager.add_provider('webpush', webpush_provider)

        return manager
