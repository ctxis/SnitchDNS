from app.lib.models.notifications import NotificationTypeModel
from app.lib.notifications.instances.notification_type import NotificationType


class NotificationTypeManager:
    def __get(self, id=None, name=None, description=None):
        query = NotificationTypeModel.query

        if id is not None:
            query = query.filter(NotificationTypeModel.id == id)

        if name is not None:
            query = query.filter(NotificationTypeModel.name == name)

        if description is not None:
            query = query.filter(NotificationTypeModel.description == description)

        return query.all()

    def __load(self, item):
        return NotificationType(item)

    def get(self, id=None, name=None):
        if (id is None) and (name is None):
            # Have to define at least one.
            return False

        results = self.__get(id=id, name=name)
        return self.__load(results[0]) if len(results) > 0 else False

    def all(self):
        results = self.__get()
        items = []
        for result in results:
            items.append(self.__load(result))
        return results

    def create(self):
        item = NotificationType(NotificationTypeModel())
        item.save()
        return item

    def get_type_name(self, type_id):
        type = self.get(id=type_id)
        if not type:
            return False

        return type.name
