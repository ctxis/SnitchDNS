from flask import Blueprint
from flask_login import login_user, current_user, login_required
from flask import render_template, redirect, url_for, flash, request, session
from app.lib.base.provider import Provider
from werkzeug.urls import url_parse
import urllib
import time


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
    ldap = provider.ldap()
    zones = provider.dns_zones()

    # First lookup local users.
    user = users.find_user_login(username, False)
    if user:
        if not users.validate_password(user.password, password):
            flash('Invalid credentials', 'error')
            return redirect(url_for('auth.login', next=next))
    elif ldap.enabled:
        ldap_user = ldap.authenticate(username, password)
        if not ldap_user:
            if len(ldap.error_message) > 0:
                flash(ldap.error_message, 'error')
            else:
                flash('Invalid credentials', 'error')
            return redirect(url_for('auth.login', next=next))

        # Now see if the user exists.
        user = users.find_user_login(username, True)
        if not user:
            # Doesn't exist yet, we'll have to create them now.
            user = users.save(0, ldap_user['username'].lower(), password, ldap_user['fullname'], ldap_user['email'], False, True, True)
            if not user:
                flash('Could not create LDAP user: {0}'.format(users.last_error), 'error')
                return redirect(url_for('auth.login', next=next))

            # Now we need to create a zone for that user.
            if not zones.create_user_base_zone(user):
                flash('User has been created but there was a problem creating their base domain. Make sure the DNS Base Domain has been set.', 'error')
                return redirect(url_for('auth.login', next=next))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('auth.login', next=next))

    if not user.active:
        # This check has to be after the password validation.
        flash('Your account is disabled.', 'error')
        return redirect(url_for('auth.login', next=next))

    # Forward to 2FA validation if it's enabled.
    if user.has_2fa():
        session['otp_userid'] = user.id
        session['otp_time'] = int(time.time())
        return redirect(url_for('auth.login_2fa', next=next))

    # If we reach this point it means that our user exists. Check if the user is active.
    user = users.login_session(user)
    login_user(user)

    # On every login we get the hashcat version and the git hash version.
    system = provider.system()
    system.run_updates()

    if next and url_parse(next).netloc == '':
        return redirect(next)

    return redirect(url_for('home.index'))


@bp.route('/login/2fa', methods=['GET'])
def login_2fa():
    next = urllib.parse.unquote_plus(request.args.get('next', '').strip())
    provider = Provider()
    users = provider.users()
    
    id = int(session['otp_userid']) if 'otp_userid' in session else 0
    otp_time = int(session['otp_time']) if 'otp_time' in session else 0

    can_continue = True
    if id <= 0:
        can_continue = False
    elif int(time.time()) > (otp_time + 120):
        # This page is valid for 2 minutes.
        can_continue = False

    if not can_continue:
        if 'otp_userid' in session:
            del session['otp_userid']
        if 'otp_time' in session:
            del session['otp_time']

        return redirect(url_for('auth.login', next=next))

    user = users.get_user(id)
    if not user:
        return redirect(url_for('auth.login', next=next))

    return render_template('auth/login_2fa.html', next=request.args.get('next', ''))


@bp.route('/login/2fa', methods=['POST'])
def login_2fa_process():
    next = urllib.parse.unquote_plus(request.args.get('next', '').strip())
    otp = request.form['otp'].strip()

    provider = Provider()
    users = provider.users()

    id = int(session['otp_userid']) if 'otp_userid' in session else 0
    otp_time = int(session['otp_time']) if 'otp_time' in session else 0

    can_continue = True
    if id <= 0:
        can_continue = False
    elif int(time.time()) > (otp_time + 120):
        # This page is valid for 2 minutes.
        can_continue = False

    if not can_continue:
        if 'otp_userid' in session:
            del session['otp_userid']
        if 'otp_time' in session:
            del session['otp_time']

        return redirect(url_for('auth.login', next=next))

    user = users.get_user(id)
    if not user:
        return redirect(url_for('auth.login', next=next))

    if not users.otp_verify_user(user, otp):
        flash('Invalid Code', 'error')
        return redirect(url_for('auth.login_2fa', next=next))

    del session['otp_userid']
    del session['otp_time']

    # If we reach this point it means that our user exists. Check if the user is active.
    user = users.login_session(user)
    login_user(user)

    # On every login we get the hashcat version and the git hash version.
    system = provider.system()
    system.run_updates()

    if next and url_parse(next).netloc == '':
        return redirect(next)

    return redirect(url_for('home.index'))


@bp.route('/logout', methods=['GET'])
@login_required
def logout():
    provider = Provider()
    users = provider.users()

    users.logout_session(current_user.id)
    return redirect(url_for('auth.login'))
