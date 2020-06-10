from flask import Blueprint
from flask_login import current_user, login_required
from flask import request
from app.lib.base.provider import Provider
import json

bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@bp.route('/webpush/register', methods=['POST'])
@login_required
def webpush_register():
    provider = Provider()
    notifications = provider.notifications()

    response = {'success': True, 'message': ''}

    user_endpoint = request.form['user_endpoint'].strip()
    user_key = request.form['user_key'].strip()
    user_authsecret = request.form['user_authsecret'].strip()

    if len(user_endpoint) == 0 or len(user_key) == 0 or len(user_authsecret) == 0:
        response['sucess'] = False,
        response['message'] = 'Data is empty'
        return json.dumps(response)

    subscription = notifications.webpush.register(current_user.id, user_endpoint, user_key, user_authsecret)
    if not subscription:
        response['sucess'] = False,
        response['message'] = 'Could not register your web push subscription'

    return json.dumps(response)
