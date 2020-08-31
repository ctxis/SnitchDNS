from flask import Blueprint

bp = Blueprint('config', __name__, url_prefix='/config')

from . import index
from .system import dns, ldap, password_complexity, smtp, system, users, webpush, slack, logs, teams
from .account import profile, api
