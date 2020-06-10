class CronManager:
    def __init__(self, notifications, dns_zones, dns_logs):
        self.__notifications = notifications
        self.__dns_zones = dns_zones
        self.__dns_logs = dns_logs

    def run(self):
        self.send_notifications()
        return True

    def send_notifications(self):
        # First get the enabled providers.
        print("Getting enabled notification providers...")
        notification_providers = self.__notifications.providers.get_enabled()
        print("Found {0} providers: {1}".format(len(notification_providers), ", ".join(notification_providers.keys())))

        for name, provider in notification_providers.items():
            print("Processing notifications for {0}".format(name))

            type = self.__notifications.types.get(name=name)
            if not type:
                print("Could not get type id for {0}".format(name))
                continue
            print("The type id for {0} is {1}".format(name, type.id))

            subscribed_zones = self.__notifications.subscriptions.all(type_id=type.id, enabled=True)
            print("Found {0} subscribed zones for {1}".format(len(subscribed_zones), name))

            for subscribed_zone in subscribed_zones:
                print("Processing {0} notifications for zone {1}".format(name, subscribed_zone.zone_id))
                # Check to see if there are new queries.
                max_id = self.__dns_logs.get_last_log_id(subscribed_zone.zone_id)
                if subscribed_zone.last_query_log_id >= max_id:
                    # No new notifications.
                    print("No new notifications for zone {0}".format(subscribed_zone.zone_id))
                    continue

                # Get the message to be sent.
                body = self.__create_message(subscribed_zone.zone_id)
                if body is False:
                    print("Could not get message body for zone {0}".format(subscribed_zone.zone_id))
                    continue

                zone = self.__dns_zones.get(subscribed_zone.zone_id)
                if not zone:
                    print("Zone {0} does not exist".format(subscribed_zone.zone_id))
                    continue

                if provider.process_cron_notification(subscribed_zone, 'SnitchDNS Notification', body, zone.user_id, verbose=True):
                    # Create a log.
                    print("Logging notification")
                    self.__notifications.logs.log(subscribed_zone.id)

        return True

    def __create_message(self, dns_zone_id):
        zone = self.__dns_zones.get(dns_zone_id)
        if not zone:
            return False

        return "Domain {0} has been resolved".format(zone.full_domain)
