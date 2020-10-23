import re
import os
import csv
from app.lib.models.dns import DNSZoneModel, DNSZoneTagModel
from app.lib.dns.instances.zone import DNSZone
from app.lib.dns.instances.zone_tag import DNSZoneTag
from app.lib.dns.helpers.shared import SharedHelper
from sqlalchemy import func


class DNSZoneManager(SharedHelper):
    def __init__(self, settings, dns_records, users, notifications, dns_logs, dns_restrictions, tag_manager):
        self.settings = settings
        self.dns_records = dns_records
        self.users = users
        self.notifications = notifications
        self.dns_logs = dns_logs
        self.dns_restrictions = dns_restrictions
        self.tag_manager = tag_manager

    def __get(self, id=None, user_id=None, domain=None, base_domain=None, full_domain=None, active=None,
              exact_match=None, master=None, order_by='id', page=None, per_page=None, search=None, tags=None):
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

        if (search is not None) and (len(search) > 0):
            query = query.filter(DNSZoneModel.full_domain.ilike("%{0}%".format(search)))

        if tags is not None:
            tag_ids = self.tag_manager.get_tag_ids(tags, user_id=user_id)
            query = query.outerjoin(DNSZoneTagModel, DNSZoneTagModel.dns_zone_id == DNSZoneModel.id)
            query = query.filter(DNSZoneTagModel.tag_id.in_(tag_ids))

        if order_by == 'user_id':
            query = query.order_by(DNSZoneModel.user_id)
        elif order_by == 'full_domain':
            query = query.order_by(DNSZoneModel.full_domain)
        else:
            query = query.order_by(DNSZoneModel.id)

        return query.all() if (page is None and per_page is None) else query.paginate(page, per_page, False)

    def get(self, dns_zone_id, user_id=None):
        results = self.__get(id=dns_zone_id, user_id=user_id)
        if len(results) == 0:
            return False

        return self.__load(results[0])

    def delete(self, dns_zone_id):
        zone = self.get(dns_zone_id)
        if not zone:
            return False

        records = self.dns_records.get_zone_records(zone.id)
        for record in records:
            self.dns_records.delete(record)

        restrictions = self.dns_restrictions.get_zone_restrictions(zone.id).all()
        for restriction in restrictions:
            restriction.delete()

        subscriptions = zone.notifications.all()
        for name, subscription in subscriptions.items():
            self.notifications.logs.delete(subscription_id=subscription.id)
            subscription.delete()

        self.dns_logs.delete(dns_zone_id=zone.id)

        zone.delete_tags()
        zone.delete()

        return True

    def __load(self, item):
        zone = DNSZone(item)
        zone.record_count = self.dns_records.count(dns_zone_id=zone.id)
        zone.username = self.users.get_user(zone.user_id).username
        zone.notifications = self.notifications.get_zone_subscriptions(zone.id)
        zone.match_count = self.dns_logs.count(dns_zone_id=zone.id)
        zone.restrictions = self.dns_restrictions.get_zone_restrictions(zone.id)
        zone.tags = self.__load_tags(zone.id)
        return zone

    def __load_tags(self, dns_zone_id):
        results = DNSZoneTagModel.query.filter(DNSZoneTagModel.dns_zone_id == dns_zone_id).all()
        tags = []
        for result in results:
            item = self.tag_manager.get(result.tag_id)
            if not item:
                continue

            tags.append(item.name)

        return tags

    def create(self):
        item = DNSZone(DNSZoneModel())
        item.save()
        return item

    def save(self, zone, user_id, domain, base_domain, active, exact_match, master, forwarding):
        zone.user_id = user_id
        zone.domain = self.__fix_domain(domain)
        zone.base_domain = self.__fix_domain(base_domain)
        zone.full_domain = zone.domain + zone.base_domain
        zone.active = active
        zone.exact_match = exact_match
        zone.master = master
        zone.forwarding = forwarding
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

    def get_user_zones(self, user_id, order_by='id', search=None, tags=None):
        results = self.__get(user_id=user_id, order_by=order_by, search=search, tags=tags)

        zones = []
        for result in results:
            zones.append(self.__load(result))

        return zones

    def get_user_zones_paginated(self, user_id, order_by='id', page=None, per_page=None, search=None, tags=None):
        if isinstance(tags, list):
            # Remove empty elements.
            tags = list(filter(None, tags))

            if len(tags) == 0:
                tags = None
        results = self.__get(user_id=user_id, order_by=order_by, page=page, per_page=per_page, search=search, tags=tags)

        zones = []
        for result in results.items:
            zones.append(self.__load(result))

        return {
            'results': results,
            'zones': zones
        }

    def find(self, full_domain, user_id=None):
        results = self.__get(full_domain=full_domain, user_id=user_id)
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

    def get_base_domain(self, is_admin, username):
        return '' if is_admin else self.get_user_base_domain(username)

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
        return self.save(zone, user.id, self.__clean_username(user.username), '.' + self.base_domain, True, False, True, False)

    def count(self, user_id=None):
        return len(self.__get(user_id=user_id))

    def exists(self, dns_zone_id=None, full_domain=None):
        return len(self.__get(id=dns_zone_id, full_domain=full_domain)) > 0

    def new(self, domain, active, exact_match, forwarding, user_id, master=False):
        errors = []

        if len(domain) == 0:
            errors.append('Invalid domain')
            return errors

        user = self.users.get_user(user_id)
        if not user:
            errors.append('Could not load user')
            return errors

        base_domain = self.get_base_domain(user.admin, user.username)
        if self.has_duplicate(0, domain, base_domain):
            errors.append('This domain already exists.')
            return errors

        zone = self.create()
        if not zone:
            errors.append('Could not get zone')
            return errors

        zone = self.save(zone, user.id, domain, base_domain, active, exact_match, master, forwarding)
        if not zone:
            errors.append('Could not save zone')
            return errors

        return zone

    def update(self, zone_id, domain, active, exact_match, forwarding, user_id, master=False):
        errors = []

        if len(domain) == 0:
            errors.append('Invalid domain')
            return errors

        zone = self.get(zone_id, user_id=user_id)
        if not zone:
            errors.append('Invalid zone')
            return errors

        user = self.users.get_user(user_id)
        if not user:
            errors.append('Could not load user')
            return errors

        base_domain = self.get_base_domain(user.admin, user.username)
        if self.has_duplicate(zone.id, domain, base_domain):
            errors.append('This domain already exists.')
            return errors

        zone = self.save(zone, user.id, domain, base_domain, active, exact_match, master, forwarding)
        return zone

    def export(self, user_id, save_as, overwrite=False, create_path=False, search=None, tags=None):
        if not self._prepare_path(save_as, overwrite, create_path):
            return False

        zones = self.get_user_zones(user_id, order_by='full_domain', search=search, tags=tags)

        header = [
            'type',
            'domain',
            'd_active',
            'd_exact_match',
            'd_forwarding',
            'd_master',
            'd_tags',
            'r_id',
            'r_ttl',
            'r_cls',
            'r_type',
            'r_active',
            'r_data'
        ]
        with open(save_as, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(header)

            for zone in zones:
                # Write the zone.
                zone_line = [
                    'zone',
                    self._sanitise_csv_value(zone.full_domain),
                    '1' if zone.active else '0',
                    '1' if zone.exact_match else '0',
                    '1' if zone.forwarding else '0',
                    '1' if zone.master else '0',
                    ','.join(zone.tags)
                ]
                writer.writerow(zone_line)

                # Write the records.
                records = self.dns_records.get_zone_records(zone.id, order_column='type')
                for record in records:
                    properties = []
                    for name, value in record.properties().items():
                        properties.append("{0}={1}".format(name, value))

                    record_line = [
                        'record',
                        self._sanitise_csv_value(zone.full_domain),
                        '',
                        '',
                        '',
                        '',
                        record.id,
                        record.ttl,
                        record.cls,
                        record.type,
                        '1' if record.active else '0',
                        "\n".join(properties)
                    ]
                    writer.writerow(record_line)

        return os.path.isfile(save_as)

    def save_tags(self, zone, tags):
        # Create tags.
        tag_mapping = {}
        for tag in tags:
            name = tag.strip().lower()
            tag_mapping[name] = self.tag_manager.save(zone.user_id, name).id

        # Delete all assigned zone tags.
        zone.delete_tags()

        # Add fresh batch.
        for name, id in tag_mapping.items():
            item = DNSZoneTag(DNSZoneTagModel())
            item.dns_zone_id = zone.id
            item.tag_id = id
            item.save()

        return zone
