from . import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider


@bp.route('/webpush', methods=['GET'])
@login_required
def webpush():
    return render_template('config/webpush.html')


@bp.route('/webpush/save', methods=['POST'])
@login_required
def webpush_save():
    provider = Provider()
    settings = provider.settings()

    vapid_private = request.form['vapid_private'].strip()
    vapid_public = request.form['vapid_public'].strip()
    webpush_enabled = True if int(request.form.get('webpush_enabled', 0)) == 1 else False
    if vapid_private == '********':
        vapid_private = ''

    if webpush_enabled:
        if len(vapid_private) == 0:
            existing_vapid_private = settings.get('vapid_private', '')
            if len(existing_vapid_private) == 0:
                flash('Please enter a VAPID Private Key', 'error')
                return redirect(url_for('config.webpush'))
        elif len(vapid_public) == 0:
            flash('Please enter a VAPID Public Key', 'error')
            return redirect(url_for('config.webpush'))

    settings.save('vapid_private', vapid_private)
    settings.save('vapid_public', vapid_public)
    settings.save('webpush_enabled', webpush_enabled)

    flash('Settings saved', 'success')
    return redirect(url_for('config.webpush'))
