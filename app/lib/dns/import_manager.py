from app.lib.dns.helpers.shared import SharedHelper
import os


class DNSImportManager(SharedHelper):
    @property
    def last_error(self):
        return self.__last_error

    @last_error.setter
    def last_error(self, value):
        self.__last_error = value

    def __init__(self, dns_zones, dns_records):
        self.__last_error = ''
        self.__dns_zones = dns_zones
        self.__dns_records = dns_records

    def review(self, csvfile, user_id):
        self.last_error = ''
        if not os.path.isfile(csvfile):
            self.last_error = 'CSV file does not exist'
            return False

        lines = self._load_csv(csvfile)
        if len(lines) == 0:
            self.last_error = 'CSV is empty'
            return False

        missing_columns = self.__get_missing_columns(lines[0])
        if len(missing_columns) > 0:
            self.last_error = 'Missing CSV columns: {0}'.format(", ".join(missing_columns))
            return False

        all_errors = []
        zone_rows, record_rows, errors = self.__categorise_rows(lines)
        all_errors += errors

        zones, errors = self.__process_zones(zone_rows, user_id)
        all_errors += errors

        records, errors = self.__process_records(record_rows, zones, user_id)
        all_errors += errors

        # Sort errors per row number.
        all_errors = sorted(all_errors, key=lambda k: k['row'])

        return {
            'zones': zones,
            'records': records,
            'errors': all_errors
        }

    def run(self, zones, records, user_id):
        errors = []
        self.__import_zones(zones, user_id, errors)
        self.__import_records(records, user_id, errors)

        return errors if len(errors) > 0 else True

    def __import_zones(self, zones, user_id, errors):
        for zone_to_import in zones:
            if zone_to_import['id'] > 0:
                zone = self.__dns_zones.update(
                    zone_to_import['id'],
                    zone_to_import['domain'],
                    zone_to_import['active'],
                    zone_to_import['exact_match'],
                    zone_to_import['forwarding'],
                    user_id,
                    zone_to_import['master']
                )
            else:
                zone = self.__dns_zones.new(
                    zone_to_import['domain'],
                    zone_to_import['active'],
                    zone_to_import['exact_match'],
                    zone_to_import['forwarding'],
                    user_id,
                    zone_to_import['master']
                )

            if isinstance(zone, list):
                # It means it's all errors.
                errors += zone
                continue

        return True

    def __import_records(self, records, user_id, errors):
        for record_to_import in records:
            # First, get the zone.
            zone = self.__dns_zones.find(record_to_import['domain'], user_id=user_id)
            if not zone:
                # At this point all zones should exist.
                errors.append('Could not find zone: {0}'.format(record_to_import['domain']))
                continue

            if record_to_import['record_id'] > 0:
                record = self.__dns_records.get(record_to_import['record_id'], dns_zone_id=zone.id)
                if not record:
                    # At this point all zones should exist.
                    errors.append('Could not find record {0} zone: {1}'.format(record_to_import['record_id'], record_to_import['domain']))
                    continue
            else:
                record = self.__dns_records.create()

            self.__dns_records.save(record, zone.id, record_to_import['ttl'], record_to_import['cls'], record_to_import['type'], record_to_import['data'], record_to_import['active'])

        return True

    def __process_zones(self, zones, user_id):
        errors = []
        items = []

        for zone in zones:
            active = True if zone['active'] in ['1', 'yes', 'true'] else False
            exact_match = True if zone['exact_match'] in ['1', 'yes', 'true'] else False
            forwarding = True if zone['forwarding'] in ['1', 'yes', 'true'] else False
            master = True if zone['master'] in ['1', 'yes', 'true'] else False

            existing_zone = self.__dns_zones.find(zone['domain'], user_id=user_id)
            zone_id = existing_zone.id if existing_zone else 0

            items.append({
                'id': zone_id,
                'domain': zone['domain'],
                'active': active,
                'exact_match': exact_match,
                'forwarding': forwarding,
                'master': master
            })

        return items, errors

    def __process_records(self, records, zones, user_id):
        errors = []
        items = []

        for record in records:
            record_errors = []

            active = True if record['active'] in ['1', 'yes', 'true'] else False
            zone_id = self.__process_record_zone(record, zones, user_id, record_errors)
            record_id = self.__process_record_id(record, zone_id, user_id, record_errors)
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

    def __process_record_id(self, record, zone_id, user_id, errors):
        record_id = 0
        if len(record['id']) > 0:
            if not record['id'].isdigit():
                errors.append({'row': record['row'], 'error': 'Invalid record id: {0}'.format(record['id'])})
                return 0
            record_id = int(record['id'])

        existing_record = self.__dns_records.get(record_id)
        if not existing_record:
            # Record not found - treat as new.
            return 0

        if zone_id > 0:
            zone = self.__dns_zones.get(zone_id, user_id=user_id)
            if not zone:
                errors.append({'row': record['row'], 'error': 'Zone {0} not found'.format(record['domain'])})
                return 0

            if record['domain'] != zone.full_domain:
                errors.append({'row': record['row'], 'error': 'Record {0} does not belong to zone {1}'.format(existing_record.id, zone_id)})
                return 0

        return record_id

    def __process_record_zone(self, record, zones, user_id, errors):
        zone_id = 0
        zone = self.__dns_zones.find(record['domain'], user_id=user_id)
        if zone:
            zone_id = zone.id
        else:
            # If the zone isn't found, try to find it in the 'zones' list in case it's an imported one.
            zone_exists = False
            for zone_to_import in zones:
                if zone_to_import['domain'] == record['domain']:
                    zone_exists = True
                    break

            if not zone_exists:
                errors.append({'row': record['row'], 'error': 'Zone not found: {0}'.format(record['domain'])})

        return zone_id

    def __process_record_ttl(self, record, errors):
        ttl = 0
        if not record['ttl'].isdigit():
            errors.append({'row': record['row'], 'error': 'Invalid TTL: {0}'.format(record['ttl'])})
        else:
            ttl = int(record['ttl'])
            if ttl <= 0:
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

    def __categorise_rows(self, rows):
        zones = []
        records = []
        errors = []
        for i, row in enumerate(rows):
            # Error row is +1 because the first row is the header which was removed.
            actual_row = i + 1

            if row['type'].lower() == 'zone':
                zones.append({
                    'row': actual_row,
                    'domain': row['domain'].strip().lower(),
                    'active': row['d_active'].strip().lower(),
                    'exact_match': row['d_exact_match'].strip().lower(),
                    'forwarding': row['d_forwarding'].strip().lower(),
                    'master': row['d_master'].strip().lower()
                })
            elif row['type'].lower() == 'record':
                records.append({
                    'row': actual_row,
                    'domain': row['domain'].strip().lower(),
                    'id': row['r_id'].strip(),
                    'ttl': row['r_ttl'].strip().lower(),
                    'cls': row['r_cls'].strip().upper(),
                    'type': row['r_type'].strip().upper(),
                    'active': row['r_active'].strip().lower(),
                    'data': row['r_data'].strip()
                })
            else:
                errors.append({'row': actual_row, 'error': "Unknown row type: '{0}'".format(row['type'])})

        return zones, records, errors

    def __get_missing_columns(self, row):
        required_columns = ['type', 'domain',
                            'd_active', 'd_exact_match', 'd_forwarding', 'd_master',
                            'r_id', 'r_ttl', 'r_cls', 'r_type', 'r_active', 'r_data']
        missing_columns = []
        for column in required_columns:
            if not column in row:
                missing_columns.append(column)

        return missing_columns
