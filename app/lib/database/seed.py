from app.lib.notifications.managers.type_manager import NotificationTypeManager
from app.lib.base.provider import Provider
from app import version as app_version
from packaging import version
import app.lib.database.upgrades.migration_v1_0_1 as v1_0_1


class SeedDatabase:
    def run(self):
        self.__seed_notification_types()
        self.__run_db_update()
        return True

    def __seed_notification_types(self):
        print("Adding notification types...")
        data = [
            {'name': 'email', 'description': 'E-mail'},
            {'name': 'webpush', 'description': 'Web Push'},
            {'name': 'slack', 'description': 'Slack Webhooks'},
            {'name': 'teams', 'description': 'Teams Webhooks'},
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

    def __run_db_update(self):
        provider = Provider()
        settings = provider.settings()

        db_version = settings.get('db_version', '0.0.0')
        installed_version = version.parse(db_version)
        if installed_version >= version.parse(app_version.__version__):
            print("No database updates required")
            return True

        if installed_version < version.parse('1.0.1'):
            migration = v1_0_1.DBMigration(provider)
            if migration.run():
                settings.save('db_version', '1.0.1')

        return True
