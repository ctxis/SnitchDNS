from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, flash
from app.lib.base.provider import Provider


def admin_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        if not current_user.admin:
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

        return f(**kwargs)
    return wrapped_view


def must_have_base_domain(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        if not current_user.admin:
            if len(Provider().dns_zones().base_domain) == 0:
                flash('The base domain has not been configured by your administrator.', 'error')
                return redirect(url_for('home.index'))
        return f(**kwargs)
    return wrapped_view


def api_auth(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        from app.lib.api.auth import ApiAuth
        from app.lib.api.base import ApiBase
        if not ApiAuth().auth(True):
            return ApiBase().send_access_denied_response()
        return f(**kwargs)
    return wrapped_view
