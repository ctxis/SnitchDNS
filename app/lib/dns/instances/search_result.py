import datetime


class SearchResult:
    def __init__(self, result):
        self.__result = result

    @property
    def domain(self):
        return self.__result.domain

    @property
    def source_ip(self):
        return self.__result.source_ip

    @property
    def rclass(self):
        return self.__result.rclass

    @property
    def type(self):
        return self.__result.type

    def created_at(self, format):
        date = ''
        try:
            date = datetime.datetime.strptime(self.__result.created_at, '%Y-%m-%d %H:%M:%S.%f').strftime(format)
        except:
            pass
        return date

    @property
    def forwarded(self):
        return self.__result.forwarded

    @property
    def matched(self):
        return self.__result.found
