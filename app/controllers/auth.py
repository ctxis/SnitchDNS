from flask import Blueprint
from flask_login import login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, request
from app.lib.models.user import UserModel
from sqlalchemy import and_, func
from app.lib.base.provider import Provider
from werkzeug.urls import url_parse
import urllib


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    return render_template('auth/login.html', next=request.args.get('next', ''))


@bp.route('/login', methods=['POST'])
def login_process():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    username = request.form['username'].strip()
    password = request.form['password'].strip()

    next = urllib.parse.unquote_plus(request.form['next'].strip())
    provider = Provider()
    users = provider.users()

    user = UserModel.query.filter(and_(func.lower(UserModel.username) == func.lower(username))).first()
    if not user:
        flash('Invalid credentials', 'error')
        return redirect(url_for('auth.login', next=next))
    elif not users.validate_password(user.password, password):
        flash('Invalid credentials', 'error')
        return redirect(url_for('auth.login', next=next))
    elif not user.active:
        # This check has to be after the password validation.
        flash('Your account is disabled.', 'error')
        return redirect(url_for('auth.login', next=next))

    user = users.login_session(user)
    login_user(user)

    # On every login we get the hashcat version and the git hash version.
    system = provider.system()
    system.run_updates()

    if next and url_parse(next).netloc == '':
        return redirect(next)

    return redirect(url_for('home.index'))


@bp.route('/logout', methods=['GET'])
def logout():
    provider = Provider()
    users = provider.users()

    users.logout_session(current_user.id)
    logout_user()
    return redirect(url_for('auth.login'))
