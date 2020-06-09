from app.lib.notifications.providers.base import BaseNotificationProvider


class EmailNotificationProvider(BaseNotificationProvider):
    def __init__(self, emails):
        super().__init__()

        self.__emails = emails
        self.title = 'E-mails'
        self.has_settings = True
