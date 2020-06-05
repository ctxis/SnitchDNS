from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/smtp', methods=['GET'])
@login_required
@admin_required
def smtp():
    return render_template('config/system/smtp.html')


@bp.route('/smtp/save', methods=['POST'])
@login_required
@admin_required
def smtp_save():
    provider = Provider()
    settings = provider.settings()

    smtp_enable = True if int(request.form.get('smtp_enable', 0)) == 1 else False
    smtp_host = request.form['smtp_host'].strip()
    smtp_port = int(request.form['smtp_port'].strip())
    smtp_tls = True if int(request.form.get('smtp_tls', 0)) == 1 else False
    smtp_user = request.form['smtp_user'].strip()
    smtp_pass = request.form['smtp_pass'].strip()
    smtp_sender = request.form['smtp_sender'].strip()

    if len(smtp_host) == 0:
        flash('Please enter SMTP Host', 'error')
        return redirect(url_for('config.smtp'))
    elif smtp_port <= 0 or smtp_port > 65535:
        flash('Please enter SMTP Port', 'error')
        return redirect(url_for('config.smtp'))
    elif len(smtp_user) == 0:
        flash('Please enter SMTP User', 'error')
        return redirect(url_for('config.smtp'))
    elif len(smtp_pass) == 0:
        flash('Please enter SMTP Pass', 'error')
        return redirect(url_for('config.smtp'))
    elif smtp_pass == '********' and len(settings.get('smtp_pass', '')) == 0:
        flash('Please enter SMTP Pass', 'error')
        return redirect(url_for('config.smtp'))
    elif len(smtp_sender) == 0:
        flash('Please enter SMTP Sender E-mail', 'error')
        return redirect(url_for('config.smtp'))

    settings.save('smtp_enable', smtp_enable)
    settings.save('smtp_host', smtp_host)
    settings.save('smtp_port', smtp_port)
    settings.save('smtp_tls', smtp_tls)
    settings.save('smtp_user', smtp_user)
    settings.save('smtp_sender', smtp_sender)
    if smtp_pass != '********':
        settings.save('smtp_pass', smtp_pass)

    flash('Settings saved', 'success')
    return redirect(url_for('config.smtp'))


@bp.route('/smtp/test', methods=['POST'])
@login_required
@admin_required
def smtp_test():
    emails = Provider().emails()

    recipient = request.form['test_email_recipient'].strip()

    result = emails.send(recipient, 'SnitchDNS - Test Message', 'Snitches get notifications!')
    if result is not True:
        flash('Could not send e-mail: ' + str(result), 'error')
    else:
        flash('E-mail sent', 'success')

    return redirect(url_for('config.smtp'))
