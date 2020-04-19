from . import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider


@bp.route('/smtp', methods=['GET'])
@login_required
def smtp():
    return render_template('config/smtp.html')


@bp.route('/smpt/save', methods=['POST'])
@login_required
def smtp_save():
    provider = Provider()
    settings = provider.settings()

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

    settings.save('smtp_host', smtp_host)
    settings.save('smtp_port', smtp_port)
    settings.save('smtp_tls', smtp_tls)
    settings.save('smtp_user', smtp_user)
    if update_password:
        settings.save('smtp_pass', smtp_pass)

    flash('Settings saved', 'success')
    return redirect(url_for('config.smtp'))
