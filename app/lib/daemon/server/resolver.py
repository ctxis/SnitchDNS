from twisted.names import dns, error
from twisted.internet import defer
from app.lib.dns.records.record_snitch import Record_SNITCH


class DatabaseDNSResolver:
    def __init__(self, app, dns_manager, logging):
        self.__app = app
        self.__dns_manager = dns_manager
        self.__logging = logging

    def query(self, query, timeout=None):
        data = self.__lookup(query)
        if data['found'] or data['stop']:
            return defer.succeed((data['answers'], data['authority'], data['additional']))
        return defer.fail(error.DomainError())

    def __lookup(self, query):
        data = {
            'found': False,
            'stop': False,
            'answers': [],
            'authority': [],
            'additional': []
        }

        with self.__app.app_context():
            lookup = self.__find(query)
            data['answers'] = lookup['answers']
            data['found'] = (len(data['answers']) > 0)
            data['stop'] = (lookup['result'] == 'stop')

            log = lookup['log']
            log.found = data['found']

            log.forwarded = self.__dns_manager.is_forwarding_enabled
            if data['found'] or data['stop']:
                log.forwarded = False
            log.save()

            # At this point, add a dict as an answer that will hold the track of the database record log.
            # I don't like this and this isn't my proudest moment. But I can't access the Source IP from here.
            data['answers'].append(Record_SNITCH(name='SNITCH', ttl=log.id))
        return data

    def __find(self, query):
        answers = []
        lookup_result = ''

        domain = str(query.name.name.decode('utf-8'))
        type = str(dns.QUERY_TYPES.get(query.type, None))
        cls = str(dns.QUERY_CLASSES.get(query.cls, None))

        # Create a new logging record.
        log = self.__logging.create(domain=domain, type=type, cls=cls)

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

            # Remove the first element of the array, to continue searching for a matching domain.
            parts.pop(0)

            db_zone = self.__dns_manager.find_zone(path, domain)
            if not db_zone:
                # Look for the next domain.
                continue

            # Log the identified zone id.
            log.dns_zone_id = db_zone.id

            # Look for more than one records (nameservers, mx records etc may have more than one).
            db_records = self.__dns_manager.find_all_records(db_zone, cls, type, active=True)
            if len(db_records) == 0:
                # No active matching records found.
                # Determine whether we can forward this record or not.
                lookup_result = 'continue' if db_zone.forwarding else 'stop'
                break

            for db_record in db_records:
                # This will hold the last db_record but we don't really care about that.
                log.dns_record_id = db_record.id

                answer = self.__build_answer(query, db_zone, db_record)
                if not answer:
                    # Something went terribly wrong. If it dies, it dies.
                    # This can be caused if the UI allows more record types to be created than the
                    # __build_answer() method supports. Probably I should add some logging here, but NOT TODAY!
                    continue

                answers.append(answer)

            # If we reached this point it means that we've already matched at least one db_zone, therefore there's not
            # need to keep looking.
            break

        log.save()
        return {
            'result': lookup_result if len(lookup_result) > 0 else 'continue',
            'answers': answers,
            'log': log
        }

    def __build_answer(self, query, db_zone, db_record):
        record = None
        if query.type == dns.A:
            record = dns.Record_A(
                address=db_record.property('address'),
                ttl=db_record.ttl
            )
        elif query.type == dns.AAAA:
            record = dns.Record_AAAA(
                address=db_record.property('address'),
                ttl=db_record.ttl
            )
        elif query.type == dns.AFSDB:
            record = dns.Record_AFSDB(
                subtype=int(db_record.property('subtype')),
                hostname=db_record.property('hostname')
            )
        elif query.type == dns.CNAME:
            record = dns.Record_CNAME(
                name=db_record.property('name'),
                ttl=db_record.ttl
            )
        elif query.type == dns.DNAME:
            record = dns.Record_DNAME(
                name=db_record.property('name'),
                ttl=db_record.ttl
            )
        elif query.type == dns.HINFO:
            record = dns.Record_HINFO(
                cpu=db_record.property('cpu').encode(),
                os=db_record.property('os').encode()
            )
        elif query.type == dns.MX:
            record = dns.Record_MX(
                preference=int(db_record.property('preference')),
                name=db_record.property('name')
            )
        elif query.type == dns.NAPTR:
            record = dns.Record_NAPTR(
                order=int(db_record.property('order')),
                preference=int(db_record.property('preference')),
                flags=db_record.property('flags').encode(),
                service=db_record.property('service').encode(),
                regexp=db_record.property('regexp').encode(),
                replacement=db_record.property('replacement')
            )
        elif query.type == dns.NS:
            record = dns.Record_NS(
                name=db_record.property('name'),
                ttl=db_record.ttl
            )
        elif query.type == dns.PTR:
            record = dns.Record_PTR(
                name=db_record.property('name'),
                ttl=db_record.ttl
            )
        elif query.type == dns.RP:
            record = dns.Record_RP(
                mbox=db_record.property('mbox'),
                txt=db_record.property('txt')
            )
        elif query.type == dns.SOA:
            record = dns.Record_SOA(
                mname=db_record.property('mname'),
                rname=db_record.property('rname'),
                serial=int(db_record.property('serial')),
                refresh=int(db_record.property('refresh')),
                retry=int(db_record.property('retry')),
                expire=int(db_record.property('expire')),
                minimum=int(db_record.property('minimum'))
            )
        elif query.type == dns.SPF:
            record = dns.Record_SPF(
                db_record.property('data').encode()
            )
        elif query.type == dns.SRV:
            record = dns.Record_SRV(
                priority=int(db_record.property('priority')),
                port=int(db_record.property('port')),
                weight=int(db_record.property('weight')),
                target=db_record.property('target')
            )
        elif query.type == dns.SSHFP:
            record = dns.Record_SSHFP(
                algorithm=int(db_record.property('algorithm')),
                fingerprintType=int(db_record.property('fingerprint_type')),
                fingerprint=db_record.property('fingerprint').encode()
            )
        elif query.type == dns.TSIG:
            record = dns.Record_TSIG(
                algorithm=db_record.property('algorithm').encode(),
                timeSigned=int(db_record.property('timesigned')),
                fudge=int(db_record.property('fudge')),
                originalID=int(db_record.property('original_id')),
                MAC=db_record.property('mac').encode(),
                otherData=db_record.property('other_data').encode()
            )
        elif query.type == dns.TXT:
            record = dns.Record_TXT(
                db_record.property('data').encode()
            )
        else:
            pass

        if not record:
            return None

        answer = dns.RRHeader(name=query.name.name, type=query.type, cls=query.cls, ttl=db_record.ttl, payload=record)
        return answer
