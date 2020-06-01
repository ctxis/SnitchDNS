from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/password/complexity', methods=['GET'])
@login_required
@admin_required
def password_complexity():
    return render_template('config/system/password_complexity.html')


@bp.route('/password/complexity/save', methods=['POST'])
@login_required
@admin_required
def password_complexity_save():
    provider = Provider()
    settings = provider.settings()

    pwd_min_length = int(request.form['pwd_min_length'].strip())
    pwd_min_lower = int(request.form['pwd_min_lower'].strip())
    pwd_min_upper = int(request.form['pwd_min_upper'].strip())
    pwd_min_digits = int(request.form['pwd_min_digits'].strip())
    pwd_min_special = int(request.form['pwd_min_special'].strip())

    settings.save('pwd_min_length', pwd_min_length)
    settings.save('pwd_min_lower', pwd_min_lower)
    settings.save('pwd_min_upper', pwd_min_upper)
    settings.save('pwd_min_digits', pwd_min_digits)
    settings.save('pwd_min_special', pwd_min_special)

    flash('Settings saved', 'success')
    return redirect(url_for('config.password_complexity'))
