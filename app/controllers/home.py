from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
@login_required
def index():
    return render_template('home/index.html')
