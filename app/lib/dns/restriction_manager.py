from sqlalchemy import asc, desc
from app.lib.dns.helpers.shared import SharedHelper
from app.lib.models.dns import DNSZoneRestrictionModel
from app.lib.dns.instances.restriction import DNSZoneRestriction
from app.lib.dns.collections.restrictions import RestrictionCollection


class RestrictionManager(SharedHelper):
    def __get(self, id=None, zone_id=None, ip_range=None, type=None, enabled=None, order_by=None, sort_order=None):
        query = DNSZoneRestrictionModel.query

        if id is not None:
            query = query.filter(DNSZoneRestrictionModel.id == id)

        if zone_id is not None:
            query = query.filter(DNSZoneRestrictionModel.zone_id == zone_id)

        if ip_range is not None:
            query = query.filter(DNSZoneRestrictionModel.ip_range == ip_range)

        if type is not None:
            query = query.filter(DNSZoneRestrictionModel.type == type)

        if enabled is not None:
            query = query.filter(DNSZoneRestrictionModel.enabled == enabled)

        if (order_by is not None) and (sort_order is not None):
            order = None
            if order_by == 'id':
                order = asc(DNSZoneRestrictionModel.id) if sort_order == 'asc' else desc(DNSZoneRestrictionModel.id)
            elif order_by == 'type':
                order = asc(DNSZoneRestrictionModel.type) if sort_order == 'asc' else desc(DNSZoneRestrictionModel.type)

            if order is not None:
                query = query.order_by(order)

        return query.all()

    def __load(self, item):
        return DNSZoneRestriction(item)

    def get_zone_restrictions(self, zone_id, enabled=None):
        zone_restrictions = RestrictionCollection()

        restrictions = self.__get(zone_id=zone_id, enabled=enabled, order_by='type', sort_order='asc')
        for restriction in restrictions:
            zone_restrictions.add(self.__load(restriction))

        return zone_restrictions

    def create(self, zone_id=None):
        item = DNSZoneRestriction(DNSZoneRestrictionModel())
        if zone_id is not None:
            item.zone_id = zone_id
        item.save()
        return item

    def save(self, restriction, zone_id, ip_range, type, enabled):
        restriction.zone_id = zone_id
        restriction.ip_range = ip_range
        restriction.type = type
        restriction.enabled = enabled
        restriction.save()
        return restriction

    def allow(self, zone_id, ip):
        # If there are no rules, allow.
        restrictions = self.get_zone_restrictions(zone_id, enabled=True)
        if restrictions.count() == 0:
            return True

        # This means that we have rules to process - default is 'block'.
        allow = False

        allow_rules = restrictions.gather(1)
        block_rules = restrictions.gather(2)

        if len(allow_rules) > 0:
            for rule in allow_rules:
                if self.ip_in_range(ip, rule.ip_range):
                    allow = True
                    break

            # As 'allow' rules exist, at this point the IP wasn't found in the allowed list, therefore it's already
            # blocked. This means that we don't even have to look in the blocked rules.
            if not allow:
                return False
        else:
            # If there are no 'allow' rules, it means that everything is allowed _except_ the blocked list.
            allow = True

        # If we reached this point, the 'allow' variable is set to True.
        if len(block_rules) > 0:
            for rule in block_rules:
                if self.ip_in_range(ip, rule.ip_range):
                    allow = False
                    break
        else:
            allow = True

        return allow

    def find(self, id=None, zone_id=None, ip_range=None, type=None, enabled=None):
        results = self.__get(id=id, zone_id=zone_id, ip_range=ip_range, type=type, enabled=enabled)
        if len(results) == 0:
            return False
        return self.__load(results[0])
