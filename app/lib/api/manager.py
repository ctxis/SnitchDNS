import string
import random
from app.lib.models.api import ApiKeyModel
from app.lib.api.instances.apikey import ApiKey


class ApiManager:
    def create(self):
        item = ApiKey(ApiKeyModel())
        item.save()
        return item

    def add(self, user_id, name):
        apikey = self.create()
        apikey.user_id = user_id
        apikey.name = name
        apikey.enabled = True
        apikey.apikey = self.__generate_key()
        apikey.save()

        return apikey

    def __generate_key(self, length=32):
        return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=length))

    def __get(self, id=None, user_id=None, name=None, apikey=None, enabled=None):
        query = ApiKeyModel.query

        if id is not None:
            query = query.filter(ApiKeyModel.id == id)

        if user_id is not None:
            query = query.filter(ApiKeyModel.user_id == user_id)

        if name is not None:
            query = query.filter(ApiKeyModel.name == name)

        if apikey is not None:
            query = query.filter(ApiKeyModel.apikey == apikey)

        if enabled is not None:
            query = query.filter(ApiKeyModel.enabled == enabled)

        return query.all()

    def all(self, user_id=None):
        results = self.__get(user_id=user_id)
        keys = []
        for result in results:
            keys.append(self.__load(result))

        return keys

    def can_access(self, key_id, user_id, is_admin=False):
        if is_admin:
            # SuperUser
            return True
        return self.__get(id=key_id, user_id=user_id) is not None

    def __load(self, item):
        return ApiKey(item)

    def get(self, key_id):
        results = self.__get(id=key_id)
        if len(results) == 0:
            return False

        return self.__load(results[0])

    def delete(self, key_id):
        key = self.get(key_id)
        if not key:
            return False

        key.delete()
        return True
