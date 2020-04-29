import datetime
from urllib.parse import urlencode


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

    def __get_param(self, name, default, type='str'):
        value = self.__request.args.get(name, default)
        if type == 'int':
            value = int(value) if str(value).isdigit() else default

        return value

    def url(self):
        params = [
            'domain=' + urlencode(self.domain),
            'source_ip=' + urlencode(self.source_ip),
            'rclass=' + urlencode(self.rclass),
            'type=' + urlencode(self.type),
            'matched=' + urlencode(self.matched)
        ]
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
            value = datetime.datetime.strptime(self.date_from + ' ' + self.time_from, '%Y-%m-%d %H:%M')
        except:
            pass
        return value

    @property
    def full_date_to(self):
        value = ''
        try:
            value = datetime.datetime.strptime(self.date_to + ' ' + self.time_to, '%Y-%m-%d %H:%M')
        except:
            pass
        return value
