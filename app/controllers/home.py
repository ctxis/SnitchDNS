from flask import Blueprint
from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def index():
    # This function deliberately doesn't have a @login_required parameter because we want to run a check for a
    # 'first-visit' type scenario, in order to create the administrator.

    provider = Provider()
    zones = provider.dns_zones()
    users = provider.users()
    if users.count() == 0:
        # Looks like we need to setup the administrator.
        return redirect(url_for('install.index'))

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    search = provider.search()
    results = search.search_from_request(request, user_ids=current_user.id)

    return render_template(
        'home/index.html',
        results=results['results'],
        params=results['params'],
        page_url='home.index',
        zone_count=zones.count(user_id=current_user.id)
    )
