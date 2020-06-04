from . import bp
from app.lib.base.decorators import api_auth
from app.lib.api.search import ApiSearch
from flask_login import current_user
from flask import request


@bp.route('/search', methods=['GET'])
@api_auth
def search():
    user_id = None if current_user.admin else current_user.id
    return ApiSearch().search(request, user_id, current_user.admin)
