from app.lib.base.instance.base_instance import BaseInstance
from app.lib.models.dns import DNSZoneTagModel


class DNSZone(BaseInstance):
    def __init__(self, item):
        super().__init__(item)

        self.__record_count = 0
        self.__match_count = 0
        self.__username = ''
        self.__notifications = None
        self.__restrictions = None
        self.__tags = []

    @property
    def domain(self):
        return self.item.domain

    @domain.setter
    def domain(self, value):
        self.item.domain = value

    @property
    def active(self):
        return self.item.active

    @active.setter
    def active(self, value):
        self.item.active = value

    @property
    def catch_all(self):
        return self.item.catch_all

    @catch_all.setter
    def catch_all(self, value):
        self.item.catch_all = value

    @property
    def user_id(self):
        return self.item.user_id

    @user_id.setter
    def user_id(self, value):
        self.item.user_id = value

    @property
    def master(self):
        return self.item.master

    @master.setter
    def master(self, value):
        self.item.master = value

    @property
    def record_count(self):
        return self.__record_count

    @record_count.setter
    def record_count(self, value):
        self.__record_count = value

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        self.__username = value

    @property
    def notifications(self):
        return self.__notifications

    @notifications.setter
    def notifications(self, value):
        self.__notifications = value

    @property
    def match_count(self):
        return self.__match_count

    @match_count.setter
    def match_count(self, value):
        self.__match_count = value

    @property
    def forwarding(self):
        return self.item.forwarding

    @forwarding.setter
    def forwarding(self, value):
        self.item.forwarding = value

    @property
    def restrictions(self):
        return self.__restrictions

    @restrictions.setter
    def restrictions(self, value):
        self.__restrictions = value

    @property
    def tags(self):
        return self.__tags

    @tags.setter
    def tags(self, value):
        self.__tags = value

    def delete_tags(self):
        DNSZoneTagModel.query.filter(DNSZoneTagModel.dns_zone_id == self.id).delete()
        self.tags = []
        self.commit()
