from . import bp
from app.lib.base.decorators import api_auth
from app.lib.api.search import ApiSearch
from flask_login import current_user
from flask import request


@bp.route('/search', methods=['GET'])
@api_auth
def search():
    return ApiSearch().search(request, current_user.id)
