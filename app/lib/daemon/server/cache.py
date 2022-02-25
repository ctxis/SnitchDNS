import copy


class DNSCache:
    def __init__(self, state, settings, max_items):
        self.__enabled = state
        self.__settings = settings
        self.__cache = {}
        self.__max_items = max_items

    def get(self, domain, cls, type, log):
        if not self.__enabled:
            return False

        self.__check_cache_status()

        domain = domain.lower()
        if domain not in self.__cache:
            return False
        elif cls not in self.__cache[domain]:
            return False
        elif type not in self.__cache[domain][cls]:
            return False

        log.dns_zone_id = self.__cache[domain][cls][type]['__dns_zone_id']
        log.dns_record_id = self.__cache[domain][cls][type]['__dns_record_id']
        log.save()

        result = self.__cache[domain][cls][type]
        result['log'] = log

        return result

    def add(self, domain, cls, type, data):
        if not self.__enabled:
            return False

        self.__check_cache_status()

        domain = domain.lower()
        if not domain in self.__cache:
            self.__cache[domain] = {}

        if not cls in self.__cache[domain]:
            self.__cache[domain][cls] = {}

        if not type in self.__cache[domain][cls]:
            cache = copy.deepcopy(data)
            cache['__dns_zone_id'] = data['log'].dns_zone_id
            cache['__dns_record_id'] = data['log'].dns_record_id
            cache['log'] = None
            self.__cache[domain][cls][type] = cache

        return True

    def __check_cache_status(self):
        if self.__settings.get('dns_clear_cache', False, type=bool) is True:
            self.__cache = {}
            self.__settings.save('dns_clear_cache', False)

        if len(self.__cache) >= self.__max_items:
            self.__cache = {}

        return True
