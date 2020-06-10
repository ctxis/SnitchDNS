from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/slack', methods=['GET'])
@login_required
@admin_required
def slack():
    return render_template('config/system/slack.html')


@bp.route('/slack/save', methods=['POST'])
@login_required
@admin_required
def slack_save():
    provider = Provider()
    settings = provider.settings()

    slack_enabled = True if int(request.form.get('slack_enabled', 0)) == 1 else False

    settings.save('slack_enabled', slack_enabled)

    flash('Settings saved', 'success')
    return redirect(url_for('config.slack'))
