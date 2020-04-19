from . import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider


@bp.route('/password', methods=['GET'])
@login_required
def password():
    return render_template('config/password.html')


@bp.route('/password/save', methods=['POST'])
@login_required
def password_save():
    pass
