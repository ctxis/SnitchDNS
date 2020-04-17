from app.lib.base.users import UserManager
from app.lib.base.settings import SettingsManager


class Provider():
    def users(self):
        return UserManager()

    def settings(self):
        return SettingsManager()
