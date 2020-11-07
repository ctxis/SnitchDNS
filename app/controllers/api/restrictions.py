from . import bp
from app.lib.base.decorators import api_auth
from app.lib.api.restrictions import ApiRestrictions
from flask_login import current_user


@bp.route('/zones/<string:zone>/restrictions', methods=['GET'])
@api_auth
def zone_restrictions(zone):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRestrictions().all(user_id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/restrictions', methods=['POST'])
@api_auth
def zone_restriction_add(zone):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRestrictions().create(user_id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/restrictions/<int:id>', methods=['GET'])
@api_auth
def zone_restriction_get(zone, id):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRestrictions().one(user_id, id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/restrictions/<int:id>', methods=['POST'])
@api_auth
def zone_restriction_update(zone, id):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRestrictions().update(user_id, id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/restrictions/<int:id>', methods=['DELETE'])
@api_auth
def zone_restriction_delete(zone, id):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRestrictions().delete(user_id, id, zone_id=zone_id, domain=domain)
