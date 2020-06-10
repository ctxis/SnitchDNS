from app.lib.notifications.providers.base import BaseNotificationProvider
import requests


class SlackWebhookNotificationProvider(BaseNotificationProvider):
    def __init__(self):
        super().__init__()

        self.title = 'Slack Webhooks'
        self.has_settings = True

    def process_cron_notification(self, subscription, subject, body, user_id, verbose=False):
        url = subscription.data.strip()
        if len(url) == 0:
            if verbose:
                print("No URL set for Slack Webhook for zone {0}. Disabling provider.".format(subscription.zone_id))

            # Disable notification.
            subscription.enabled = False
            subscription.save()

            return False

        result = self.__send(url, "{0}: {1}".format(subject, body), verbose=verbose)
        if result:
            if verbose:
                print("Slack notification for zone {0} sent.".format(subscription.zone_id))

            # Disable.
            subscription.enabled = False
            subscription.save()
        else:
            if verbose:
                print("Could not send Slack Webhook notification for zone {0}".format(subscription.zone_id))

        return result

    def __send(self, url, text, verbose=False):
        response = requests.post(url, json={'text': text})
        if response.status_code == 200:
            return True

        if verbose:
            print("Error: Slack Webhook response is {0}: {1}".format(response.status_code, response.content.decode()))
        return False
