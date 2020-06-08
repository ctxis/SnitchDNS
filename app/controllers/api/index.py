from . import bp
from flask import redirect, url_for, Response
from flask_login import login_required
from app.lib.api.base import ApiBase


@bp.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('api.swagger'))


@bp.route('/swagger.yaml', methods=['GET'])
@login_required
def swagger():
    base = ApiBase()
    contents = base.get_swagger_file('v1')

    response = Response(mimetype='text/plain')
    response.data = contents
    return response
