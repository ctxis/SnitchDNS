from . import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider


@bp.route('/password', methods=['GET'])
@login_required
def password():
    if current_user.ldap:
        flash('LDAP users cannot change password')
        return redirect(url_for('home.index'))
    return render_template('config/password.html')


@bp.route('/password/save', methods=['POST'])
@login_required
def password_save():
    provider = Provider()
    users = provider.users()

    if current_user.ldap:
        flash('LDAP users cannot change password')
        return redirect(url_for('home.index'))

    existing_password = request.form['existing_password'].strip()
    new_password = request.form['new_password'].strip()
    confirm_password = request.form['confirm_password'].strip()

    if len(existing_password) == 0:
        flash('Please enter your existing password', 'error')
        return redirect(url_for('config.password'))
    elif len(new_password) == 0:
        flash('Please enter your new password', 'error')
        return redirect(url_for('config.password'))
    elif new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('config.password'))

    if not users.validate_user_password(current_user.id, existing_password):
        flash('Invalid existing password', 'error')
        return redirect(url_for('config.password'))
    elif not users.update_user_password(current_user.id, new_password):
        flash('Could not update password: ' + users.last_error, 'error')
        return redirect(url_for('config.password'))

    flash('Password updated', 'success')
    return redirect(url_for('config.password'))
