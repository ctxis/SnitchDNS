from . import bp
from app.lib.base.decorators import api_auth
from app.lib.api.notifications import ApiNotifications
from flask_login import current_user


@bp.route('/notifications/providers', methods=['GET'])
@api_auth
def notification_providers():
    return ApiNotifications().providers()


@bp.route('/zones/<string:zone>/notifications', methods=['GET'])
@api_auth
def zone_notifications(zone):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiNotifications().all(user_id, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/notifications/<string:type>', methods=['GET'])
@api_auth
def zone_notifications_get(zone, type):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiNotifications().get(user_id, type, zone_id=zone_id, domain=domain)


@bp.route('/zones/<string:zone>/notifications/<string:type>', methods=['POST'])
@api_auth
def zone_notifications_update(zone, type):
    user_id = None if current_user.admin else current_user.id

    domain = None
    zone_id = None
    if zone.isdigit():
        zone_id = int(zone)
    else:
        domain = zone

    return ApiNotifications().update(user_id, type, zone_id=zone_id, domain=domain)
