from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
import re


@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    provider = Provider()
    users = provider.users()
    ldap = provider.ldap()

    return render_template(
        'config/account/profile.html',
        user=users.get_user(current_user.id),
        has_email_mapping=(len(ldap.mapping_email) > 0),
        password_complexity=users.password_complexity.get_requirement_description()
    )


@bp.route('/profile/save', methods=['POST'])
@login_required
def profile_save():
    provider = Provider()
    users = provider.users()
    ldap = provider.ldap()

    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")

    user = users.get_user(current_user.id)
    if user.ldap:
        has_email_mapping = (len(ldap.mapping_email) > 0)
        if not has_email_mapping:
            email = request.form['email'].strip().lower().replace(' ', '')
            if len(email) == 0 or not email_regex.match(email):
                flash('Invalid e-mail', 'error')
                return redirect(url_for('config.profile'))
            user = users.update_property(current_user.id, 'email', email)
    else:
        full_name = request.form['full_name'].strip()
        email = request.form['email'].strip().lower().replace(' ', '')

        existing_password = request.form['existing_password'].strip()
        new_password = request.form['new_password'].strip()
        confirm_password = request.form['confirm_password'].strip()

        if len(full_name) == 0:
            flash('Invalid full name', 'error')
            return redirect(url_for('config.profile'))
        elif len(email) == 0 or not email_regex.match(email):
            flash('Invalid e-mail', 'error')
            return redirect(url_for('config.profile'))

        user = users.update_property(current_user.id, 'email', email)
        user = users.update_property(current_user.id, 'full_name', full_name)

        if len(existing_password) > 0 and len(new_password) > 0 and len(confirm_password) > 0:
            # Password change as well.
            if len(existing_password) == 0:
                flash('Please enter your existing password', 'error')
                return redirect(url_for('config.profile'))
            elif len(new_password) == 0:
                flash('Please enter your new password', 'error')
                return redirect(url_for('config.profile'))
            elif new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('config.profile'))

            if not users.validate_user_password(current_user.id, existing_password):
                flash('Invalid existing password', 'error')
                return redirect(url_for('config.profile'))
            elif not users.update_user_password(current_user.id, new_password):
                flash('Could not update password: ' + users.last_error, 'error')
                return redirect(url_for('config.profile'))

            # Force the user to re-login.
            users.logout_session(current_user.id)

            flash('Please login with your new password', 'success')
            return redirect(url_for('config.profile'))

    flash('Profile updated', 'success')
    return redirect(url_for('config.profile'))
