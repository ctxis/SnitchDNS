from twisted.names import dns, error
from twisted.internet import defer


class DatabaseDNSResolver:
    def __init__(self, app, dns_manager, logging):
        self.__app = app
        self.__dns_manager = dns_manager
        self.__logging = logging

    def query(self, query, timeout=None):
        data = self.__lookup(query)
        if data['found']:
            return defer.succeed((data['answers'], data['authority'], data['additional']))
        return defer.fail(error.DomainError())

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
                data['found'] = True
                data['answers'].append(answer)

        return data

    def __find(self, query):
        answer = None

        domain = str(query.name.name.decode('utf-8'))
        type = str(dns.QUERY_TYPES.get(query.type, None))
        cls = str(dns.QUERY_CLASSES.get(query.cls, None))

        # Try to find the logging record.
        log = self.__logging.find(None, domain, cls, type, False)
        if not log:
            # TODO / Log error, as this record won't be reliable.
            pass

        # Split the query into an array.
        # 'something.snitch.contextis.com' will become:
        #   0 => something
        #   1 => snitch
        #   2 => contextis
        #   3 => com
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
                # Save log item.
                if log:
                    log.dns_zone_id = db_zone.id
                    log.save()

                db_record = self.__dns_manager.find_record(db_zone, cls, type)
                if db_record:
                    # We found a match.
                    answer = self.__build_answer(query, db_zone, db_record)
                    if not answer:
                        # TODO / Something went terribly wrong. If it dies, it dies.
                        pass

                    # Update log item.
                    log.dns_record_id = db_record.id
                    log.found = True
                    log.completed = True
                    log.data = str(answer)
                    log.save()
                    break

            # Remove the first element of the array, to continue searching for a matching domain.
            parts.pop(0)

        return answer

    def __build_answer(self, query, db_zone, db_record):
        record = None
        if query.type == dns.A:
            record = dns.Record_A(address=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.A6:
            pass
        elif query.type == dns.AAAA:
            record = dns.Record_AAAA(address=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.AFSDB:
            pass
        elif query.type == dns.CNAME:
            record = dns.Record_CNAME(name=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.DNAME:
            record = dns.Record_DNAME(name=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.HINFO:
            pass
        elif query.type == dns.MB:
            record = dns.Record_MB(name=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.MD:
            record = dns.Record_MD(name=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.MF:
            record = dns.Record_MF(name=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.MG:
            record = dns.Record_MG(name=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.MINFO:
            pass
        elif query.type == dns.MR:
            record = dns.Record_MR(name=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.MX:
            pass
        elif query.type == dns.NAPTR:
            pass
        elif query.type == dns.NS:
            record = dns.Record_NS(name=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.NULL:
            record = dns.Record_NULL(payload=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.PTR:
            record = dns.Record_PTR(name=db_record.data, ttl=db_record.ttl)
        elif query.type == dns.RP:
            pass
        elif query.type == dns.SOA:
            pass
        elif query.type == dns.SPF:
            pass
        elif query.type == dns.SRV:
            pass
        elif query.type == dns.SSHFP:
            pass
        elif query.type == dns.TSIG:
            pass
        elif query.type == dns.TXT:
            pass
        elif query.type == dns.WKS:
            pass
        else:
            pass

        return dns.RRHeader(
            name=query.name.name,
            type=query.type,
            cls=query.cls,
            ttl=db_record.ttl,
            payload=record
        ) if record else None

