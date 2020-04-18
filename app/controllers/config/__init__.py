from flask import Blueprint

bp = Blueprint('config', __name__)

from . import index, forwarding
