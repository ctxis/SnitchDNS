from app.lib.notifications.providers.base import BaseNotificationProvider


class EmailNotificationProvider(BaseNotificationProvider):
    def __init__(self, emails):
        super().__init__()

        self.__emails = emails
        self.title = 'E-mails'
        self.has_settings = True

    def send(self, recipients, subject, body):
        if isinstance(recipients, str):
            recipients = [recipients]

        if len(recipients) == 0:
            return False

        return self.__emails.send(recipients, subject, body)
