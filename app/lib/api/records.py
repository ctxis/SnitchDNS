from app.lib.base.provider import Provider
from app.lib.api.base import ApiBase
from app.lib.api.definitions.record import Record


class ApiRecords(ApiBase):
    def all(self, zone_id, user_id):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        if not zones.can_access(zone_id, user_id):
            return self.send_access_denied_response()

        zone = zones.get(zone_id)
        if not zone:
            return self.send_access_denied_response()

        results = records.get_zone_records(zone.id)
        data = []
        for result in results:
            data.append(self.__load_record(result))

        return self.send_valid_response(data)

    def one(self, zone_id, record_id, user_id):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        if not zones.can_access(zone_id, user_id):
            return self.send_access_denied_response()

        zone = zones.get(zone_id)
        if not zone:
            return self.send_access_denied_response()

        record = records.get(record_id, dns_zone_id=zone_id)
        if not record:
            return self.send_access_denied_response()

        return self.send_valid_response(self.__load_record(record))

    def __load_record(self, item):
        record = Record()
        record.id = item.id
        record.zone_id = item.dns_zone_id
        record.active = int(item.active) > 0
        record.cls = item.cls
        record.type = item.type
        record.ttl = int(item.ttl)
        record.data = item.data

        return record

    def classes(self):
        records = Provider().dns_records()
        return self.send_valid_response(records.get_classes())

    def types(self):
        records = Provider().dns_records()
        return self.send_valid_response(records.get_types())

    def delete(self, zone_id, record_id, user_id):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        if not zones.can_access(zone_id, user_id):
            return self.send_access_denied_response()

        zone = zones.get(zone_id)
        if not zone:
            return self.send_access_denied_response()

        record = records.get(record_id, dns_zone_id=zone_id)
        if not record:
            return self.send_access_denied_response()

        record.delete()
        return self.send_success_response()

    def create(self, zone_id, user_id):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        if not zones.can_access(zone_id, user_id):
            return self.send_access_denied_response()

        zone = zones.get(zone_id)
        if not zone:
            return self.send_access_denied_response()

        # First get the mandatory fields for all record types.
        required_fields = ['class', 'type', 'ttl', 'active']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(
                5000,
                'Missing fields',
                'Required fields are: {0}'.format(', '.join(required_fields))
            )

        # Validate.
        if data['class'] not in records.get_classes():
            return self.send_error_response(5005, 'Invalid class', '')
        elif data['type'] not in records.get_types():
            return self.send_error_response(5005, 'Invalid type', '')

        if isinstance(data['ttl'], str):
            if not data['ttl'].isdigit():
                return self.send_error_response(5005, 'Invalid TTL', '')
            data['ttl'] = int(data['ttl'])

        if data['ttl'] < 0:
            return self.send_error_response(5005, 'Invalid TTL', '')

        # Fix types.
        data['ttl'] = int(data['ttl'])
        data['active'] = True if data['active'] else False

        # Now that we have the type, we can get the type-specific properties.
        record_type_properties = records.get_record_type_properties(data['type'], clean=True)
        errors = []
        type_data = {}
        for property, type in record_type_properties.items():
            if property not in data['data']:
                errors.append('Missing type property {0}'.format(property))
                continue

            value = data['data'][property]
            if (type == 'int') and (isinstance(value, str)):
                if not value.isdigit():
                    errors.append('Invalid {0} value'.format(property))
                    continue
                value = int(value)

            if (type == 'str') and (len(value) == 0):
                errors.append('Invalid {0} value'.format(property))
            elif (type == 'int') and (value < 0):
                errors.append('Invalid {0} value'.format(property))

            type_data[property] = value

        if len(errors) > 0:
            return self.send_error_response(
                5005,
                'Invalid type property fields',
                errors
            )

        # Create the record.
        record = records.create()
        record = records.save(record, zone.id, data['ttl'], data['class'], data['type'], type_data, data['active'])

        return self.one(zone.id, record.id, user_id)

    def update(self, zone_id, record_id, user_id):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        if not zones.can_access(zone_id, user_id):
            return self.send_access_denied_response()

        zone = zones.get(zone_id)
        if not zone:
            return self.send_access_denied_response()

        # Get record.
        record = records.get(record_id, dns_zone_id=zone.id)
        if not record:
            return self.send_access_denied_response()

        data = self.get_json([])
        if 'class' in data:
            if data['class'] not in records.get_classes():
                return self.send_error_response(5005, 'Invalid class', '')
        else:
            data['class'] = record.cls

        if 'type' in data:
            if data['type'] not in records.get_types():
                return self.send_error_response(5005, 'Invalid type', '')
        else:
            data['type'] = record.type

        if 'ttl' in data:
            if isinstance(data['ttl'], str):
                if not data['ttl'].isdigit():
                    return self.send_error_response(5005, 'Invalid TTL', '')
                data['ttl'] = int(data['ttl'])
            if data['ttl'] < 0:
                return self.send_error_response(5005, 'Invalid TTL', '')
        else:
            data['ttl'] = record.ttl

        if 'active' in data:
            data['active'] = True if data['active'] else False
        else:
            data['active'] = record.active

        if 'data' in data:
            type_data = record.properties()

            # Now that we have the type, we can get the type-specific properties.
            record_type_properties = records.get_record_type_properties(data['type'], clean=True)
            errors = []
            for property, type in record_type_properties.items():
                if property not in data['data']:
                    # This property wasn't set, move on.
                    continue

                value = data['data'][property]
                if (type == 'int') and (isinstance(value, str)):
                    if not value.isdigit():
                        errors.append('Invalid {0} value'.format(property))
                        continue
                    value = int(value)

                if (type == 'str') and (len(value) == 0):
                    errors.append('Invalid {0} value'.format(property))
                elif (type == 'int') and (value < 0):
                    errors.append('Invalid {0} value'.format(property))

                type_data[property] = value

            if len(errors) > 0:
                return self.send_error_response(
                    5005,
                    'Invalid type property fields',
                    errors
                )
        else:
            type_data = record.data

        record = records.save(record, zone.id, data['ttl'], data['class'], data['type'], type_data, data['active'])

        return self.one(zone.id, record.id, user_id)
