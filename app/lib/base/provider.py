from app.lib.base.users import UserManager


class Provider():
    def users(self):
        return UserManager()
