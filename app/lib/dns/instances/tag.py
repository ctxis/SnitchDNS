from app.lib.base.instance.base_instance import BaseInstance


class Tag(BaseInstance):
    def __init__(self, item):
        super().__init__(item)

    @property
    def user_id(self):
        return self.item.user_id

    @user_id.setter
    def user_id(self, value):
        self.item.user_id = value

    @property
    def name(self):
        return self.item.name

    @name.setter
    def name(self, value):
        self.item.name = value
