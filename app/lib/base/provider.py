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
from app.lib.notifications.providers.slack import SlackWebhookNotificationProvider
from app.lib.log.manager import LoggingManager
from app.lib.dns.restriction_manager import RestrictionManager
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
            self.notifications(),
            self.dns_logs(),
            self.dns_restrictions()
        )

    def dns_records(self):
        return DNSRecordManager(
            self.dns_logs()
        )

    def dns_logs(self):
        return DNSLogManager()

    def dns_restrictions(self):
        return RestrictionManager()

    def search(self):
        return SearchManager()

    def password_complexity(self):
        settings = self.settings()
        return PasswordComplexityManager(
            settings.get('pwd_min_length', 12, type=int),
            settings.get('pwd_min_lower', 2, type=int),
            settings.get('pwd_min_upper', 2, type=int),
            settings.get('pwd_min_digits', 2, type=int),
            settings.get('pwd_min_special', 2, type=int)
        )

    def emails(self):
        settings = self.settings()
        return EmailManager(
            settings.get('smtp_host', 'localhost'),
            settings.get('smtp_port', 25, type=int),
            settings.get('smtp_user', ''),
            settings.get('smtp_pass', ''),
            settings.get('smtp_sender', ''),
            settings.get('smtp_tls', False, type=bool)
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
            settings.get('dns_daemon_bind_port', 0, type=int),
            self.system(),
            self.shell()
        )

    def ldap(self):
        settings = self.settings()
        manager = LDAPManager()

        manager.enabled = settings.get('ldap_enabled', False, type=bool)
        manager.ssl = settings.get('ldap_ssl', False, type=bool)
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

        # Create manager.
        manager = NotificationManager()

        # Put some error handler in case the user forgets to run the seed function.
        expected_providers = ['email', 'webpush', 'slack']
        for name in expected_providers:
            if manager.types.get(name=name) is False:
                raise Exception("Notification provider {0} is missing. Make sure you run the SnitchDNS 'snitchdb' function".format(name))

        # Load E-mail Provider.
        email_provider = EmailNotificationProvider(self.emails())
        email_provider.enabled = settings.get('smtp_enabled', False, type=bool)
        email_provider.type_id = manager.types.get(name='email').id

        # Load Web Push Provider.

        # Load data per supported notification type.
        admins = self.users().get_admins(active=True)
        # Get the first admin's e-mail or fallback to a dummy e-mail.
        admin_email = admins[0].email if len(admins) > 0 else 'error@example.com'

        webpush_provider = WebPushNotificationProvider()
        webpush_provider.enabled = settings.get('webpush_enabled', False, type=bool)
        webpush_provider.type_id = manager.types.get(name='webpush').id
        webpush_provider.admin_email = admin_email
        webpush_provider.vapid_private = self.settings().get('vapid_private', '')
        webpush_provider.icon = '/static/images/favicon.png'

        # Load Slack Webhook Provider.
        slack_provider = SlackWebhookNotificationProvider()
        slack_provider.enabled = settings.get('slack_enabled', False, type=bool)
        slack_provider.type_id = manager.types.get(name='slack').id

        manager.providers.add('email', email_provider)
        manager.providers.add('webpush', webpush_provider)
        manager.providers.add('slack', slack_provider)

        return manager

    def logging(self):
        return LoggingManager(self.users())

    def env(self, name, default=None, must_exist=False):
        if not name in os.environ:
            if must_exist:
                raise Exception("Environment variable not found: {0}".format(name))
            return default
        return os.environ[name]
