from app.lib.notifications.providers.base import BaseNotificationProvider
from app.lib.notifications.managers.webpush_manager import WebPushManager
from pywebpush import webpush, WebPushException
import json


class WebPushNotificationProvider(BaseNotificationProvider):
    @property
    def icon(self):
        return self.__icon

    @icon.setter
    def icon(self, value):
        self.__icon = value

    @property
    def vapid_private(self):
        return self.__vapid_private

    @vapid_private.setter
    def vapid_private(self, value):
        self.__vapid_private = value

    @property
    def admin_email(self):
        return self.__admin_email

    @admin_email.setter
    def admin_email(self, value):
        self.__admin_email = value

    def __init__(self):
        super().__init__()

        self.title = 'Web Push'
        self.__icon = ''
        self.__vapid_private = ''
        self.__admin_email = ''

    def process_cron_notification(self, subscription, subject, body, user_id, verbose=False):
        # Get all the endpoints registered by the user.
        webpush_manager = WebPushManager()
        endpoints = webpush_manager.all(user_id=user_id)

        # Send it to all.
        final_result = False
        for endpoint in endpoints:
            data = {
                'title': subject,
                'body': body,
                'url': '/dns/{0}/view'.format(subscription.zone_id),
                'icon': self.icon
            }

            result = self.__send(data, endpoint.endpoint, endpoint.key, endpoint.authsecret, verbose=verbose)
            if result:
                if verbose:
                    print("Notification for endpoint {0} sent to user {1} and zone {2}".format(endpoint.id, user_id, subscription.zone_id))
                # If at least one is sent, mark as success.
                final_result = True
            else:
                if verbose:
                    print("Could not send notification for endpoint {0} sent to user {1} and zone {2}".format(endpoint.id, user_id, subscription.zone_id))

        if final_result:
            # Disable.
            subscription.enabled = False
            subscription.save()

        return final_result

    def __send(self, data, endpoint, key, authsecret, verbose=False):
        try:
            webpush(
                subscription_info={
                    'endpoint': endpoint,
                    'keys': {
                        'p256dh': key,
                        'auth': authsecret
                    },
                    'contentEncoding': 'aesgcm'
                },
                data=json.dumps(data),
                vapid_private_key=self.vapid_private,
                vapid_claims={
                    'sub': 'mailto:' + self.admin_email
                }
            )

            return True
        except WebPushException as ex:
            if verbose:
                print("Error sending push notification: {}", repr(ex))
            if ex.response and ex.response.json():
                extra = ex.response.json()
                if verbose:
                    print("Remote service replied with a {}:{}, {}", extra.code, extra.errno, extra.message)

        return False
