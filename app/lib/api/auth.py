from flask import request
from flask_login import login_user
from app.lib.base.provider import Provider


class ApiAuth:
    def auth(self, auto_login_user):
        apikey = request.headers['X-SnitchDNS-Auth'].strip() if 'X-SnitchDNS-Auth' in request.headers else ''
        if len(apikey) == 0:
            return False

        user = self.__auth(apikey)
        if not user:
            return False

        if auto_login_user:
            login_user(user)

        return True

    def __auth(self, apikey):
        if len(apikey) == 0:
            return False

        provider = Provider()
        api = provider.api()
        users = provider.users()

        key = api.find(apikey)
        if not key:
            return False
        elif not key.enabled:
            return False

        user = users.get_user(key.user_id)
        if not user:
            return False
        elif not user.active:
            return False

        return user
