from . import bp
from app.lib.base.decorators import api_auth
from app.lib.api.zones import ApiZones
from flask_login import current_user


@bp.route('/zones', methods=['GET'])
@api_auth
def zones():
    user_id = None if current_user.admin else current_user.id
    return ApiZones().all(user_id)


@bp.route('/zones', methods=['POST'])
@api_auth
def zones_create():
    return ApiZones().create(current_user.id)


@bp.route('/zones/<string:zone>', methods=['POST'])
@api_auth
def zones_update(zone):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiZones().update(user_id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>', methods=['GET'])
@api_auth
def zone_get_one(zone):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiZones().one(user_id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>', methods=['DELETE'])
@api_auth
def zone_delete(zone):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiZones().delete(user_id, zone_id=zone_id, domain=domain)
