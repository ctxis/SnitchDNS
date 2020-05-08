from . import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/daemon', methods=['GET'])
@login_required
@admin_required
def daemon():
    return render_template('config/daemon.html')


@bp.route('/daemon/save', methods=['POST'])
@login_required
@admin_required
def daemon_save():
    pass