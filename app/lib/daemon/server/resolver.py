from twisted.names import dns, error
from twisted.names.dns import REV_TYPES
from twisted.internet import defer
from app.lib.dns.records.record_snitch import Record_SNITCH
from app.lib.dns.records.record_caa import Record_CAA


class DatabaseDNSResolver:
    def __init__(self, app, dns_manager, logging, cache):
        self.__app = app
        self.__dns_manager = dns_manager
        self.__logging = logging
        self.__cache = cache

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
            data['found'] = lookup['found']
            data['stop'] = (lookup['result'] == 'stop')

            log = lookup['log']
            log.found = data['found']

            log.forwarded = self.__dns_manager.is_forwarding_enabled
            if data['found'] or data['stop']:
                log.forwarded = False
            log.save()

            if data['found'] and len(data['answers']) == 0:
                data['authority'] = lookup['soa_answers']

            # At this point, add a dict as an answer that will hold the track of the database record log.
            # I don't like this and this isn't my proudest moment. But I can't access the Source IP from here.
            data['answers'].append(Record_SNITCH(name='SNITCH', ttl=log.id))
        return data

    def __find(self, query):
        answers = []
        soa_answers = []
        lookup_result = ''
        found = False

        domain = str(query.name.name.decode('utf-8'))
        type = str(dns.QUERY_TYPES.get(query.type, None))
        cls = str(dns.QUERY_CLASSES.get(query.cls, None))

        # Create a new logging record.
        log = self.__logging.create(domain=domain, type=type, cls=cls)

        cached_result = self.__cache.get(domain, cls, type, log)
        if cached_result:
            return cached_result

        # Before we start checking the domain part by part, check it against any regex domains.
        db_zone = self.__dns_manager.find_zone_regex(domain)
        if db_zone:
            lookup_result, answers, log = self.__get_zone_answers(db_zone, query, cls, type, log)
        else:
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
                path = ".".join(parts).lower()

                # Remove the first element of the array, to continue searching for a matching domain.
                parts.pop(0)

                db_zone = self.__dns_manager.find_zone(path, domain.lower())
                if db_zone:
                    found = True
                    lookup_result, answers, log = self.__get_zone_answers(db_zone, query, cls, type, log)
                    if len(answers) == 0:
                        soa_lookup_result, soa_answers, soa_log = self.__get_zone_answers(db_zone, query, cls, 'SOA', None)
                    break

        log.save()

        result = {
            'result': lookup_result if len(lookup_result) > 0 else 'continue',
            'answers': answers,
            'soa_answers': soa_answers,
            'log': log,
            'found': found
        }

        self.__cache.add(domain, cls, type, result)
        return result

    def __get_zone_answers(self, db_zone, query, cls, type, log):
        answers = []
        lookup_result = ''

        if log:
            log.dns_zone_id = db_zone.id

        db_records = self.__get_records(db_zone, cls, type)
        if len(db_records) == 0:
            # If we still haven't found anything (no matches), determine whether we can forward this record or not.
            lookup_result = 'continue' if db_zone.forwarding else 'stop'
        else:
            has_cname = False
            for db_record in db_records:
                # This will hold the last db_record but we don't really care about that.
                if log:
                    log.dns_record_id = db_record.id

                if has_cname is False and db_record.type == 'CNAME':
                    has_cname = True
                answer = self.__build_answer(query, db_zone, db_record, is_conditional_response=self.__is_conditional_response(db_record), has_cname=has_cname)
                if not answer:
                    # Something went terribly wrong. If it dies, it dies.
                    # This can be caused if the UI allows more record types to be created than the
                    # __build_answer() method supports. Probably I should add some logging here, but NOT TODAY!
                    continue

                answers.append(answer)

        return lookup_result, answers, log

    def __is_conditional_response(self, db_record):
        if not db_record.has_conditional_responses:
            return False

        db_record.conditional_count += 1
        db_record.save()

        if db_record.conditional_count < db_record.conditional_limit:
            return False

        if db_record.conditional_reset:
            db_record.conditional_count = 0
            db_record.save()

        return True

    def __get_records(self, db_zone, cls, type):
        # First look for a CNAME.
        redir_records = []
        records = self.__dns_manager.find_all_records(db_zone, cls, 'CNAME', active=True)
        if len(records) == 0:
            records = self.__dns_manager.find_all_records(db_zone, cls, type, active=True)
        else:
            redir_domain = records[0].property('name', '')
            if len(redir_domain) > 0:
                redir_zone = self.__dns_manager.find_zone(redir_domain, '', validate_catch_all=False)
                if redir_zone:
                    # We have an entry for this domain. Lookup the requested record there.
                    redir_records = self.__dns_manager.find_all_records(redir_zone, cls, type, active=True)

        return records + redir_records

    def __build_answer(self, query, db_zone, db_record, is_conditional_response=False, has_cname=False):
        record = None
        # Calculate the query type (in case it's a request for A but a CNAME is returned).
        query_type = REV_TYPES[db_record.type]
        query_domain = None
        if has_cname and db_record.type != 'CNAME':
            query_zone = self.__dns_manager.get_zone(db_record.dns_zone_id)
            query_domain = None if query_zone is False else query_zone.domain

        if query_type == dns.A:
            record = dns.Record_A(
                address=db_record.property('address', conditional=is_conditional_response),
                ttl=db_record.ttl
            )
        elif query_type == dns.AAAA:
            record = dns.Record_AAAA(
                address=db_record.property('address', conditional=is_conditional_response),
                ttl=db_record.ttl
            )
        elif query_type == dns.AFSDB:
            record = dns.Record_AFSDB(
                subtype=int(db_record.property('subtype', conditional=is_conditional_response)),
                hostname=db_record.property('hostname', conditional=is_conditional_response)
            )
        elif query_type == dns.CNAME:
            record = dns.Record_CNAME(
                name=db_record.property('name', conditional=is_conditional_response),
                ttl=db_record.ttl
            )
        elif query_type == dns.DNAME:
            record = dns.Record_DNAME(
                name=db_record.property('name', conditional=is_conditional_response),
                ttl=db_record.ttl
            )
        elif query_type == dns.HINFO:
            record = dns.Record_HINFO(
                cpu=db_record.property('cpu', conditional=is_conditional_response).encode(),
                os=db_record.property('os', conditional=is_conditional_response).encode()
            )
        elif query_type == dns.MX:
            record = dns.Record_MX(
                preference=int(db_record.property('preference', conditional=is_conditional_response)),
                name=db_record.property('name', conditional=is_conditional_response)
            )
        elif query_type == dns.NAPTR:
            record = dns.Record_NAPTR(
                order=int(db_record.property('order', conditional=is_conditional_response)),
                preference=int(db_record.property('preference', conditional=is_conditional_response)),
                flags=db_record.property('flags', conditional=is_conditional_response).encode(),
                service=db_record.property('service', conditional=is_conditional_response).encode(),
                regexp=db_record.property('regexp', conditional=is_conditional_response).encode(),
                replacement=db_record.property('replacement', conditional=is_conditional_response)
            )
        elif query_type == dns.NS:
            record = dns.Record_NS(
                name=db_record.property('name', conditional=is_conditional_response),
                ttl=db_record.ttl
            )
        elif query_type == dns.PTR:
            record = dns.Record_PTR(
                name=db_record.property('name', conditional=is_conditional_response),
                ttl=db_record.ttl
            )
        elif query_type == dns.RP:
            record = dns.Record_RP(
                mbox=db_record.property('mbox', conditional=is_conditional_response),
                txt=db_record.property('txt', conditional=is_conditional_response)
            )
        elif query_type == dns.SOA:
            record = dns.Record_SOA(
                mname=db_record.property('mname', conditional=is_conditional_response),
                rname=db_record.property('rname', conditional=is_conditional_response),
                serial=int(db_record.property('serial', conditional=is_conditional_response)),
                refresh=int(db_record.property('refresh', conditional=is_conditional_response)),
                retry=int(db_record.property('retry', conditional=is_conditional_response)),
                expire=int(db_record.property('expire', conditional=is_conditional_response)),
                minimum=int(db_record.property('minimum', conditional=is_conditional_response))
            )
        elif query_type == dns.SPF:
            record = dns.Record_SPF(
                db_record.property('data', conditional=is_conditional_response).encode()
            )
        elif query_type == dns.SRV:
            record = dns.Record_SRV(
                priority=int(db_record.property('priority', conditional=is_conditional_response)),
                port=int(db_record.property('port', conditional=is_conditional_response)),
                weight=int(db_record.property('weight', conditional=is_conditional_response)),
                target=db_record.property('target', conditional=is_conditional_response)
            )
        elif query_type == dns.SSHFP:
            record = dns.Record_SSHFP(
                algorithm=int(db_record.property('algorithm', conditional=is_conditional_response)),
                fingerprintType=int(db_record.property('fingerprint_type', conditional=is_conditional_response)),
                fingerprint=db_record.property('fingerprint', conditional=is_conditional_response).encode()
            )
        elif query_type == dns.TSIG:
            record = dns.Record_TSIG(
                algorithm=db_record.property('algorithm', conditional=is_conditional_response).encode(),
                timeSigned=int(db_record.property('timesigned', conditional=is_conditional_response)),
                fudge=int(db_record.property('fudge', conditional=is_conditional_response)),
                originalID=int(db_record.property('original_id', conditional=is_conditional_response)),
                MAC=db_record.property('mac', conditional=is_conditional_response).encode(),
                otherData=db_record.property('other_data', conditional=is_conditional_response).encode()
            )
        elif query_type == dns.TXT:
            record = dns.Record_TXT(
                db_record.property('data', conditional=is_conditional_response).encode()
            )
        elif query_type == Record_CAA.TYPE:
            record = Record_CAA(
                db_record.property('issue', conditional=is_conditional_response).encode()
            )
        else:
            pass

        if not record:
            return None

        query_domain = query.name.name if query_domain is None else query_domain
        answer = dns.RRHeader(name=query_domain, type=query_type, cls=query.cls, ttl=db_record.ttl, payload=record)
        return answer
