from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider


@bp.route('/api', methods=['GET'])
@login_required
def api():
    provider = Provider()
    api = provider.api()

    return render_template(
        'config/account/api.html',
        keys=api.all(current_user.id)
    )


@bp.route('/api/action/<string:action>', methods=['POST'])
@bp.route('/api/action/<string:action>/<int:id>', methods=['POST'])
@login_required
def api_action(action, id=0):
    if action == 'add':
        return __create_apikey()
    elif action == 'delete':
        return __delete_apikey(id)
    elif action == 'toggle':
        return __toggle_apikey(id)

    flash('Unknown action', 'error')
    return redirect(url_for('config.api'))


def __create_apikey():
    provider = Provider()
    api = provider.api()

    name = request.form['name'].strip()
    if len(name) == 0:
        flash('Please enter your key description', 'error')
        return redirect(url_for('config.api'))

    if not api.add(current_user.id, name):
        flash('Could not create API key', 'error')
        return redirect(url_for('config.api'))

    flash('API Key created', 'success')
    return redirect(url_for('config.api'))


def __delete_apikey(id):
    provider = Provider()
    api = provider.api()

    if not api.can_access(id, current_user.id, is_admin=current_user.admin):
        flash('Access Denied', 'error')
        return redirect(url_for('config.api'))

    if not api.delete(id):
        flash('Could not delete key', 'error')
        return redirect(url_for('config.api'))

    flash('API Key deleted', 'success')
    return redirect(url_for('config.api'))


def __toggle_apikey(id):
    provider = Provider()
    api = provider.api()

    if not api.can_access(id, current_user.id, is_admin=current_user.admin):
        flash('Access Denied', 'error')
        return redirect(url_for('config.api'))

    key = api.get(id)
    if not key:
        flash('Could not retrieve key', 'error')
        return redirect(url_for('config.api'))

    key.enabled = not key.enabled
    key.save()

    flash('API Key status updated', 'success')
    return redirect(url_for('config.api'))
