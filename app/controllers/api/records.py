from . import bp
from app.lib.base.decorators import api_auth
from app.lib.api.records import ApiRecords
from flask_login import current_user


@bp.route('/zones/<string:zone>/records', methods=['GET'])
@api_auth
def zone_records(zone):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRecords().all(user_id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/records', methods=['POST'])
@api_auth
def zone_records_create(zone):
    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRecords().create(current_user.id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/records/<int:id>', methods=['GET'])
@api_auth
def zone_record_by_id(zone, id):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRecords().one(user_id, id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/records/<int:id>', methods=['POST'])
@api_auth
def zone_records_update(zone, id):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRecords().update(user_id, id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/records/<int:id>', methods=['DELETE'])
@api_auth
def zone_record_delete(zone, id):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiRecords().delete(user_id, id, zone_id=zone_id, domain=domain)


@bp.route('/records/classes', methods=['GET'])
@api_auth
def record_classes():
    return ApiRecords().classes()


@bp.route('/records/types', methods=['GET'])
@api_auth
def record_types():
    return ApiRecords().types()
