from flask import Blueprint

bp = Blueprint('dns', __name__, url_prefix='/dns')

from . import zones, records, notifications, restrictions, upload
