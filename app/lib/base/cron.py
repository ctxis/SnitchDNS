class CronManager:
    def __init__(self, notifications, dns_zones, dns_logs):
        self.__notifications = notifications
        self.__dns_zones = dns_zones
        self.__dns_logs = dns_logs

    def run(self):
        self.send_notifications()
        return True

    def send_notifications(self):
        # First get enabled providers.
        notification_providers = self.__notifications.get_enabled_providers()

        # Then get zones with that provider enabled.
        for name, provider in notification_providers.items():
            print("Processing notifications for {0}".format(name))
            if name == 'emails':
                self.__send_email_notifications(provider)
            elif name == 'webpush':
                pass
            else:
                continue

        return True

    def __send_email_notifications(self, provider):
        zone_notifications = self.__notifications.get_subscribed(email=True)

        # Check to see if a notification needs to be sent.
        print("Processing subscribed {0} zone(s)".format(len(zone_notifications)))
        for zone_notification in zone_notifications:
            recipients = zone_notification.email_recipients()
            if len(recipients) == 0:
                # This is an error, disable the provider.
                print("Error: Zone {0} does not have any recipients.".format(zone_notification.dns_zone_id))

                zone_notification.email = False
                zone_notification.save()
                continue

            max_id = self.__dns_logs.get_last_log_id(zone_notification.dns_zone_id)
            if zone_notification.last_query_log_id >= max_id:
                # Nothing to do.
                continue

            message = self.__create_message(zone_notification.dns_zone_id)
            if message is False:
                print("Error: Could not load message for zone {0}".format(zone_notification.dns_zone_id))
                continue

            print("Trying to send notification for zone {0}".format(zone_notification.dns_zone_id))
            if provider.send(recipients, 'SnitchDNS Notification', message) is True:
                # Disable provider for that zone.
                print("Notification sent - disabling provider")
                zone_notification.email = False
                zone_notification.save()
            else:
                print("Could not send e-mail notifications for zone {0}".format(zone_notification.dns_zone_id))

        return True

    def __create_message(self, dns_zone_id):
        zone = self.__dns_zones.get(dns_zone_id)
        if not zone:
            return False

        return "Domain {0} has been resolved".format(zone.full_domain)
