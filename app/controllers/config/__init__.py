from flask import Blueprint

bp = Blueprint('config', __name__)

from . import index, dns, smtp, webpush, ldap, password, password_complexity, users
