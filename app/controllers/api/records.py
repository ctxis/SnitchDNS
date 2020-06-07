from . import bp
from app.lib.base.decorators import api_auth
from app.lib.api.records import ApiRecords
from flask_login import current_user


@bp.route('/zones/<int:zone_id>/records', methods=['GET'])
@api_auth
def zone_records(zone_id):
    return ApiRecords().all(zone_id, current_user.id)


@bp.route('/zones/<int:zone_id>/records', methods=['POST'])
@api_auth
def zone_records_create(zone_id):
    return ApiRecords().create(zone_id, current_user.id)


@bp.route('/zones/<int:zone_id>/records/<int:record_id>', methods=['GET'])
@api_auth
def zone_record_by_id(zone_id, record_id):
    return ApiRecords().one(zone_id, record_id, current_user.id)


@bp.route('/zones/<int:zone_id>/records/<int:record_id>', methods=['POST'])
@api_auth
def zone_records_update(zone_id, record_id):
    return ApiRecords().update(zone_id, record_id, current_user.id)


@bp.route('/zones/<int:zone_id>/records/<int:record_id>', methods=['DELETE'])
@api_auth
def zone_record_delete(zone_id, record_id):
    return ApiRecords().delete(zone_id, record_id, current_user.id)


@bp.route('/records/classes', methods=['GET'])
@api_auth
def record_classes():
    return ApiRecords().classes()


@bp.route('/records/types', methods=['GET'])
@api_auth
def record_types():
    return ApiRecords().types()
