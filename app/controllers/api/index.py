from . import bp
from flask import redirect, url_for, Response
from app.lib.api.base import ApiBase


@bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('api.swagger'))


@bp.route('/swagger.yaml', methods=['GET'])
def swagger():
    base = ApiBase()
    contents = base.get_swagger_file('v1')

    response = Response()
    response.headers.add('Content-Type', 'text/plain')
    response.data = contents
    return response
