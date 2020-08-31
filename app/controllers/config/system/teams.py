from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/teams', methods=['GET'])
@login_required
@admin_required
def teams():
    return render_template('config/system/teams.html')


@bp.route('/teams/save', methods=['POST'])
@login_required
@admin_required
def teams_save():
    provider = Provider()
    settings = provider.settings()

    teams_enabled = True if int(request.form.get('teams_enabled', 0)) == 1 else False

    settings.save('teams_enabled', teams_enabled)

    flash('Settings saved', 'success')
    return redirect(url_for('config.teams'))
