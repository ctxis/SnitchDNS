from flask import Blueprint

bp = Blueprint('config', __name__)

from . import index, forwarding, smtp, webpush, ldap, password, password_complexity, users
