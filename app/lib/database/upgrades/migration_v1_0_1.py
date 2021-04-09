class DBMigration:
    def __init__(self, provider):
        self.__provider = provider

    def run(self):
        print("Upgrading to version v1.0.1...")
        self.__add_auth_types()
        self.__migrate_existing_users()
        return True

    def __add_auth_types(self):
        users = self.__provider.users()

        auth_types = [
            {'name': 'Local'},
            {'name': 'LDAP'}
        ]

        for auth_type in auth_types:
            item = users.get_authtype(name=auth_type['name'])
            if not item:
                print("Adding auth type {0}".format(auth_type['name']))
                users.add_authtype(auth_type['name'])

        return True

    def __migrate_existing_users(self):
        users = self.__provider.users()

        all_users = users.all()
        for user in all_users:
            method = 'Local' if user.ldap == 0 else 'LDAP'
            print("Migrating user {0} to auth type {1}".format(user.username, method))
            users.set_auth_method_by_name(user.id, method)

        return True
