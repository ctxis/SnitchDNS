from sqlalchemy import asc, desc
from app.lib.models.logging import LoggingErrors
from app.lib.log.instances.log_error import LogError


class LoggingManager:
    def __init__(self, users):
        self.__users = users
        self.__cache_users = {0: 'Anonymous'}

    def __get_errors(self, id=None, user_id=None, order_by=None, sort_order=None, page=None, per_page=None):
        query = LoggingErrors.query

        if id is not None:
            query = query.filter(LoggingErrors.id == id)

        if user_id is not None:
            query = query.filter(LoggingErrors.user_id == user_id)

        order = None
        if order_by is not None:
            if order_by == 'id':
                order = asc(LoggingErrors.id) if sort_order == 'asc' else desc(LoggingErrors.id)

        if order is None:
            order = asc(LoggingErrors.id)

        query = query.order_by(order)

        if (page is not None) and (per_page is not None):
            results = query.paginate(page, per_page, False)
        else:
            results = query.all()

        return results

    def __load_error(self, item):
        log = LogError(item)
        log.username = self.__cache_users[item.user_id]
        return log

    def log_error(self, user_id, description, details):
        item = LogError(LoggingErrors())
        item.user_id = user_id
        item.description = description
        item.details = details
        item.save()

        return item

    def view_errors(self, page, per_page):
        records = self.__get_errors(order_by='id', sort_order='desc', page=page, per_page=per_page)
        for record in records.items:
            if record.user_id not in self.__cache_users:
                self.__cache_users[record.user_id] = self.__users.get_user(record.user_id).username
            record.username = self.__cache_users[record.user_id]
        return records
