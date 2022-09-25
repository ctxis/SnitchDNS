from app.lib.models.user import UserModel
from sqlalchemy import or_
from app import db


class DBMigration:
    def __init__(self, provider):
        self.__provider = provider

    def run(self):
        print("Upgrading to version v1.1.9...")
        self.__add_auth_types()
        self.__fix_column_values()
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

    def __fix_column_values(self):
        print("Fixing null azure columns")
        # Fix any issues with new columns/fields.
        results = UserModel.query.filter(or_(UserModel.access_token == None, UserModel.access_token_expiration == None)).all()
        for result in results:
            result.access_token = ''
            result.access_token_expiration = 0
            db.session.commit()
