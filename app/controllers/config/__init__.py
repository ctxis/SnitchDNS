from flask import Blueprint

bp = Blueprint('config', __name__, url_prefix='/config')

from . import index, dns, smtp, webpush, ldap, password, password_complexity, users, daemon
