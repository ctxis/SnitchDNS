from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/logs/errors', methods=['GET'])
@login_required
@admin_required
def logs_errors():
    provider = Provider()
    logging = provider.logging()

    default_per_page = 20

    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', default_per_page)

    if isinstance(page, str):
        page = int(page) if page.isdigit() else 1
    if isinstance(per_page, str):
        per_page = int(per_page) if per_page.isdigit() else 1

    if page <= 0:
        page = 1

    if per_page <= 0:
        per_page = default_per_page

    return render_template(
        'config/system/logs/errors.html',
        results=logging.view_errors(page, per_page)
    )
