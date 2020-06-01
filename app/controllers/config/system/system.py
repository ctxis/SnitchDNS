from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/system', methods=['GET'])
@login_required
@admin_required
def system():
    provider = Provider()
    system = provider.system()
    daemon = provider.daemon()

    return render_template(
        'config/system.html',
        is_venv=system.is_virtual_environment(),
        flask=system.can_run_flask(),
        version=system.check_version(system.get_python_version(), '3.6'),
        daemon_running=daemon.is_running(),
        daemon_configured=daemon.is_configured()
    )


@bp.route('/system/daemon', methods=['POST'])
@login_required
@admin_required
def system_daemon():
    provider = Provider()
    daemon = provider.daemon()

    action = request.form['action'].strip()

    if not daemon.is_configured():
        flash('DNS Daemon is not configured', 'error')
        return redirect(url_for('config.system'))
    elif action not in ['start', 'stop']:
        flash('Invalid action', 'error')
        return redirect(url_for('config.system'))

    if action == 'start':
        if daemon.start():
            flash('DNS Daemon Started', 'success')
        else:
            flash('Could not start DNS Daemon', 'error')
    elif action == 'stop':
        if daemon.stop():
            flash('DNS Daemon Stopped', 'success')
        else:
            flash('Could not stop DNS Daemon', 'error')

    return redirect(url_for('config.system'))
