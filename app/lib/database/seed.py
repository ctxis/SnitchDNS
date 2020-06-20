from app.lib.notifications.managers.type_manager import NotificationTypeManager


class SeedDatabase:
    def run(self):
        self.__seed_notification_types()
        return True

    def __seed_notification_types(self):
        print("Adding notification types...")
        data = [
            {'name': 'email', 'description': 'E-mail'},
            {'name': 'webpush', 'description': 'Web Push'},
            {'name': 'slack', 'description': 'Slack Webhooks'}
        ]

        type_manager = NotificationTypeManager()
        for item in data:
            type = type_manager.get(name=item['name'])
            if type:
                # Found, skip.
                print("Type {0} already exists - skipping".format(item['name']))
                continue

            print("Creating type {0}".format(item['name']))
            type = type_manager.create()
            type.name = item['name']
            type.description = item['description']
            type.save()

        return True
