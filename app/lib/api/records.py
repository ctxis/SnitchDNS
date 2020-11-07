from app.lib.base.provider import Provider
from app.lib.api.base import ApiBase
from app.lib.api.definitions.record import Record


class ApiRecords(ApiBase):
    def all(self, user_id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        results = records.get_zone_records(zone.id)
        data = []
        for result in results:
            data.append(self.__load_record(result))

        return self.send_valid_response(data)

    def one(self, user_id, record_id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        record = records.get(record_id, dns_zone_id=zone_id)
        if not record:
            return self.send_not_found_response()

        return self.send_valid_response(self.__load_record(record))

    def __load_record(self, item):
        record = Record()
        record.id = item.id
        record.zone_id = item.dns_zone_id
        record.active = item.active
        record.cls = item.cls
        record.type = item.type
        record.ttl = int(item.ttl)
        record.data = item.data
        record.is_conditional = item.has_conditional_responses
        record.conditional_count = item.conditional_count
        record.conditional_limit = item.conditional_limit
        record.confitional_reset = item.conditional_reset
        record.conditional_data = item.conditional_data

        return record

    def classes(self):
        records = Provider().dns_records()
        return self.send_valid_response(records.get_classes())

    def types(self):
        records = Provider().dns_records()
        return self.send_valid_response(records.get_types())

    def delete(self, user_id, record_id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        record = records.get(record_id, dns_zone_id=zone_id)
        if not record:
            return self.send_not_found_response()

        records.delete(record)
        return self.send_success_response()

    def create(self, user_id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        # First get the mandatory fields for all record types.
        required_fields = [
            'class',
            'type',
            'ttl',
            'active',
            'data',
            'is_conditional',
            'conditional_count',
            'conditional_limit',
            'conditional_reset',
            'conditional_data'
        ]
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

        if isinstance(data['ttl'], str) and data['ttl'].isdigit() is False:
            return self.send_error_response(5005, 'Invalid TTL', '')
        data['ttl'] = int(data['ttl'])
        if data['ttl'] < 0:
            return self.send_error_response(5005, 'Invalid TTL', '')
        elif data['conditional_count'] < 0:
            return self.send_error_response(5005, 'Invalid Conditional Count', '')
        elif data['conditional_limit'] < 0:
            return self.send_error_response(5005, 'Invalid Conditional Limit', '')

        # Fix types.
        data['active'] = True if data['active'] else False
        data['is_conditional'] = True if data['is_conditional'] else False

        # Now that we have the type, we can get the type-specific properties.
        record_type_properties = records.get_record_type_properties(data['type'], clean=True)
        record_type_conditional_properties = records.get_record_type_properties(data['type'], clean=True)
        all_errors = []

        basic_data, errors = self.__parse_data_properties(data['data'], record_type_properties)
        all_errors += errors

        conditional_data, errors = self.__parse_data_properties(data['conditional_data'], record_type_conditional_properties)
        all_errors += errors

        if len(errors) > 0:
            return self.send_error_response(
                5005,
                'Invalid type property fields',
                errors
            )

        # Create the record.
        record = records.create()
        record = records.save(record, zone.id, data['ttl'], data['class'], data['type'], basic_data, data['active'])
        record = records.save_conditions(record, enabled=data['is_conditional'], data=conditional_data,
                                         count=data['conditional_count'], limit=data['conditional_limit'],
                                         reset=data['conditional_reset'])

        return self.one(user_id, record.id, zone_id=zone.id)

    def __parse_data_properties(self, data, properties):
        errors = []
        output = {}
        for property, type in properties.items():
            if property not in data:
                errors.append('Missing type property {0}'.format(property))
                continue

            value = data[property]
            if (type == 'int') and (isinstance(value, str)):
                if not value.isdigit():
                    errors.append('Invalid {0} value'.format(property))
                    continue
                value = int(value)

            if (type == 'str') and (len(value) == 0):
                errors.append('Invalid {0} value'.format(property))
            elif (type == 'int') and (value < 0):
                errors.append('Invalid {0} value'.format(property))

            output[property] = value

        return output, errors

    def update(self, user_id, record_id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()
        records = provider.dns_records()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        # Get record.
        record = records.get(record_id, dns_zone_id=zone.id)
        if not record:
            return self.send_not_found_response()

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

        if 'is_conditional' in data:
            data['is_conditional'] = True if data['is_conditional'] else False
        else:
            data['is_conditional'] = record.has_conditional_responses

        data['conditional_limit'] = data['conditional_limit'] if 'conditional_limit' in data else record.conditional_limit
        data['conditional_count'] = data['conditional_count'] if 'conditional_count' in data else record.conditional_count
        data['conditional_reset'] = data['conditional_reset'] if 'conditional_reset' in data else record.conditional_reset

        if 'data' in data:
            record_type_properties = records.get_record_type_properties(data['type'], clean=True)
            data['data'], errors = self.__parse_data_properties(data['data'], record_type_properties)
            if len(errors) > 0:
                return self.send_error_response(
                    5005,
                    'Invalid type property fields',
                    errors
                )
        else:
            data['data'] = record.data

        if 'conditional_data' in data:
            record_type_properties = records.get_record_type_properties(data['type'], clean=True)
            data['conditional_data'], errors = self.__parse_data_properties(data['conditional_data'], record_type_properties)
            if len(errors) > 0:
                return self.send_error_response(
                    5005,
                    'Invalid type property fields',
                    errors
                )
        else:
            data['conditional_data'] = record.conditional_data

        record = records.save(record, zone.id, data['ttl'], data['class'], data['type'], data['data'], data['active'])
        record = records.save_conditions(record, enabled=data['is_conditional'], data=data['conditional_data'],
                                         count=data['conditional_count'], limit=data['conditional_limit'],
                                         reset=data['conditional_reset'])

        return self.one(user_id, record.id, zone_id=zone.id)
