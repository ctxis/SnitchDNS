from urllib.parse import urlencode


class SearchParams:
    def __init__(self, request):
        self.__request = request

        self.__domain = None
        self.__source_ip = None
        self.__rclass = None
        self.__type = None

        self.__load()

    def __load(self):
        self.__domain = self.__request.args.get('domain', '')
        self.__source_ip = self.__request.args.get('source_ip', '')
        self.__rclass = self.__request.args.get('rclass', '')
        self.__type = self.__request.args.get('type', '')

    def url(self):
        params = [
            'domain=' + urlencode(self.domain),
            'source_ip=' + urlencode(self.source_ip),
            'rclass=' + urlencode(self.rclass),
            'type=' + urlencode(self.type)
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
