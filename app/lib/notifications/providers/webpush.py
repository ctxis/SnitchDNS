from app.lib.notifications.providers.base import BaseNotificationProvider


class WebPushNotificationProvider(BaseNotificationProvider):
    def __init__(self):
        super().__init__()

        self.title = 'Web Push'
