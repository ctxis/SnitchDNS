from app.lib.models.tags import TagModel
from app.lib.dns.instances.tag import Tag
from sqlalchemy import desc, asc


class TagManager:
    def __get(self, id=None, user_id=None, name=None, order_column=None, order_by=None):
        query = TagModel.query

        if id is not None:
            query = query.filter(TagModel.id == id)

        if user_id is not None:
            query = query.filter(TagModel.user_id == user_id)

        if name is not None:
            if isinstance(name, list):
                # A list of tags has been passed.
                query = query.filter(TagModel.name.in_(name))
            else:
                query = query.filter(TagModel.name == name)

        if (order_column is not None) and (order_by is not None):
            order = None

            if order_column == 'id':
                order = asc(TagModel.id) if order_by == 'asc' else desc(TagModel.id)
            elif order_column == 'name':
                order = asc(TagModel.name) if order_by == 'asc' else desc(TagModel.name)

            if order is not None:
                query = query.order_by(order)

        return query.all()

    def __load(self, item):
        return Tag(item)

    def save(self, user_id, name):
        item = self.__get(user_id=user_id, name=name)
        if not item:
            item = Tag(TagModel())
            item.user_id = user_id
            item.name = name
            item.save()
        else:
            item = item[0]

        return item

    def get(self, tag_id):
        result = self.__get(id=tag_id)
        if len(result) == 0:
            return False

        return self.__load(result[0])

    def all(self, user_id=None, name=None, order_column=None, order_by=None):
        results = self.__get(user_id=user_id, name=name, order_column=order_column, order_by=order_by)
        tags = []
        for result in results:
            tags.append(self.__load(result))
        return tags

    def get_tag_ids(self, tags, user_id=None):
        results = self.__get(user_id=user_id, name=tags)
        ids = []
        for result in results:
            ids.append(result.id)

        return ids
