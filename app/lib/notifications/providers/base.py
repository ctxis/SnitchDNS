class BaseNotificationProvider:
    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = value

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = value

    @property
    def has_settings(self):
        return self.__has_settings

    @has_settings.setter
    def has_settings(self, value):
        self.__has_settings = value

    def __init__(self):
        self.__enabled = False
        self.__has_settings = False
        self.__title = ''

    def process_cron_notification(self, subscription, subject, body, verbose=False):
        raise Exception("Coding Error: process_cron_notification() not implemented.")
