from twisted.names import dns


class DatabaseDNSResolver:
    def __init__(self, app, dns_manager):
        self.__app = app
        self.__dns_manager = dns_manager

    def query(self, query, timeout=None):
        data = self.__lookup(query)
        return data['answers'], data['authority'], data['additional']

    def __lookup(self, query):
        data = {
            'found': False,
            'answers': [],
            'authority': [],
            'additional': []
        }

        with self.__app.app_context():
            answer = self.__find(query)
            if answer:
                data['answers'].append(answer)

        return data

    def __find(self, query):
        answer = None

        # Split the query into an array.
        # 'something.snitch.contextis.com' will become:
        #   0 => something
        #   1 => snitch
        #   2 => contextis
        #   3 => com
        domain = str(query.name.name.decode('utf-8'))
        parts = domain.split('.')

        # The following loop will lookup from the longest to the shortest domain, for example:
        #   1 => something.snitch.contextis.com
        #   2 => snitch.contextis.com
        #   3 => contextis
        #   4 => com
        # Whichever it finds first, that's the one it will return and exit.
        while len(parts) > 0:
            # Join all the current items to re-create the domain.
            path = ".".join(parts)
            db_zone = self.__dns_manager.find_zone(path, domain)
            if db_zone:
                db_record = self.__dns_manager.find_record(
                    db_zone,
                    str(dns.QUERY_CLASSES.get(query.cls, None)),
                    str(dns.QUERY_TYPES.get(query.type, None))
                )

                if db_record:
                    # We found a match.
                    answer = self.__build_answer(query, db_zone, db_record)
                    break

            # Remove the first element of the array, to continue searching for a matching domain.
            parts.pop(0)

        return answer

    def __build_answer(self, query, db_zone, db_record):
        record = None
        if query.type == dns.A:
            record = dns.Record_A(address=db_record.data, ttl=db_record.ttl)

        return dns.RRHeader(name=query.name.name, type=query.type, cls=query.cls, ttl=db_record.ttl, payload=record)

