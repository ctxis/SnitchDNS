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

        self.__load()

    def __load(self):
        self.domain = self.__get_param('domain', '')
        self.source_ip = self.__get_param('source_ip', '')
        self.rclass = self.__get_param('rclass', '')
        self.type = self.__get_param('type', '')
        self.matched = self.__get_param('matched', -1, type='int')
        self.forwarded = self.__get_param('forwarded', -1, type='int')

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
