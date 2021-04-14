import re
import os
import csv
import zipfile
import time
from app.lib.models.dns import DNSZoneModel, DNSZoneTagModel
from app.lib.dns.instances.zone import DNSZone
from app.lib.dns.instances.zone_tag import DNSZoneTag
from app.lib.dns.helpers.shared import SharedHelper
from sqlalchemy import func
from app import db


class DNSZoneManager(SharedHelper):
    def __init__(self, settings, dns_records, users, notifications, dns_logs, dns_restrictions, tag_manager):
        self.settings = settings
        self.dns_records = dns_records
        self.users = users
        self.notifications = notifications
        self.dns_logs = dns_logs
        self.dns_restrictions = dns_restrictions
        self.tag_manager = tag_manager

    def __get(self, id=None, user_id=None, domain=None, active=None, catch_all=None, master=None, order_by='id',
              page=None, per_page=None, search=None, tags=None, regex=None):
        query = DNSZoneModel.query

        if id is not None:
            query = query.filter(DNSZoneModel.id == id)

        if domain is not None:
            query = query.filter(func.lower(DNSZoneModel.domain) == domain.lower())

        if active is not None:
            query = query.filter(DNSZoneModel.active == active)

        if catch_all is not None:
            query = query.filter(DNSZoneModel.catch_all == catch_all)

        if user_id is not None:
            query = query.filter(DNSZoneModel.user_id == user_id)

        if master is not None:
            query = query.filter(DNSZoneModel.master == master)

        if regex is not None:
            query = query.filter(DNSZoneModel.regex == regex)

        if (search is not None) and (len(search) > 0):
            query = query.filter(DNSZoneModel.domain.ilike("%{0}%".format(search)))

        if tags is not None:
            tags = list(filter(None, tags))
            if len(tags) > 0:
                tag_ids = self.tag_manager.get_tag_ids(tags, user_id=user_id)
                query = query.outerjoin(DNSZoneTagModel, DNSZoneTagModel.dns_zone_id == DNSZoneModel.id)
                query = query.filter(DNSZoneTagModel.tag_id.in_(tag_ids))

        if order_by == 'user_id':
            query = query.order_by(DNSZoneModel.user_id)
        elif order_by == 'domain':
            query = query.order_by(DNSZoneModel.domain)
        else:
            query = query.order_by(DNSZoneModel.id)

        return query.all() if (page is None and per_page is None) else query.paginate(page, per_page, False)

    def get(self, dns_zone_id, user_id=None):
        results = self.__get(id=dns_zone_id, user_id=user_id)
        if len(results) == 0:
            return False

        return self.__load(results[0])

    def delete(self, dns_zone_id, delete_old_logs=False, update_old_logs=True):
        #
        #
        #
        #
        # If you change this function, make sure you update group_delete() further down.
        #
        #
        #
        #
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

        if delete_old_logs:
            self.dns_logs.delete(dns_zone_id=zone.id)
        elif update_old_logs:
            self.dns_logs.update_old_logs(zone.domain, 0)

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

    def save(self, zone, user_id, domain, active, catch_all, master, forwarding, regex, update_old_logs=False):
        zone.user_id = user_id
        zone.domain = domain.lower()
        zone.active = active
        zone.catch_all = catch_all
        zone.master = master
        zone.forwarding = forwarding
        zone.regex = regex
        zone.save()

        if update_old_logs:
            self.dns_logs.update_old_logs(zone.domain, zone.id)

        return zone

    def __fix_domain(self, domain):
        return domain.rstrip('.')

    def all(self):
        results = self.__get()

        zones = []
        for result in results:
            zones.append(self.__load(result))

        return zones

    def get_user_zones(self, user_id, order_by='id', search=None, tags=None, raw=False):
        results = self.__get(user_id=user_id, order_by=order_by, search=search, tags=tags)
        if raw:
            return results

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

    def find(self, domain, user_id=None):
        results = self.__get(domain=domain, user_id=user_id)
        if len(results) == 0:
            return False

        return self.__load(results[0])

    def load_regex_domains(self, user_id=None):
        results = self.__get(user_id=user_id, regex=True)
        zones = []
        for result in results:
            zones.append(self.__load(result))

        return zones

    @property
    def base_domain(self):
        return self.settings.get('dns_base_domain', '')

    def get_user_base_domain(self, username):
        # Keep only letters, digits, underscore.
        username = self.__clean_username(username)
        return username + '.' + self.base_domain

    def get_base_domain(self, is_admin, username):
        return '' if is_admin else self.get_user_base_domain(username)

    def __clean_username(self, username):
        return re.sub(r'\W+', '', username)

    def has_duplicate(self, dns_zone_id, domain):
        return DNSZoneModel.query.filter(
            DNSZoneModel.id != dns_zone_id,
            DNSZoneModel.domain == domain
        ).count() > 0

    def can_access(self, dns_zone_id, user_id):
        if self.users.is_admin(user_id):
            return True
        return len(self.__get(id=dns_zone_id, user_id=user_id)) > 0

    def create_user_base_zone(self, user):
        if len(self.base_domain) == 0:
            return False

        zone = self.create()
        return self.save(zone, user.id, self.get_user_base_domain(user.username), True, True, True, False, False)

    def count(self, user_id=None):
        return len(self.__get(user_id=user_id))

    def exists(self, dns_zone_id=None, domain=None):
        return len(self.__get(id=dns_zone_id, domain=domain)) > 0

    def new(self, domain, active, catch_all, forwarding, regex, user_id, master=False, update_old_logs=False):
        errors = []

        if len(domain) == 0:
            errors.append('Invalid domain')
            return errors

        user = self.users.get_user(user_id)
        if not user:
            errors.append('Could not load user')
            return errors

        base_domain = self.get_base_domain(user.admin, user.username)
        if len(base_domain) > 0:
            domain = domain + '.' + base_domain

        if self.has_duplicate(0, domain):
            errors.append('This domain already exists.')
            return errors

        zone = self.create()
        if not zone:
            errors.append('Could not get zone')
            return errors

        zone = self.save(zone, user.id, domain, active, catch_all, master, forwarding, regex)
        if not zone:
            errors.append('Could not save zone')
            return errors

        if update_old_logs:
            self.dns_logs.update_old_logs(zone.domain, zone.id)

        return zone

    def update(self, zone_id, domain, active, catch_all, forwarding, regex, user_id, master=False, update_old_logs=False):
        errors = []

        if len(domain) == 0 and master is False:
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

        if not master:
            base_domain = self.get_base_domain(user.admin, user.username)
            if len(base_domain) > 0:
                domain = domain + '.' + base_domain

        if self.has_duplicate(zone.id, domain):
            errors.append('This domain already exists.')
            return errors

        zone = self.save(zone, user.id, domain, active, catch_all, master, forwarding, regex, update_old_logs=update_old_logs)
        return zone

    def export_zones(self, zones, output):
        zone_header = [
            'domain',
            'active',
            'catch_all',
            'forwarding',
            'regex',
            'master',
            'tags'
        ]

        with open(output, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(zone_header)

            for zone in zones:
                line = [
                    self._sanitise_csv_value(zone.domain),
                    '1' if zone.active else '0',
                    '1' if zone.catch_all else '0',
                    '1' if zone.forwarding else '0',
                    '1' if zone.regex else '0',
                    '1' if zone.master else '0',
                    ','.join(self.__load_tags(zone.id))
                ]
                writer.writerow(line)

        return True

    def export_records(self, zones, output):
        record_header = [
            'domain',
            'id',
            'ttl',
            'cls',
            'type',
            'active',
            'data',
            'is_conditional',
            'conditional_count',
            'conditional_limit',
            'conditional_reset',
            'conditional_data'
        ]

        with open(output, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(record_header)

            for zone in zones:
                records = self.dns_records.get_zone_records(zone.id, order_column='type')
                for record in records:
                    properties = []
                    conditional_properties = []
                    for name, value in record.properties().items():
                        properties.append("{0}={1}".format(name, value))

                    for name, value in record.conditional_properties().items():
                        conditional_properties.append("{0}={1}".format(name, value))

                    line = [
                        self._sanitise_csv_value(zone.domain),
                        record.id,
                        record.ttl,
                        record.cls,
                        record.type,
                        '1' if record.active else '0',
                        "\n".join(properties),
                        '1' if record.has_conditional_responses else '0',
                        record.conditional_count,
                        record.conditional_limit,
                        '1' if record.conditional_reset else '0',
                        "\n".join(conditional_properties)
                    ]
                    writer.writerow(line)

        return True

    def export(self, user_id=None, working_folder=None, export_zones=False, export_records=False, compress_export=False, search=None, tags=None):
        if working_folder is None:
            working_folder = self.get_user_data_path(user_id if user_id is not None else 0, folder=str(int(time.time())))

        if not self._prepare_path(working_folder, True, True):
            return False
        elif export_zones is False and export_records is False:
            # Why are you even here?
            return False

        file_zones = os.path.join(working_folder, 'zones.csv')
        file_records = os.path.join(working_folder, 'records.csv')
        save_as = os.path.join(working_folder, 'export.zip')

        zones = self.get_user_zones(user_id, order_by='domain', search=search, tags=tags, raw=True)
        if export_zones:
            if not self.export_zones(zones, file_zones):
                return False

        if export_records:
            if not self.export_records(zones, file_records):
                return False

        if compress_export:
            with zipfile.ZipFile(save_as, 'w', zipfile.ZIP_DEFLATED) as zip:
                if export_zones:
                    zip.write(file_zones, 'zones.csv')
                if export_records:
                    zip.write(file_records, 'records.csv')

        return {
            'zones': file_zones if export_zones else '',
            'records': file_records if export_records else '',
            'zip': save_as if compress_export else ''
        }

    def save_tags(self, zone, tags):
        # Remove empty tags.
        tags = list(filter(None, tags))

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

    def tag_count(self, tag_id):
        return DNSZoneTagModel.query.filter(DNSZoneTagModel.tag_id == tag_id).count()

    def tag_delete(self, tag_id):
        DNSZoneTagModel.query.filter(DNSZoneTagModel.tag_id == tag_id).delete()
        db.session.commit()
        return True

    def group_delete(self, user_id, search=None, tags=None, batch_size=1000):
        """
        This function is heavily optimised, cause object creation is very slow. Effectively it does the same thing as
        delete() further up, but with raw queries.
        """
        # This will only fetch domains that belong to the user, therefore we don't have to do any other checks.
        zones = self.get_user_zones(user_id, order_by='domain', search=search, tags=tags, raw=True)
        zone_ids = []
        for zone in zones:
            zone_ids.append(zone.id)

        batches = list(self.__chunks(zone_ids, batch_size))
        for batch in batches:
            i = 0
            params = {}
            for id in batch:
                i += 1
                params['param' + str(i)] = id

            bind = [':' + v for v in params.keys()]

            queries = [
                "DELETE FROM dns_records WHERE dns_zone_id IN({0})".format(', '.join(bind)),
                "DELETE FROM dns_zone_restrictions WHERE zone_id IN({0})".format(', '.join(bind)),
                "DELETE FROM notification_subscriptions WHERE zone_id IN({0})".format(', '.join(bind)),
                "DELETE FROM dns_zone_tags WHERE dns_zone_id IN({0})".format(', '.join(bind)),
                "DELETE FROM dns_zones WHERE id IN({0})".format(', '.join(bind))
            ]

            for sql in queries:
                db.session.execute(sql, params)

        db.session.commit()

        return True

    def __chunks(self, data, size):
        # From https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        for i in range(0, len(data), size):
            yield data[i:i + size]
