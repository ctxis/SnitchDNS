from app.lib.base.instance.base_instance import BaseInstance


class LogError(BaseInstance):
    def __init__(self, item):
        super().__init__(item)

        self.__username = ''

    @property
    def user_id(self):
        return self.item.user_id

    @user_id.setter
    def user_id(self, value):
        self.item.user_id = value

    @property
    def description(self):
        return self.item.description

    @description.setter
    def description(self, value):
        self.item.description = value

    @property
    def details(self):
        return self.item.details

    @details.setter
    def details(self, value):
        self.item.details = value

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        self.__username = value
