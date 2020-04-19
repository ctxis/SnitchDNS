from . import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/ldap', methods=['GET'])
@login_required
@admin_required
def ldap():
    return render_template('config/ldap.html')


@bp.route('/ldap/save', methods=['POST'])
@login_required
@admin_required
def ldap_save():
    provider = Provider()
    settings = provider.settings()

    ldap_enabled = True if int(request.form.get('ldap_enabled', 0)) == 1 else False
    ldap_ssl = True if int(request.form.get('ldap_ssl', 0)) == 1 else False
    ldap_bind_pass = request.form['ldap_bind_pass'].strip()

    # Put the rest of the ldap options in a dict to make it easier to validate and save.
    ldap_settings = {
        'ldap_host': {'value': request.form['ldap_host'].strip(), 'error': 'LDAP Host cannot be empty'},
        'ldap_base_dn': {'value': request.form['ldap_base_dn'].strip(), 'error': 'LDAP Base cannot be empty'},
        'ldap_domain': {'value': request.form['ldap_domain'].strip(), 'error': 'LDAP Domain cannot be empty'},
        'ldap_bind_user': {'value': request.form['ldap_bind_user'].strip(), 'error': 'LDAP Bind User cannot be empty'},
        'ldap_mapping_username': {'value': request.form['ldap_mapping_username'].strip(),
                                  'error': 'LDAP Mapping Username cannot be empty'},
        'ldap_mapping_fullname': {'value': request.form['ldap_mapping_fullname'].strip(),
                                  'error': 'LDAP Mapping Full Name cannot be empty'}
    }

    has_errors = False
    if ldap_enabled:
        # If it's disabled it doesn't make sense to validate any settings.
        for key, data in ldap_settings.items():
            if len(data['value']) == 0:
                has_errors = True
                flash(data['error'], 'error')

    if has_errors:
        return redirect(url_for('config.ldap'))

    settings.save('ldap_mapping_email', request.form['ldap_mapping_email'].strip())
    settings.save('ldap_enabled', ldap_enabled)
    settings.save('ldap_ssl', ldap_ssl)
    for key, data in ldap_settings.items():
        settings.save(key, data['value'])

    # If the password is not '********' then save it. This is because we show that value instead of the actual password.
    if len(ldap_bind_pass) > 0 and ldap_bind_pass != '********':
        settings.save('ldap_bind_pass', ldap_bind_pass)

    flash('Settings saved', 'success')
    return redirect(url_for('config.ldap'))















    smtp_enable = True if int(request.form.get('smtp_enable', 0)) == 1 else False
    smtp_host = request.form['smtp_host'].strip()
    smtp_port = int(request.form['smtp_port'].strip())
    smtp_tls = True if int(request.form.get('smtp_tls', 0)) == 1 else False
    smtp_user = request.form['smtp_user'].strip()
    smtp_pass = request.form['smtp_pass'].strip()
    if smtp_pass == '********':
        smtp_pass = ''

    if len(smtp_host) == 0:
        flash('Please enter SMTP Host', 'error')
        return redirect(url_for('config.smtp'))
    elif smtp_port <= 0 or smtp_port > 65535:
        flash('Please enter SMTP Port', 'error')
        return redirect(url_for('config.smtp'))
    elif len(smtp_user) == 0:
        flash('Please enter SMTP User', 'error')
        return redirect(url_for('config.smtp'))

    # Checking for the password is a bit different. If there's a password stored already in the database, we check
    # if the password is ********. If it is, we don't update but we let it go through. If it isn't, we update.
    existing_password = settings.get('smtp_pass', '')
    if len(existing_password) == 0:
        # If there's no stored password, require one.
        if len(smtp_pass) == 0:
            flash('Please enter SMTP Pass', 'error')
            return redirect(url_for('config.smtp'))
        else:
            update_password = True
    else:
        if len(smtp_pass) > 0:
            update_password = True
        else:
            # Don't update the password as the user probably updated something else on the form.
            update_password = False

    settings.save('smtp_enable', smtp_enable)
    settings.save('smtp_host', smtp_host)
    settings.save('smtp_port', smtp_port)
    settings.save('smtp_tls', smtp_tls)
    settings.save('smtp_user', smtp_user)
    if update_password:
        settings.save('smtp_pass', smtp_pass)

    flash('Settings saved', 'success')
    return redirect(url_for('config.smtp'))
