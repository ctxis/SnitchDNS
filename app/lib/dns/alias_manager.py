from app.lib.models.aliases import AliasModel
from app.lib.dns.instances.alias import Alias
from app.lib.dns.helpers.shared import SharedHelper
from sqlalchemy import desc, asc


class AliasManager(SharedHelper):
    def __get(self, id=None, user_id=None, ip=None, name=None, order_column=None, order_by=None):
        query = AliasModel.query

        if id is not None:
            query = query.filter(AliasModel.id == id)

        if user_id is not None:
            query = query.filter(AliasModel.user_id == user_id)

        if ip is not None:
            query = query.filter(AliasModel.ip == ip)

        if name is not None:
            query = query.filter(AliasModel.name == name)

        if (order_column is not None) and (order_by is not None):
            order = None

            if order_column == 'id':
                order = asc(AliasModel.id) if order_by == 'asc' else desc(AliasModel.id)
            elif order_column == 'name':
                order = asc(AliasModel.name) if order_by == 'asc' else desc(AliasModel.name)

            if order is not None:
                query = query.order_by(order)

        return query.all()

    def __load(self, item):
        return Alias(item)

    def save(self, user_id, ip, name):
        item = self.__get(user_id=user_id, ip=ip)
        if not item:
            item = Alias(AliasModel())
            item.user_id = user_id
            item.ip = ip
        else:
            item = self.__load(item[0])

        item.name = name
        item.save()
        return item

    def update(self, alias_id, user_id=None, ip=None, name=None):
        alias = self.get(alias_id)
        if not alias:
            return False

        if user_id is not None:
            alias.user_id = user_id

        if ip is not None:
            alias.ip = ip

        if name is not None:
            alias.name = name

        alias.save()
        return alias

    def get(self, alias_id, user_id=None, ip=None, name=None):
        result = self.__get(id=alias_id, user_id=user_id, ip=ip, name=name)
        if len(result) == 0:
            return False

        return self.__load(result[0])

    def all(self, user_id=None, ip=None, name=None, order_column=None, order_by=None):
        results = self.__get(user_id=user_id, ip=ip, name=name, order_column=order_column, order_by=order_by)
        aliases = []
        for result in results:
            aliases.append(self.__load(result))
        return aliases

    def can_access(self, alias_id, user_id):
        return len(self.__get(id=alias_id, user_id=user_id)) > 0

    def delete(self, alias_id, user_id=None):
        results = self.__get(id=alias_id, user_id=user_id)
        if not results:
            return False

        self.__load(results[0]).delete()
        return True
