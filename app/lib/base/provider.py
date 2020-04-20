from app.lib.base.users import UserManager
from app.lib.base.settings import SettingsManager
from app.lib.dns.manager import DNSManager
from app.lib.base.password_complexity import PasswordComplexityManager
from app.lib.base.email import EmailManager


class Provider:
    def users(self):
        return UserManager(self.password_complexity())

    def settings(self):
        return SettingsManager()

    def dns(self):
        return DNSManager(self.settings())

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
