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
    provider = Provider()
    settings = provider.settings()
    dns = provider.dns_manager()

    dns_daemon_bind_ip = request.form['dns_daemon_bind_ip'].strip()
    dns_daemon_bind_port = int(request.form['dns_daemon_bind_port'].strip())

    if not dns.is_valid_ip_address(dns_daemon_bind_ip):
        flash('Invalid IP Address', 'error')
        return redirect(url_for('config.daemon'))
    elif dns_daemon_bind_port <= 0 or dns_daemon_bind_port > 65535:
        flash('Invalid Port', 'error')
        return redirect(url_for('config.daemon'))
    elif dns_daemon_bind_port < 1024:
        flash('Please enter a port between 1024 and 65535. Port numbers below 1024 require root access.', 'error')
        return redirect(url_for('config.daemon'))

    settings.save('dns_daemon_bind_ip', dns_daemon_bind_ip)
    settings.save('dns_daemon_bind_port', dns_daemon_bind_port)

    flash('Settings saved', 'success')
    return redirect(url_for('config.daemon'))
