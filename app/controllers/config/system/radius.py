from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/radius', methods=['GET'])
@login_required
@admin_required
def radius():
    return render_template('config/system/radius.html')


@bp.route('/radius/save', methods=['POST'])
@login_required
@admin_required
def radius_save():
    provider = Provider()
    settings = provider.settings()

    radius_enabled = True if int(request.form.get('radius_enabled', 0)) == 1 else False
    radius_host = request.form['radius_host'].strip()
    radius_port = request.form['radius_port'].strip()
    radius_port = int(radius_port) if radius_port.isdigit else 0
    radius_secret = request.form['radius_secret'].strip()

    if len(radius_host) == 0:
        flash('RADIUS Host cannot be empty', 'error')
        return redirect(url_for('config.ldap'))
    elif radius_port <= 0:
        flash('Invalid RADIUS port', 'error')
        return redirect(url_for('config.ldap'))

    settings.save('radius_host', radius_host)
    settings.save('radius_port', radius_port)
    settings.save('radius_enabled', radius_enabled)

    # If the password is not '********' then save it. This is because we show that value instead of the actual password.
    if len(radius_secret) > 0 and radius_secret != '********':
        settings.save('radius_secret', radius_secret)

    flash('Settings saved', 'success')
    return redirect(url_for('config.radius'))


@bp.route('/radius/test', methods=['POST'])
@login_required
@admin_required
def radius_test():
    provider = Provider()
    radius = provider.radius()

    if not radius.test_connection():
        flash('RADIUS Response: {0}'.format(radius.error_message), 'error')
    else:
        flash('Connection established!', 'success')
    return redirect(url_for('config.radius'))
