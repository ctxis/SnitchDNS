from dnslib.server import BaseResolver, DNSLogger, DNSServer
from dnslib import RR, QTYPE, RCODE, CLASS
from app import create_app


class DatabaseResolver(BaseResolver):
    def __init__(self, dns_manager):
        # Create application instance within this thread.
        self.app = create_app()
        self.app.app_context().push()

        self.dns_manager = dns_manager
        self.zones = []

    def resolve(self, request, handler):
        # Create the response that we'll send back.
        reply = request.reply()

        # Try to find the requested zone.
        with self.app.app_context():
            zone = self.__find_zone(request.q)
            if zone:
                reply.add_answer(zone)

        if not reply.rr:
            reply.header.rcode = RCODE.NXDOMAIN
        return reply

    def __find_zone(self, query):
        zone = None

        # Split the query into an array.
        # 'something.snitch.contextis.com' will become:
        #   0 => something
        #   1 => snitch
        #   2 => contextis
        #   3 => com
        parts = str(query.qname).split('.')

        # The following loop will lookup from the longest to the shortest domain, for example:
        #   1 => something.snitch.contextis.com
        #   2 => snitch.contextis.com
        #   3 => contextis
        #   4 => com
        # Whichever it finds first, that's the one it will return and exit.
        while len(parts) > 0:
            # Join all the current items to re-create the domain.
            path = ".".join(parts)
            db_zone = self.dns_manager.find_zone(domain=path, type=str(QTYPE[query.qtype]), rclass=str(CLASS[query.qclass]))
            if db_zone:
                # We found a match.
                zone = self.__build_zone(path, db_zone)
                break

            # Remove the first element of the array, to continue searching for a matching domain.
            parts.pop(0)

        return zone

    def __build_zone(self, domain, db_zone):
        # Create a tab separated string with the zone data.
        zone = db_zone.build_zone(domain=domain)
        # Parse the zone into a new zone object.
        new_zone = [(rr.rname, QTYPE[rr.rtype], rr) for rr in RR.fromZone(zone)]
        # Cache it.
        self.zones.append(new_zone[0])

        # Split elements.
        name, rtype, rr = new_zone[0]
        return rr

