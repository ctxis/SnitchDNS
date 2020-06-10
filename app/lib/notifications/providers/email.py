from app.lib.notifications.providers.base import BaseNotificationProvider
import json


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

    def process_cron_notification(self, subscription, subject, body, user_id, verbose=False):
        recipients = self.__get_recipients(subscription.data)
        if len(recipients) == 0:
            if verbose:
                print("No e-mail recipients found for zone {0}. Disabling provider.".format(subscription.zone_id))

            # Disable notification.
            subscription.enabled = False
            subscription.save()

            return False

        if verbose:
            print("Sending notification for zone {0} to {1}".format(subscription.zone_id, ", ".join(recipients)))

        result = self.send(recipients, subject, body)

        if result:
            if verbose:
                print("Notification sent! Disabling provider.")

            # Disable notification.
            subscription.enabled = False
            subscription.save()
        else:
            if verbose:
                print("Error: Could not send notification for zone {0}".format(subscription.zone_id))

        return result

    def __get_recipients(self, data):
        if data is None:
            return []
        elif not data:
            return []
        elif len(data) == 0:
            return []

        try:
            recipients = json.loads(data)
        except:
            recipients = []

        return recipients
