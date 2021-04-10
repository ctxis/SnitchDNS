from app.lib.base.provider import Provider
from app.lib.api.base import ApiBase
from app.lib.api.definitions.zone import Zone


class ApiZones(ApiBase):
    def all(self, user_id):
        provider = Provider()
        zones = provider.dns_zones()

        page = self.get_request_param('page', 1, int)
        per_page = self.get_request_param('per_page', 50, int)
        search = self.get_request_param('search', '', str)
        tags = self.get_request_param('tags', '', str).split(',')

        results = zones.get_user_zones_paginated(user_id, page=page, per_page=per_page, search=search, tags=tags)

        response = {
            'page': results['results'].page,
            'pages': results['results'].pages,
            'per_page': results['results'].per_page,
            'total': results['results'].total,
            'data': []
        }

        data = []
        for result in results['zones']:
            data.append(self.__load_zone(result))
        response['data'] = data

        return self.send_valid_response(response)

    def one(self, user_id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        return self.send_valid_response(self.__load_zone(zone))

    def create(self, user_id):
        required_fields = ['domain', 'active', 'catch_all', 'master', 'forwarding', 'regex', 'tags']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(
                5000,
                'Missing fields',
                'Required fields are: {0}'.format(', '.join(required_fields))
            )

        if len(data['domain']) == 0:
            return self.send_error_response(5001, 'Domain cannot be empty.', '')

        data['active'] = True if data['active'] else False
        data['catch_all'] = True if data['catch_all'] else False
        data['master'] = True if data['master'] else False
        data['forwarding'] = True if data['forwarding'] else False
        data['regex'] = True if data['regex'] else False
        data['tags'] = data['tags'].split(',')

        provider = Provider()
        zones = provider.dns_zones()

        zone = zones.new(data['domain'], data['active'], data['catch_all'], data['forwarding'], data['regex'], user_id, master=data['master'], update_old_logs=True)
        if isinstance(zone, list):
            errors = '\n'.join(zone)
            return self.send_error_response(5003, 'Could not create zone', errors)

        zone = zones.save_tags(zone, data['tags'])
        if not zone:
            return self.send_error_response(5002, 'Could not save tags', '')

        return self.one(user_id, zone_id=zone.id)

    def update(self, user_id, zone_id=None, domain=None):
        data = self.get_json([])
        if data is False:
            return self.send_error_response(5004, 'Invalid incoming data', '')

        provider = Provider()
        zones = provider.dns_zones()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        if 'domain' in data:
            data['domain'] = data['domain'] if not zone.master else zone.domain
        else:
            data['domain'] = zone.domain

        # Check for duplicates first.
        if zones.has_duplicate(zone.id, data['domain']):
            return self.send_error_response(5003, 'Domain already exists', '')

        # 'master' property is missing on purpose.
        if 'active' in data:
            data['active'] = True if data['active'] else False
        else:
            data['active'] = zone.active

        if 'catch_all' in data:
            data['catch_all'] = True if data['catch_all'] else False
        else:
            data['catch_all'] = zone.catch_all

        if 'forwarding' in data:
            data['forwarding'] = True if data['forwarding'] else False
        else:
            data['forwarding'] = zone.forwarding

        if 'regex' in data:
            data['regex'] = True if data['regex'] else False
        else:
            data['regex'] = zone.regex

        if 'tags' in data:
            data['tags'] = data['tags'].split(',')
        else:
            data['tags'] = []

        zone = zones.update(zone.id, data['domain'], data['active'], data['catch_all'], data['forwarding'], data['regex'], zone.user_id, master=zone.master, update_old_logs=True)
        if isinstance(zone, list):
            errors = '\n'.join(zone)
            return self.send_error_response(5003, 'Could not save zone', errors)

        zone = zones.save_tags(zone, data['tags'])
        if not zone:
            return self.send_error_response(5002, 'Could not save tags', '')

        return self.one(user_id, zone_id=zone.id)

    def delete(self, user_id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        zones.delete(zone.id)
        return self.send_success_response()

    def __load_zone(self, item):
        zone = Zone()
        zone.id = item.id
        zone.user_id = item.user_id
        zone.active = item.active
        zone.catch_all = item.catch_all
        zone.forwarding = item.forwarding
        zone.regex = item.regex
        zone.master = item.master
        zone.domain = item.domain
        zone.tags = item.tags
        zone.created_at = str(item.created_at)
        zone.updated_at = str(item.updated_at)

        return zone
