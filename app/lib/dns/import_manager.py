from app.lib.dns.helpers.shared import SharedHelper
import os
import datetime
import json
import progressbar
from app import db


class DNSImportManager(SharedHelper):
    IMPORT_TYPE_ZONE = 1
    IMPORT_TYPE_RECORD = 2

    @property
    def last_error(self):
        return self.__last_error

    @last_error.setter
    def last_error(self, value):
        self.__last_error = value

    def __init__(self, dns_zones, dns_records, users):
        self.__last_error = ''
        self.__dns_zones = dns_zones
        self.__dns_records = dns_records
        self.__zone_headers = ['domain', 'active', 'catch_all', 'forwarding', 'master', 'tags']
        self.__record_headers = ['domain', 'id', 'ttl', 'cls', 'type', 'active', 'data']
        self.__users = users

    def identify(self, csvfile):
        self.last_error = ''
        if not os.path.isfile(csvfile):
            self.last_error = 'CSV file does not exist'
            return False

        header = self._load_csv_header(csvfile)
        zone_header_count = 0
        record_header_count = 0
        for column in header:
            if column in self.__zone_headers:
                zone_header_count += 1

            if column in self.__record_headers:
                record_header_count += 1

        if zone_header_count == len(self.__zone_headers):
            return self.IMPORT_TYPE_ZONE
        elif record_header_count == len(self.__record_headers):
            return self.IMPORT_TYPE_RECORD

        self.last_error = 'If you are uploading a ZONE file these are the required columns: {0}. If you are uploading a RECORD file then the required columns are: {1}.'.format(', '.join(self.__zone_headers), ', '.join(self.__record_headers))
        return False

    def review(self, csvfile, type, user_id, show_progressbar=False):
        self.last_error = ''
        if not os.path.isfile(csvfile):
            self.last_error = 'CSV file does not exist'
            return False

        lines = self._load_csv(csvfile)
        if len(lines) == 0:
            self.last_error = 'CSV is empty'
            return False

        user = self.__users.get_user(user_id)
        if not user:
            self.last_error = 'Could not find user with ID {0}'.format(user_id)
            return False

        all_errors = []
        errors = []
        rows = []
        if type == self.IMPORT_TYPE_ZONE:
            rows = self.__categorise_rows(lines, type)
            rows, errors = self.__process_zones(rows, user, show_progressbar=show_progressbar)
        elif type == self.IMPORT_TYPE_RECORD:
            rows = self.__categorise_rows(lines, type)
            rows, errors = self.__process_records(rows, user, show_progressbar=show_progressbar)

        all_errors += errors

        # Sort errors per row number.
        all_errors = sorted(all_errors, key=lambda k: k['row'])

        return {
            'data': rows,
            'errors': all_errors
        }

    def run(self, data, type, user_id, show_progressbar=False):
        errors = []
        if type == self.IMPORT_TYPE_ZONE:
            self.__import_zones(data, user_id, show_progressbar=show_progressbar)
        elif type == self.IMPORT_TYPE_RECORD:
            self.__import_records(data, user_id, errors, show_progressbar=show_progressbar)

        return errors if len(errors) > 0 else True

    def __import_zones(self, zones, user_id, show_progressbar=False, batch_size=100):
        """
        This function has been heavily optimised as when I tried to import 250k domains its ETA was 1.5h, which isn't
        very practical. The main assumption made here is that when this function is called, all validation checks will
        have ready been completed.
        """

        widget = [
            progressbar.FormatLabel(''),
            ' ',
            progressbar.Percentage(),
            ' ',
            progressbar.Bar('#'),
            ' ',
            progressbar.RotatingMarker(),
            ' ',
            progressbar.ETA()
        ]

        count = 0
        unique_tags = []
        if show_progressbar:
            widget[0] = progressbar.FormatLabel('Importing zones')
            bar = progressbar.ProgressBar(max_value=len(zones), widgets=widget)

        # with bar as zones:
        for zone_to_import in list(zones):
            count += 1
            bar.update(count) if show_progressbar else False

            self.__zone_update_or_create(
                zone_to_import['domain'],
                zone_to_import['active'],
                zone_to_import['catch_all'],
                zone_to_import['forwarding'],
                zone_to_import['master'],
                user_id,
                id=zone_to_import['id'],
                autocommit=False
            )

            if count % batch_size == 0:
                db.session.commit()

            unique_tags = list(set(unique_tags + zone_to_import['tags']))

        db.session.commit()

        if show_progressbar:
            widget[0] = progressbar.FormatLabel('Re-mapping zones')
            bar = progressbar.ProgressBar(max_value=len(zones), widgets=widget)

        domain_mapping = self.__get_domain_mapping(user_id)
        zone_ids = []
        i = 0
        for zone_to_import in list(zones):
            i += 1
            bar.update(i) if show_progressbar else False

            zone_to_import['id'] = domain_mapping[zone_to_import['domain']] if zone_to_import['domain'] in domain_mapping else 0
            zone_ids.append(zone_to_import['id'])

        self.__zone_clear_tags(zone_ids, show_progressbar=show_progressbar, widget=widget)

        if show_progressbar:
            widget[0] = progressbar.FormatLabel('Importing tags')
            bar = progressbar.ProgressBar(max_value=len(zones), widgets=widget)

        self.__tags_create(user_id, unique_tags)
        tag_mapping = self.__get_tag_mapping(user_id)
        count = 0
        for zone_to_import in list(zones):
            count += 1
            bar.update(count) if show_progressbar else False

            tags = {}
            for tag in zone_to_import['tags']:
                tags[tag] = tag_mapping[tag]

            self.__zone_save_tags(zone_to_import['id'], tags, autocommit=False)

            if count % batch_size == 0:
                db.session.commit()

        db.session.commit()

        return True

    def __import_records(self, records, user_id, errors, show_progressbar=False, batch_size = 100):
        domain_mapping = self.__get_domain_mapping(user_id)

        widget = [
            progressbar.FormatLabel(''),
            ' ',
            progressbar.Percentage(),
            ' ',
            progressbar.Bar('#'),
            ' ',
            progressbar.RotatingMarker(),
            ' ',
            progressbar.ETA()
        ]

        if show_progressbar:
            widget[0] = progressbar.FormatLabel('Importing records')
            bar = progressbar.ProgressBar(max_value=len(records), widgets=widget)

        count = 0
        for record_to_import in records:
            count += 1
            bar.update(count) if show_progressbar else False

            # First, get the zone.
            zone_id = domain_mapping[record_to_import['domain']] if record_to_import['domain'] in domain_mapping else None
            if not zone_id:
                # At this point all zones should exist.
                errors.append('Could not find zone: {0}'.format(record_to_import['domain']))
                continue

            data = json.dumps(record_to_import['data']) if isinstance(record_to_import['data'], dict) else record_to_import['data']

            self.__record_update_or_create(
                zone_id,
                record_to_import['ttl'],
                record_to_import['cls'],
                record_to_import['type'],
                record_to_import['active'],
                data,
                id=record_to_import['record_id'],
                autocommit=False
            )

            if count % batch_size == 0:
                db.session.commit()

        db.session.commit()

        return True

    def __process_zones(self, zones, user, show_progressbar=False):
        errors = []
        items = []

        widget = [
            progressbar.FormatLabel(''),
            ' ',
            progressbar.Percentage(),
            ' ',
            progressbar.Bar('#'),
            ' ',
            progressbar.RotatingMarker(),
            ' ',
            progressbar.ETA()
        ]

        if show_progressbar:
            widget[0] = progressbar.FormatLabel('Processing zones')
            bar = progressbar.ProgressBar(max_value=len(zones), widgets=widget)

        domain_mapping = self.__get_domain_mapping(user.id)

        count = 0
        for zone in zones:
            count += 1
            bar.update(count) if show_progressbar else False

            active = True if zone['active'] in ['1', 'yes', 'true'] else False
            catch_all = True if zone['catch_all'] in ['1', 'yes', 'true'] else False
            forwarding = True if zone['forwarding'] in ['1', 'yes', 'true'] else False
            master = True if zone['master'] in ['1', 'yes', 'true'] else False
            tags = zone['tags'].split(',')
            # Trim each element.
            map(str.strip, tags)
            # Remove empty elements.
            tags = list(filter(None, tags))

            domain = {
                'id': domain_mapping[zone['domain']] if zone['domain'] in domain_mapping else 0,
                'domain': zone['domain'],
                'active': active,
                'catch_all': catch_all,
                'forwarding': forwarding,
                'master': master,
                'tags': tags
            }
            items.append(domain)

        return items, errors

    def __process_records(self, records, user, show_progressbar=False):
        errors = []
        items = []

        widget = [
            progressbar.FormatLabel(''),
            ' ',
            progressbar.Percentage(),
            ' ',
            progressbar.Bar('#'),
            ' ',
            progressbar.RotatingMarker(),
            ' ',
            progressbar.ETA()
        ]

        if show_progressbar:
            widget[0] = progressbar.FormatLabel('Processing records')
            bar = progressbar.ProgressBar(max_value=len(records), widgets=widget)

        domain_mapping = self.__get_domain_mapping(user.id)
        domain_mapping_reverse = self.__get_domain_mapping(user.id, reverse=True)

        count = 0
        for record in records:
            count += 1
            bar.update(count) if show_progressbar else False

            record_errors = []

            active = True if record['active'] in ['1', 'yes', 'true'] else False
            zone_id = self.__process_record_zone(record, record_errors, domain_mapping)
            record_id = self.__process_record_id(record, zone_id, record_errors, domain_mapping_reverse)
            ttl = self.__process_record_ttl(record, record_errors)
            cls = self.__process_record_cls(record, record_errors)
            type = self.__process_record_type(record, record_errors)
            data = {}
            if len(type) > 0:
                data = self.__process_record_data(record, type, record_errors)

            if len(record_errors) == 0:
                items.append({
                    'record_id': record_id,
                    'zone_id': zone_id,
                    'domain': record['domain'],
                    'active': active,
                    'ttl': ttl,
                    'cls': cls,
                    'type': type,
                    'data': data
                })
            else:
                errors += record_errors

        return items, errors

    def __process_record_id(self, record, zone_id, errors, domain_mapping):
        zone_id = zone_id if zone_id > 0 else None

        record_id = 0
        if len(record['id']) > 0:
            if not record['id'].isdigit():
                errors.append({'row': record['row'], 'error': 'Invalid record id: {0}'.format(record['id'])})
                return 0
            record_id = int(record['id'])

        if record_id > 0:
            record_exists = self.__record_exists(record_id, dns_zone_id=zone_id)
            if not record_exists:
                # Record not found - treat as new.
                return 0

        if zone_id > 0:
            domain = domain_mapping[zone_id] if zone_id in domain_mapping else None
            if not domain:
                errors.append({'row': record['row'], 'error': 'Zone {0} not found'.format(record['domain'])})
                return 0

            if record['domain'] != domain:
                errors.append({'row': record['row'], 'error': 'Record {0} does not belong to zone {1}'.format(record_id, zone_id)})
                return 0

        return record_id

    def __process_record_zone(self, record, errors, domain_mapping):
        zone_id = domain_mapping[record['domain']] if record['domain'] in domain_mapping else 0
        if zone_id == 0:
            errors.append({'row': record['row'], 'error': 'Zone not found: {0}'.format(record['domain'])})

        return zone_id

    def __record_exists(self, dns_record_id, dns_zone_id=None):
        params = {'id': dns_record_id}
        sql = "SELECT COUNT(id) AS c FROM dns_records WHERE id = :id"
        if dns_zone_id is not None:
            params['dns_zone_id'] = dns_zone_id
            sql += " AND dns_zone_id = :dns_zone_id"
        result = db.session.execute(sql, params).first()
        return result[0] > 0 if result is not None else False

    def __process_record_ttl(self, record, errors):
        ttl = 0
        if not record['ttl'].isdigit():
            errors.append({'row': record['row'], 'error': 'Invalid TTL: {0}'.format(record['ttl'])})
        else:
            ttl = int(record['ttl'])
            if ttl < 0:
                errors.append({'row': record['row'], 'error': 'Invalid TTL: {0}'.format(record['ttl'])})

        return ttl

    def __process_record_cls(self, record, errors):
        cls = ''
        if not record['cls'] in self.__dns_records.get_classes():
            errors.append({'row': record['row'], 'error': 'Invalid class: {0}'.format(record['cls'])})
        else:
            cls = record['cls']
        return cls

    def __process_record_type(self, record, errors):
        type = ''
        if not record['type'] in self.__dns_records.get_types():
            errors.append({'row': record['row'], 'error': 'Invalid type: {0}'.format(record['type'])})
        else:
            type = record['type']

        return type

    def __properties_to_dict(self, record, errors):
        rows = record['data'].split("\n")
        properties = {}
        for row in rows:
            parts = row.split('=', 1)
            if len(parts) != 2:
                errors.append({'row': record['row'], 'error': 'Invalid record property: {0}'.format(row)})
                continue

            name = parts[0].lower().strip()
            value = parts[1].strip()

            properties[name] = value

        return properties

    def __process_record_data(self, record, type, errors):
        record_properties = self.__properties_to_dict(record, errors)
        required_properties = self.__dns_records.get_record_type_properties(type, clean=True)

        data = {}
        for property_name, property_type in required_properties.items():
            if not property_name in record_properties:
                errors.append({'row': record['row'], 'error': 'Missing record property: {0}'.format(property_name)})
                continue

            value = record_properties[property_name]
            if (property_type == 'int') and (isinstance(value, str)):
                if not value.isdigit():
                    errors.append({'row': record['row'], 'error': "Invalid value '{0}' for property '{1}'".format(value, property_name)})
                    continue
                value = int(value)

            if (property_type == 'str') and (len(value) == 0):
                errors.append({'row': record['row'], 'error': "Invalid value '{0}' for property '{1}'".format(value, property_name)})
                continue
            elif (property_type == 'int') and (value < 0):
                errors.append({'row': record['row'], 'error': "Invalid value '{0}' for property '{1}'".format(value, property_name)})
                continue

            data[property_name] = value
        return data

    def __categorise_rows(self, rows, type):
        data = []
        for i, row in enumerate(rows):
            # Error row is +1 because the first row is the header which was removed.
            actual_row = i + 1

            if type == self.IMPORT_TYPE_ZONE:
                data.append({
                    'row': actual_row,
                    'domain': row['domain'].strip().lower(),
                    'active': row['active'].strip().lower(),
                    'catch_all': row['catch_all'].strip().lower(),
                    'forwarding': row['forwarding'].strip().lower(),
                    'master': row['master'].strip().lower(),
                    'tags': row['tags'].strip()
                })
            elif type == self.IMPORT_TYPE_RECORD:
                data.append({
                    'row': actual_row,
                    'domain': row['domain'].strip().lower(),
                    'id': row['id'].strip(),
                    'ttl': row['ttl'].strip().lower(),
                    'cls': row['cls'].strip().upper(),
                    'type': row['type'].strip().upper(),
                    'active': row['active'].strip().lower(),
                    'data': row['data'].strip()
                })

        return data

    def __get_domain_mapping(self, user_id, reverse=False):
        result = db.session.execute(
            "SELECT id, domain FROM dns_zones WHERE user_id = :user_id",
            {'user_id': user_id}
        )
        mapping = {}
        for row in result:
            if reverse:
                mapping[row[0]] = row[1]
            else:
                mapping[row[1]] = row[0]

        return mapping

    def __get_tag_mapping(self, user_id):
        result = db.session.execute(
            "SELECT id, name FROM tags WHERE user_id = :user_id",
            {'user_id': user_id}
        )
        mapping = {}
        for row in result:
            mapping[row[1]] = row[0]

        return mapping

    def __zone_update_or_create(self, domain, active, catch_all, forwarding, master, user_id, id=None, autocommit=True):
        params = {
            'domain': domain,
            'active': active,
            'catch_all': catch_all,
            'forwarding': forwarding,
            'master': master,
            'user_id': user_id,
            'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        if (id is None) or (id == 0):
            params['created_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            sql = "INSERT INTO dns_zones (domain, active, catch_all, forwarding, master, user_id, updated_at, created_at)" \
                  "VALUES(:domain, :active, :catch_all, :forwarding, :master, :user_id, :updated_at, :created_at)"
        else:
            params['id'] = id

            sql = "UPDATE dns_zones SET domain = :domain, active = :active, catch_all = :catch_all, forwarding = :forwarding, master = :master, user_id = :user_id, updated_at = :updated_at WHERE id = :id"

        result = db.session.execute(sql, params)
        if autocommit:
            db.session.commit()

        return True

    def __record_update_or_create(self, zone_id, ttl, cls, type, active, data, id=None, autocommit=True):
        params = {
            'zone_id': zone_id,
            'ttl': ttl,
            'cls': cls,
            'type': type,
            'active': active,
            'data': data,
            'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        if (id is None) or (id == 0):
            params['created_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            sql = "INSERT INTO dns_records (dns_zone_id, ttl, cls, type, data, active, updated_at, created_at) " \
                  "VALUES(:zone_id, :ttl, :cls, :type, :data, :active, :updated_at, :created_at)"
        else:
            params['id'] = id

            sql = "UPDATE dns_records SET dns_zone_id = :zone_id, ttl = :ttl, cls = :cls, type = :type, data = :data, active = :active, updated_at = :updated_at, created_at = :created_at WHERE id = :id"

        result = db.session.execute(sql, params)
        if autocommit:
            db.session.commit()

        return True

    def __tags_create(self, user_id, tags):
        for tag in tags:
            name = tag.strip().lower()
            result = db.session.execute(
                "SELECT id FROM tags WHERE name = :name AND user_id = :user_id",
                {'name': name, 'user_id': user_id}
            ).first()
            if result is None:
                params = {
                    'user_id': user_id,
                    'name': tag,
                    'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                sql = "INSERT INTO tags (user_id, name, created_at, updated_at) VALUES(:user_id, :name, :created_at, :updated_at)"
                db.session.execute(sql, params)

        db.session.commit()
        return True

    def __zone_save_tags(self, zone_id, tags, autocommit=True):
        for name, id in tags.items():
            params = {
                'dns_zone_id': zone_id,
                'tag_id': id,
                'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            sql = "INSERT INTO dns_zone_tags (dns_zone_id, tag_id, created_at, updated_at) VALUES(:dns_zone_id, :tag_id, :created_at, :updated_at)"
            db.session.execute(sql, params)

        if autocommit:
            db.session.commit()

        return True

    def __zone_clear_tags(self, zone_ids, batch_size=100, show_progressbar=False, widget=None):
        batches = list(self.__chunks(zone_ids, batch_size))

        if show_progressbar:
            widget[0] = progressbar.FormatLabel('Removing existing tags')
            bar = progressbar.ProgressBar(max_value=len(batches), widgets=widget)

        count = 0
        for batch in batches:
            count += 1
            bar.update(count) if show_progressbar else False

            i = 0
            params = {}
            for id in batch:
                i += 1
                params['param' + str(i)] = id

            bind = [':' + v for v in params.keys()]

            sql = "DELETE FROM dns_zone_tags WHERE dns_zone_id IN({0})".format(', '.join(bind))
            db.session.execute(sql, params)
            db.session.commit()

        return True

    def __chunks(self, data, size):
        # From https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        for i in range(0, len(data), size):
            yield data[i:i + size]
