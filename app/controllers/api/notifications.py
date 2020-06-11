from . import bp
from app.lib.base.decorators import api_auth
from app.lib.api.notifications import ApiNotifications
from flask_login import current_user


@bp.route('/notifications/providers', methods=['GET'])
@api_auth
def notification_providers():
    return ApiNotifications().providers()


@bp.route('/zones/<int:zone_id>/notifications', methods=['GET'])
@api_auth
def zone_notifications(zone_id):
    return ApiNotifications().all(zone_id, current_user.id)


@bp.route('/zones/<int:zone_id>/notifications/<string:type>', methods=['GET'])
@api_auth
def zone_notifications_get(zone_id, type):
    return ApiNotifications().get(zone_id, type, current_user.id)


@bp.route('/zones/<int:zone_id>/notifications/<string:type>', methods=['POST'])
@api_auth
def zone_notifications_update(zone_id, type):
    return ApiNotifications().update(zone_id, type, current_user.id)
