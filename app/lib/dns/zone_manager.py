import re
from app.lib.models.dns import DNSZoneModel
from app.lib.dns.instances.zone import DNSZone
from sqlalchemy import func


class DNSZoneManager:
    def __init__(self, settings, dns_records, users, notifications, dns_logs):
        self.settings = settings
        self.dns_records = dns_records
        self.users = users
        self.notifications = notifications
        self.dns_logs = dns_logs

    def __get(self, id=None, user_id=None, domain=None, base_domain=None, full_domain=None, active=None,
              exact_match=None, master=None, order_by='id'):
        query = DNSZoneModel.query

        if id is not None:
            query = query.filter(DNSZoneModel.id == id)

        if domain is not None:
            query = query.filter(func.lower(DNSZoneModel.domain) == domain.lower())

        if active is not None:
            query = query.filter(DNSZoneModel.active == active)

        if exact_match is not None:
            query = query.filter(DNSZoneModel.exact_match == exact_match)

        if user_id is not None:
            query = query.filter(DNSZoneModel.user_id == user_id)

        if full_domain is not None:
            query = query.filter(func.lower(DNSZoneModel.full_domain) == full_domain.lower())

        if base_domain is not None:
            query = query.filter(func.lower(DNSZoneModel.base_domain) == base_domain.lower())

        if master is not None:
            query = query.filter(DNSZoneModel.master == master)

        if order_by == 'user_id':
            query = query.order_by(DNSZoneModel.user_id)
        else:
            query = query.order_by(DNSZoneModel.id)

        return query.all()

    def get(self, dns_zone_id):
        results = self.__get(id=dns_zone_id)
        if len(results) == 0:
            return False

        return self.__load(results[0])

    def delete(self, dns_zone_id):
        zone = self.get(dns_zone_id)
        if not zone:
            return False

        records = self.dns_records.get_zone_records(zone.id)
        for record in records:
            record.delete()

        zone.delete()

        return True

    def __load(self, item):
        zone = DNSZone(item)
        zone.record_count = self.dns_records.count(dns_zone_id=zone.id)
        zone.username = self.users.get_user(zone.user_id).username
        zone.notifications = self.notifications.get_zone_subscriptions(zone.id)
        zone.match_count = self.dns_logs.count(dns_zone_id=zone.id)
        return zone

    def create(self):
        item = DNSZone(DNSZoneModel())
        item.save()
        return item

    def save(self, zone, user_id, domain, base_domain, active, exact_match, master):
        zone.user_id = user_id
        zone.domain = self.__fix_domain(domain)
        zone.base_domain = self.__fix_domain(base_domain)
        zone.full_domain = zone.domain + zone.base_domain
        zone.active = active
        zone.exact_match = exact_match
        zone.master = master
        zone.save()

        return zone

    def __fix_domain(self, domain):
        return domain.rstrip('.')

    def all(self):
        results = self.__get()

        zones = []
        for result in results:
            zones.append(self.__load(result))

        return zones

    def get_user_zones(self, user_id, order_by='id'):
        results = self.__get(user_id=user_id, order_by=order_by)

        zones = []
        for result in results:
            zones.append(self.__load(result))

        return zones

    def find(self, full_domain):
        results = self.__get(full_domain=full_domain)
        if len(results) == 0:
            return False

        return self.__load(results[0])

    @property
    def base_domain(self):
        return self.settings.get('dns_base_domain', '')

    def get_user_base_domain(self, username):
        dns_base_domain = self.__fix_domain(self.base_domain).lstrip('.')
        # Keep only letters, digits, underscore.
        username = self.__clean_username(username)
        return '.' + username + '.' + dns_base_domain

    def __clean_username(self, username):
        return re.sub(r'\W+', '', username)

    def has_duplicate(self, dns_zone_id, domain, base_domain):
        return DNSZoneModel.query.filter(
            DNSZoneModel.id != dns_zone_id,
            DNSZoneModel.domain == domain,
            DNSZoneModel.base_domain == base_domain
        ).count() > 0

    def can_access(self, dns_zone_id, user_id):
        if self.users.is_admin(user_id):
            return True
        return len(self.__get(id=dns_zone_id, user_id=user_id)) > 0

    def create_user_base_zone(self, user):
        if len(self.base_domain) == 0:
            return False

        zone = self.create()
        return self.save(zone, user.id, self.__clean_username(user.username), '.' + self.base_domain, True, False, True)

    def count(self, user_id=None):
        return len(self.__get(user_id=user_id))
