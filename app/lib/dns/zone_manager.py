import re
from app.lib.models.dns import DNSZoneModel
from app.lib.dns.instances.zone import DNSZone
from sqlalchemy import func


class DNSZoneManager:
    def __init__(self, settings):
        self.settings = settings

    def __get(self, id=None, user_id=None, domain=None, base_domain=None, full_domain=None, active=None, exact_match=None):
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

        return query.all()

    def get(self, dns_zone_id):
        results = self.__get(id=dns_zone_id)
        if len(results) == 0:
            return False

        return self.__load(results[0])

    def __load(self, item):
        return DNSZone(item)

    def create(self):
        item = DNSZone(DNSZoneModel())
        item.save()
        return item

    def save(self, zone, user_id, domain, base_domain, active, exact_match):
        zone.user_id = user_id
        zone.domain = self.__fix_domain(domain)
        zone.base_domain = self.__fix_base_domain(base_domain)
        zone.full_domain = zone.domain + zone.base_domain
        zone.active = active
        zone.exact_match = exact_match
        zone.save()

        return True

    def __fix_domain(self, domain):
        return domain.rstrip('.')

    def __fix_base_domain(self, domain):
        return domain.rstrip('.') + '.'

    def all(self):
        results = self.__get()

        zones = []
        for result in results:
            zones.append(self.__load(result))

        return zones

    def get_user_zones(self, user_id):
        results = self.__get(user_id=user_id)

        zones = []
        for result in results:
            zones.append(self.__load(result))

        return zones

    def find(self, full_domain):
        results = self.__get(full_domain=full_domain)
        if len(results) == 0:
            return False

        return self.__load(results[0])

    # def get_all_logs(self):
    #     results = DNSQueryLogModel.query.order_by(DNSQueryLogModel.id).all()
    #
    #     logs = []
    #     for result in results:
    #         logs.append(DNSQueryLog(result))
    #
    #     return logs

    # def get_log_filters(self):
    #     classes = db.session.query(DNSQueryLogModel.rclass).group_by(DNSQueryLogModel.rclass).order_by(DNSQueryLogModel.rclass)
    #     types = db.session.query(DNSQueryLogModel.type).group_by(DNSQueryLogModel.type).order_by(DNSQueryLogModel.type)
    #     source_ips = db.session.query(DNSQueryLogModel.source_ip).group_by(DNSQueryLogModel.source_ip).order_by(DNSQueryLogModel.source_ip)
    #
    #     return {
    #         'classes': classes,
    #         'types': types,
    #         'source_ips': source_ips
    #     }

    @property
    def base_domain(self):
        return self.settings.get('dns_base_domain', '')

    def get_user_base_domain(self, username):
        dns_base_domain = self.__fix_domain(self.base_domain).lstrip('.')
        # Keep only letters, digits, underscore.
        username = re.sub(r'\W+', '', username)
        return '.' + username + '.' + dns_base_domain

    def has_duplicate(self, dns_zone_id, domain, base_domain):
        return DNSZoneModel.query.filter(
            DNSZoneModel.id != dns_zone_id,
            DNSZoneModel.domain == domain,
            DNSZoneModel.base_domain == base_domain
        ).count() > 0

    def can_access(self, dns_zone_id, user_id, is_admin=False):
        if is_admin:
            # SuperUser
            return True
        return self.__get(id=dns_zone_id, user_id=user_id) is not None
