from . import bp
from flask_login import login_required, current_user
from flask import redirect, url_for


@bp.route('/', methods=['GET'])
@login_required
def index():
    if current_user.admin:
        return redirect(url_for('config.forwarding'))
    else:
        return redirect(url_for('config.password'))
