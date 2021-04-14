from .. import bp
from flask import request, render_template, flash, redirect, url_for, session
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
import re


@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    provider = Provider()
    users = provider.users()
    ldap = provider.ldap()

    user = users.get_user(current_user.id)
    auth_type = users.get_authtype(id=user.auth_type_id).name

    return render_template(
        'config/account/profile/general.html',
        user=user,
        has_email_mapping=(len(ldap.mapping_email) > 0),
        password_complexity=users.password_complexity.get_requirement_description(),
        auth_type=auth_type.lower(),
        ldap_pwdchange=ldap.pwchange
    )


@bp.route('/profile/save', methods=['POST'])
@login_required
def profile_save():
    provider = Provider()
    users = provider.users()
    ldap = provider.ldap()

    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")

    user = users.get_user(current_user.id)
    auth_type = users.get_authtype(id=user.auth_type_id)
    if not auth_type:
        flash('Invalid authentication type', 'error')
        return redirect(url_for('config.profile'))

    if auth_type.name.lower() == 'ldap':
        has_email_mapping = (len(ldap.mapping_email) > 0)
        if not has_email_mapping:
            email = request.form['email'].strip().lower().replace(' ', '')
            if len(email) == 0 or not email_regex.match(email):
                flash('Invalid e-mail', 'error')
                return redirect(url_for('config.profile'))
            user = users.update_property(current_user.id, 'email', email)

        if ldap.pwchange:
            existing_password = request.form['existing_password'].strip()
            new_password = request.form['new_password'].strip()
            confirm_password = request.form['confirm_password'].strip()

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

                if not ldap.update_password_ad(user.username, existing_password, new_password):
                    if len(ldap.error_message) > 0:
                        flash(ldap.error_message, 'error')
                    else:
                        flash('Could not update password', 'error')
                    return redirect(url_for('config.profile'))

                # Force the user to re-login.
                users.logout_session(current_user.id)

                flash('Please login with your new password', 'success')
                return redirect(url_for('config.profile'))
    elif auth_type.name.lower() == 'local':
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


@bp.route('/profile/2fa', methods=['GET'])
@login_required
def profile_2fa():
    provider = Provider()
    users = provider.users()

    twofa_enabled = False if current_user.otp_secret is None else len(current_user.otp_secret) > 0
    otp = users.otp_new(current_user)

    # Save the secret into the session to prevent users from setting their own during the request.
    session['otp'] = otp['secret']

    return render_template(
        'config/account/profile/2fa.html',
        twofa_enabled=twofa_enabled,
        otp_secret=otp['secret'],
        otp_uri=otp['uri']
    )


@bp.route('/profile/2fa/save', methods=['POST'])
@login_required
def profile_2fa_save():
    provider = Provider()
    users = provider.users()

    if users.has_2fa(current_user.id):
        # This will be treated as a "disable 2fa" request.
        action = request.form['action'] if 'action' in request.form else ''
        if action == 'disable':
            users.twofa_disable(current_user.id)

            users.logout_session(current_user.id)
            flash('Two Factor Authentication has been disabled. Please login again.')
            return redirect(url_for('auth.login'))
    else:
        # This will be treated as an "enable 2fa" request.
        otp_code = request.form['otp'].strip()
        otp_secret = ''
        if 'otp' in session:
            otp_secret = session['otp']
            del session['otp']

        if len(otp_secret) == 0:
            flash('Could not load OTP secret from session.', 'error')
            return redirect(url_for('config.profile_2fa'))
        elif len(otp_code) == 0:
            flash('OTP code is missing', 'error')
            return redirect(url_for('config.profile_2fa'))

        if not users.otp_verify(otp_secret, otp_code):
            flash('Invalid OTP Code', 'error')
            return redirect(url_for('config.profile_2fa'))

        if not users.twofa_enable(current_user.id, otp_secret):
            flash('Could not enable 2FA', 'error')
            return redirect(url_for('config.profile_2fa'))

        users.logout_session(current_user.id)
        flash('Two Factor Authentication has been enabled. Please login again.')
        return redirect(url_for('auth.login'))

    return redirect(url_for('config.profile_2fa'))
