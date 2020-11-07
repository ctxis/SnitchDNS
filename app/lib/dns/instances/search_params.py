import datetime
from urllib.parse import quote_plus


class SearchParams:
    def __init__(self, request=None, method='get'):
        self.__request = request
        self.__method = method.lower()
        if self.__method not in ['dict', 'get', 'post']:
            raise Exception("Coding Error: Invalid SearchParams() method: {0}".format(self.__method))

        self.__domain = None
        self.__source_ip = None
        self.__cls = None
        self.__type = None
        self.__matched = None
        self.__forwarded = None
        self.__date_from = None
        self.__date_to = None
        self.__time_from = None
        self.__time_to = None
        self.__page = None
        self.__per_page = None
        self.__user_id = None
        self.__blocked = None
        self.__tags = None
        self.__advanced = None
        self.__alias = None

        self.__load()

    def __load(self):
        self.domain = self.__get_param('domain', '')
        self.source_ip = self.__get_param('source_ip', '')
        self.cls = self.__get_param('cls', '')
        self.type = self.__get_param('type', '')
        self.matched = self.__get_param('matched', -1, type='int')
        self.forwarded = self.__get_param('forwarded', -1, type='int')
        self.blocked = self.__get_param('blocked', -1, type='int')
        self.date_from = self.__get_param('date_from', '')
        self.date_to = self.__get_param('date_to', '')
        self.time_from = self.__get_param('time_from', '')
        self.time_to = self.__get_param('time_to', '')
        self.page = self.__get_param('page', 1, type='int')
        self.per_page = self.__get_param('per_page', 20, type='int')
        self.user_id = self.__get_param('user_id', -1, type='int')
        self.tags = self.__get_param('tags', [], type='list')
        self.advanced = self.__get_param('advanced', 0, type='int')
        self.alias = self.__get_param('alias', '')

        if len(self.date_from) > 0 and len(self.time_from) == 0:
            self.time_from = '00:00:00'
        elif len(self.time_from) > 0 and len(self.time_from) != 8:
            self.time_from += ':00'

        if len(self.date_to) > 0 and len(self.time_to) == 0:
            self.time_to = '23:59:59'
        elif len(self.time_to) > 0 and len(self.time_to) != 8:
            self.time_to += ':59'

        if self.page <= 0:
            self.page = 1

        if isinstance(self.tags, str):
            self.tags = self.tags.split(',')
        self.tags = list(filter(None, self.tags))

    def __get_param(self, name, default, type='str'):
        if self.__request is None:
            return default

        value = default
        if self.__method in ['get', 'post']:
            if self.__method == 'get':
                value = self.__request.args.getlist(name) if type == 'list' else self.__request.args.get(name, value)
            elif self.__method == 'post':
                value = self.__request.form.getlist(name) if type == 'list' else self.__request.form.get(name, value)
        elif self.__method == 'dict':
            value = self.__request[name] if name in self.__request else default

        if type == 'int':
            value = int(value) if str(value).isdigit() else default

        return value

    def url(self):
        params = []

        params.append('domain=' + quote_plus(self.domain)) if len(self.domain) > 0 else False
        params.append('source_ip=' + quote_plus(self.source_ip)) if len(self.source_ip) > 0 else False
        params.append('cls=' + quote_plus(self.cls)) if len(self.cls) > 0 else False
        params.append('type=' + quote_plus(self.type)) if len(self.type) > 0 else False
        params.append('matched=' + quote_plus(str(self.matched))) if self.matched in [0, 1] else False
        params.append('forwarded=' + quote_plus(str(self.forwarded))) if self.forwarded in [0, 1] else False
        params.append('blocked=' + quote_plus(str(self.blocked))) if self.blocked in [0, 1] else False
        params.append('user_id=' + quote_plus(str(self.user_id))) if self.user_id >= 0 else False
        params.append('date_from=' + quote_plus(self.date_from)) if len(self.date_from) > 0 else False
        params.append('time_from=' + quote_plus(self.time_from)) if len(self.time_from) > 0 else False
        params.append('date_to=' + quote_plus(self.date_to)) if len(self.date_to) > 0 else False
        params.append('time_to=' + quote_plus(self.time_to)) if len(self.time_to) > 0 else False
        params.append('tags=' + '&tags='.join(self.tags)) if len(self.tags) > 0 else False
        params.append('alias=' + quote_plus(self.alias)) if len(self.alias) > 0 else False
        params.append('advanced=' + quote_plus(str(self.advanced))) if self.advanced == 1 else False
        params.append('page=')  # Must be last.

        return "&".join(params)

    @property
    def domain(self):
        return self.__domain

    @domain.setter
    def domain(self, value):
        self.__domain = value

    @property
    def source_ip(self):
        return self.__source_ip

    @source_ip.setter
    def source_ip(self, value):
        self.__source_ip = value

    @property
    def cls(self):
        return self.__cls

    @cls.setter
    def cls(self, value):
        self.__cls = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def matched(self):
        return self.__matched

    @matched.setter
    def matched(self, value):
        self.__matched = value

    @property
    def forwarded(self):
        return self.__forwarded

    @forwarded.setter
    def forwarded(self, value):
        self.__forwarded = value

    @property
    def date_from(self):
        return self.__date_from

    @date_from.setter
    def date_from(self, value):
        self.__date_from = value

    @property
    def date_to(self):
        return self.__date_to

    @date_to.setter
    def date_to(self, value):
        self.__date_to = value

    @property
    def time_from(self):
        return self.__time_from

    @time_from.setter
    def time_from(self, value):
        self.__time_from = value

    @property
    def time_to(self):
        return self.__time_to

    @time_to.setter
    def time_to(self, value):
        self.__time_to = value

    @property
    def full_date_from(self):
        value = ''
        try:
            value = datetime.datetime.strptime(self.date_from + ' ' + self.time_from, '%Y-%m-%d %H:%M:%S')
        except:
            pass
        return value

    @property
    def full_date_to(self):
        value = ''
        try:
            value = datetime.datetime.strptime(self.date_to + ' ' + self.time_to, '%Y-%m-%d %H:%M:%S')
        except:
            pass
        return value

    @property
    def page(self):
        return self.__page

    @page.setter
    def page(self, value):
        self.__page = value

    @property
    def per_page(self):
        return self.__per_page

    @per_page.setter
    def per_page(self, value):
        self.__per_page = value

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, value):
        self.__user_id = value

    @property
    def blocked(self):
        return self.__blocked

    @blocked.setter
    def blocked(self, value):
        self.__blocked = value

    @property
    def tags(self):
        return self.__tags

    @tags.setter
    def tags(self, value):
        self.__tags = value

    @property
    def advanced(self):
        return self.__advanced

    @advanced.setter
    def advanced(self, value):
        self.__advanced = value

    @property
    def alias(self):
        return self.__alias

    @alias.setter
    def alias(self, value):
        self.__alias = value

    def get(self, name):
        return getattr(self, name) if self.__is_property(name) else None

    def all_properties(self):
        # A lazy way to get all the properties of the class, so I could loop through them.
        properties = []
        for name in dir(self):
            if self.__is_property(name):
                properties.append(name)
        return properties

    def __is_property(self, name):
        return isinstance(getattr(type(self), name, None), property)
