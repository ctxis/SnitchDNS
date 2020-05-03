import datetime
from urllib.parse import quote_plus


class SearchParams:
    def __init__(self, request):
        self.__request = request

        self.__domain = None
        self.__source_ip = None
        self.__rclass = None
        self.__type = None
        self.__matched = None
        self.__forwarded = None
        self.__date_from = None
        self.__date_to = None
        self.__time_from = None
        self.__time_to = None
        self.__page = None
        self.__per_page = None

        self.__load()

    def __load(self):
        self.domain = self.__get_param('domain', '')
        self.source_ip = self.__get_param('source_ip', '')
        self.rclass = self.__get_param('rclass', '')
        self.type = self.__get_param('type', '')
        self.matched = self.__get_param('matched', -1, type='int')
        self.forwarded = self.__get_param('forwarded', -1, type='int')
        self.date_from = self.__get_param('date_from', '')
        self.date_to = self.__get_param('date_to', '')
        self.time_from = self.__get_param('time_from', '')
        self.time_to = self.__get_param('time_to', '')
        self.page = self.__get_param('page', 1, type='int')
        self.per_page = self.__get_param('per_page', 10, type='int')

        if len(self.date_from) > 0 and len(self.time_from) == 0:
            self.time_from = '00:00:00'
        elif len(self.time_from) > 0:
            self.time_from += ':00'

        if len(self.date_to) > 0 and len(self.time_to) == 0:
            self.time_to = '23:59:59'
        elif len(self.time_to) > 0:
            self.time_to += ':59'

        if self.page <= 0:
            self.page = 1

    def __get_param(self, name, default, type='str'):
        value = self.__request.args.get(name, default)
        if type == 'int':
            value = int(value) if str(value).isdigit() else default

        return value

    def url(self):
        params = []

        params.append('domain=' + quote_plus(self.domain)) if len(self.domain) > 0 else False
        params.append('source_ip=' + quote_plus(self.source_ip)) if len(self.source_ip) > 0 else False
        params.append('rclass=' + quote_plus(self.rclass)) if len(self.rclass) > 0 else False
        params.append('type=' + quote_plus(self.type)) if len(self.type) > 0 else False
        params.append('matched=' + quote_plus(self.matched)) if self.matched in [0, 1] else False
        params.append('forwarded=' + quote_plus(self.forwarded)) if self.forwarded in [0, 1] else False
        params.append('date_from=' + quote_plus(self.date_from)) if len(self.date_from) > 0 else False
        params.append('time_from=' + quote_plus(self.time_from)) if len(self.time_from) > 0 else False
        params.append('date_to=' + quote_plus(self.date_to)) if len(self.date_to) > 0 else False
        params.append('time_to=' + quote_plus(self.time_to)) if len(self.time_to) > 0 else False
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
    def rclass(self):
        return self.__rclass

    @rclass.setter
    def rclass(self, value):
        self.__rclass = value

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
