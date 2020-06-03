from . import bp
from app.lib.base.decorators import api_auth
from app.lib.api.zones import ApiZones
from flask_login import current_user


@bp.route('/zones', methods=['GET'])
@api_auth
def zones():
    user_id = 0 if current_user.admin else current_user.id
    return ApiZones().all(user_id)


@bp.route('/zones', methods=['POST'])
@api_auth
def zones_create():
    user_id = 0 if current_user.admin else current_user.id
    return ApiZones().create(user_id, current_user.username, current_user.admin)


@bp.route('/zones/all', methods=['GET'])
@api_auth
def zones_all():
    # Only allow admins to retrieve all. If a low priv user calls this endpoint, return only their zones.
    user_id = None if current_user.admin else current_user.id
    return ApiZones().all(user_id)


@bp.route('/zones/<int:zone_id>', methods=['POST'])
@api_auth
def zones_update(zone_id):
    user_id = 0 if current_user.admin else current_user.id
    return ApiZones().update(zone_id, user_id, current_user.username, current_user.admin)


@bp.route('/zones/<int:zone_id>', methods=['GET'])
@api_auth
def zones_by_id(zone_id):
    user_id = 0 if current_user.admin else current_user.id
    return ApiZones().one(zone_id, user_id, current_user.admin)


@bp.route('/zones/<int:zone_id>', methods=['DELETE'])
@api_auth
def zone_delete(zone_id):
    user_id = 0 if current_user.admin else current_user.id
    return ApiZones().delete(zone_id, user_id, current_user.admin)
