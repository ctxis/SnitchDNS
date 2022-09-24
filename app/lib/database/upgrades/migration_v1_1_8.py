class DBMigration:
    def __init__(self, provider):
        self.__provider = provider

    def run(self):
        print("Upgrading to version v1.1.8...")
        self.__add_auth_types()
        return True

    def __add_auth_types(self):
        users = self.__provider.users()

        auth_types = [
            {'name': 'Azure'}
        ]

        for auth_type in auth_types:
            item = users.get_authtype(name=auth_type['name'])
            if not item:
                print("Adding auth type {0}".format(auth_type['name']))
                users.add_authtype(auth_type['name'])

        return True
