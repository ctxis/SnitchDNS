from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required
import re


@bp.route('/users', methods=['GET'])
@login_required
@admin_required
def users():
    users = Provider().users()

    return render_template(
        'config/users/index.html',
        users=users.all()
    )


@bp.route('/users/<int:user_id>/edit', methods=['GET'])
@login_required
@admin_required
def user_edit(user_id):
    provider = Provider()
    users = provider.users()
    zones = provider.dns_zones()

    user = None
    if user_id <= 0:
        user_id = 0
    else:
        user = users.get_user(user_id)
        if not user:
            flash('Invalid User ID', 'error')
            return redirect(url_for('config.users'))

    return render_template(
        'config/users/edit.html',
        user_id=user_id,
        user=user,
        password_complexity=users.password_complexity.get_requirement_description(),
        base_domain=zones.base_domain
    )


@bp.route('/users/<int:user_id>/edit/save', methods=['POST'])
@login_required
@admin_required
def user_edit_save(user_id):
    provider = Provider()
    users = provider.users()
    zones = provider.dns_zones()

    user = None
    if user_id <= 0:
        user_id = 0
    else:
        user = users.get_user(user_id)
        if not user:
            flash('Invalid User ID', 'error')
            return redirect(url_for('config.users'))

    username = request.form['username'].strip()
    password = request.form['password'].strip()
    full_name = request.form['full_name'].strip()
    email = request.form['email'].strip()
    admin = True if int(request.form.get('admin', 0)) == 1 else False
    ldap = True if int(request.form.get('ldap', 0)) == 1 else False
    active = True if int(request.form.get('active', 0)) == 1 else False

    if user and password == '********':
        password = ''

    if len(username) == 0:
        flash('Please enter a username', 'error')
        return redirect(url_for('config.user_edit', user_id=user_id))
    elif len(password) == 0 and not user:
        flash('Please enter a password', 'error')
        return redirect(url_for('config.user_edit', user_id=user_id))
    elif len(full_name) == 0:
        flash('Please enter full name', 'error')
        return redirect(url_for('config.user_edit', user_id=user_id))
    elif len(email) == 0:
        flash('Please enter an e-mail', 'error')
        return redirect(url_for('config.user_edit', user_id=user_id))
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash('Please enter a valid e-mail', 'error')
        return redirect(url_for('config.user_edit', user_id=user_id))

    user = users.save(user_id, username, password, full_name, email, admin, ldap, active)
    if not user:
        flash('Could not save user: ' + users.last_error, 'error')
        return redirect(url_for('config.user_edit', user_id=user_id))

    # Now create the base domain zone for that user.
    if not zones.create_user_base_zone(user):
        flash('User has been created but there was a problem creating their base domain. Make sure the DNS Base Domain has been set.', 'error')
        return redirect(url_for('config.users'))

    flash('User saved', 'success')
    return redirect(url_for('config.users'))
