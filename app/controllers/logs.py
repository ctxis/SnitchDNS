from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required

bp = Blueprint('logs', __name__, url_prefix='/logs')


@bp.route('/', methods=['GET'])
@login_required
def index():
    provider = Provider()
    logs = provider.dns_logs()

    user_id = 0 if current_user.admin else current_user.id
    log_items = logs.get_user_logs(user_id)

    return render_template(
        'logs/index.html',
        logs=log_items
    )


@bp.route('/unmatched', methods=['GET'])
@login_required
@admin_required
def index_unmatched():
    provider = Provider()
    logs = provider.dns_logs()

    log_items = logs.get_unmatched_logs()

    return render_template(
        'logs/index.html',
        logs=log_items
    )
