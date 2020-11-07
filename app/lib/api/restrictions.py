from app.lib.base.provider import Provider
from app.lib.api.base import ApiBase
from app.lib.api.definitions.restriction import Restriction


class ApiRestrictions(ApiBase):
    def all(self, user_id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        data = []
        for restriction in zone.restrictions.all():
            data.append(self.__load_restriction(restriction))
        return self.send_valid_response(data)

    def __load_restriction(self, item):
        restriction = Restriction()
        restriction.id = item.id
        restriction.ip = item.ip_range
        restriction.type = 'allow' if item.type == 1 else 'block'
        restriction.enabled = item.enabled
        return restriction

    def create(self, user_id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()
        restrictions = provider.dns_restrictions()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        required_fields = ['type', 'enabled', 'ip_or_range']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(
                5000,
                'Missing fields',
                'Required fields are: {0}'.format(', '.join(required_fields))
            )

        if data['type'] not in ['allow', 'block']:
            return self.send_error_response(5005, 'Invalid restriction type', '')
        elif len(data['ip_or_range']) == 0 or not restrictions.is_valid_ip_or_range(data['ip_or_range']):
            return self.send_error_response(5005, 'Invalid IP or Range', '')

        data['enabled'] = True if data['enabled'] else False
        data['type'] = 1 if data['type'] == 'allow' else 2

        restriction = restrictions.create(zone_id=zone.id)
        restriction = restrictions.save(restriction, zone.id, data['ip_or_range'], data['type'], data['enabled'])

        return self.one(user_id, restriction.id, zone_id=zone.id)

    def one(self, user_id, id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()
        restrictions = provider.dns_restrictions()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        restriction = restrictions.find(id=id, zone_id=zone.id)
        if not restriction:
            return self.send_not_found_response()

        return self.send_valid_response(self.__load_restriction(restriction))

    def update(self, user_id, id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()
        restrictions = provider.dns_restrictions()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        restriction = restrictions.find(id=id, zone_id=zone.id)
        if not restriction:
            return self.send_not_found_response()

        data = self.get_json([])
        if 'enabled' in data:
            data['enabled'] = True if data['enabled'] else False
        else:
            data['enabled'] = restriction.enabled

        if 'type' in data:
            if data['type'] not in ['allow', 'block']:
                return self.send_error_response(5005, 'Invalid restriction type', '')
            data['type'] = 1 if data['type'] == 'allow' else 2
        else:
            data['type'] = restriction.type

        if 'ip_or_range' in data:
            if len(data['ip_or_range']) == 0 or not restrictions.is_valid_ip_or_range(data['ip_or_range']):
                return self.send_error_response(5005, 'Invalid IP or Range', '')
        else:
            data['ip_or_range'] = restriction.ip_range

        restriction = restrictions.save(restriction, zone.id, data['ip_or_range'], data['type'], data['enabled'])

        return self.one(user_id, restriction.id, zone_id=zone.id)

    def delete(self, user_id, id, zone_id=None, domain=None):
        provider = Provider()
        zones = provider.dns_zones()
        restrictions = provider.dns_restrictions()

        zone = zones.get(zone_id, user_id) if zone_id is not None else zones.find(domain, user_id=user_id)
        if not zone:
            return self.send_not_found_response()

        restriction = restrictions.find(id=id, zone_id=zone.id)
        if not restriction:
            return self.send_not_found_response()

        restriction.delete()
        return self.send_success_response()
