from app.lib.base.users import UserManager
from app.lib.base.settings import SettingsManager
from app.lib.dns.manager import DNSManager


class Provider():
    def users(self):
        return UserManager()

    def settings(self):
        return SettingsManager()

    def dns(self):
        return DNSManager()
