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

    provider = Provider()
    ldap = provider.ldap()
    radius = provider.radius()

    return render_template(
        'auth/login.html',
        next=request.args.get('next', ''),
        multiauth=(ldap.enabled and radius.enabled)
    )


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
    radius = provider.radius()
    zones = provider.dns_zones()

    # If more than one external methods are defined, the user has to specify which one they want to authenticate
    # against, as we won't be trying each and every one until we get a hit. If only one method is enabled (ie LDAP) then
    # LOCAL auth will be tried first and then it will try LDAP.
    multiauth = ldap.enabled and radius.enabled
    auth = request.form['auth'].strip().lower() if 'auth' in request.form else ''

    login_result = False
    fullname = ''
    email = ''

    if (multiauth is False) or (multiauth is True and auth == 'local'):
        auth = 'local'  # For when multiauth = False.
        login_result = __auth_local(username, password)

    if (login_result is False) and ldap.enabled:
        if (multiauth is False) or (multiauth is True and auth == 'ldap'):
            auth = 'ldap'
            ldap_result, error_message = __auth_ldap(username, password)
            if ldap_result is False:
                error_message = error_message if len(error_message) > 0 else 'Invalid credentials'
                flash(error_message, 'error')
                return redirect(url_for('auth.login', next=next))
            elif ldap_result['result'] == ldap.AUTH_SUCCESS:
                login_result = True
                fullname = ldap_result['user']['fullname'].lower()
                email = ldap_result['user']['email'].lower()
            elif ldap_result['result'] == ldap.AUTH_CHANGE_PASSWORD:
                if ldap.pwchange:
                    session['ldap_username'] = username
                    session['ldap_time'] = int(time.time())
                    flash('Your LDAP password has expired or needs changing', 'error')
                    return redirect(url_for('auth.ldap_changepwd', next=next))
                else:
                    flash('Your LDAP password has expired or needs changing', 'error')
                    return redirect(url_for('auth.login', next=next))
            elif ldap_result['result'] == ldap.AUTH_LOCKED:
                flash('Your AD account is disabled', 'error')
                return redirect(url_for('auth.login', next=next))
            else:
                flash('Invalid credentials', 'error')
                return redirect(url_for('auth.login', next=next))

    if (login_result is False) and radius.enabled:
        if (multiauth is False) or (multiauth is True and auth == 'radius'):
            auth = 'radius'
            radius_result, error_message = __auth_radius(username, password)
            if radius_result is False:
                error_message = error_message if len(error_message) > 0 else 'Invalid credentials'
                flash(error_message, 'error')
                return redirect(url_for('auth.login', next=next))
            login_result = radius_result
            fullname = username.lower()
            email = ''

    if login_result is False:
        flash('Invalid credentials', 'error')
        return redirect(url_for('auth.login', next=next))

    # Check to see if the user exists. This will return false only if it's the first login of an external user.
    user = users.find_user_login(username)
    if not user:
        user = users.save(0, username.lower(), password, fullname.lower(), email.lower(), False, auth, True)
        if not user:
            flash('Could not create external user: {0}'.format(users.last_error), 'error')
            return redirect(url_for('auth.login', next=next))

        # Now create the default zone for that user.
        if not zones.create_user_base_zone(user):
            flash('User has been created but there was a problem creating their base domain. Make sure the DNS Base Domain has been set.', 'error')
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
        session.pop('otp_userid', None)
        session.pop('otp_time', None)

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
        session.pop('otp_userid', None)
        session.pop('otp_time', None)

        return redirect(url_for('auth.login', next=next))

    user = users.get_user(id)
    if not user:
        return redirect(url_for('auth.login', next=next))

    if not users.otp_verify_user(user, otp):
        flash('Invalid Code', 'error')
        return redirect(url_for('auth.login_2fa', next=next))

    session.pop('otp_userid', None)
    session.pop('otp_time', None)

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
    is_azure = current_user.get_auth_name() == 'azure'

    provider = Provider()
    users = provider.users()

    users.logout_session(current_user.id)

    if is_azure:
        azure = Provider().azure()
        return redirect(azure.get_logout_url(url_for('auth.login', _external=True)))
    return redirect(url_for('auth.login'))


@bp.route('/ldap/password', methods=['GET'])
def ldap_changepwd():
    provider = Provider()
    ldap = provider.ldap()

    next = urllib.parse.unquote_plus(request.args.get('next', '').strip())
    if not ldap.pwchange:
        return redirect(url_for('auth.login', next=next))
    
    username = session['ldap_username'] if 'ldap_username' in session else ''
    ldap_time = session['ldap_time'] if 'ldap_time' in session else 0
    if len(username) == 0:
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))
    elif int(time.time()) > (ldap_time + 120):
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))

    return render_template('auth/ldap_password.html', next=request.args.get('next', ''))


@bp.route('/ldap/password', methods=['POST'])
def ldap_changepwd_process():
    provider = Provider()
    ldap = provider.ldap()

    next = urllib.parse.unquote_plus(request.args.get('next', '').strip())
    if not ldap.pwchange:
        return redirect(url_for('auth.login', next=next))

    password = request.form['password'].strip()
    new_password = request.form['new_password'].strip()
    confirm_password = request.form['confirm_password'].strip()

    username = session['ldap_username'] if 'ldap_username' in session else ''
    ldap_time = session['ldap_time'] if 'ldap_time' in session else 0
    if len(username) == 0:
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))
    elif int(time.time()) > (ldap_time + 120):
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))

    if len(password) == 0:
        flash('Please enter your current password', 'error')
        return redirect(url_for('ldap_changepwd', next=next))
    elif len(new_password) == 0 or len(confirm_password) == 0:
        flash('Please enter your new password', 'error')
        return redirect(url_for('ldap_changepwd', next=next))
    elif new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('ldap_changepwd', next=next))

    username = session.pop('ldap_username', None)
    session.pop('ldap_time', None)

    if not ldap.update_password_ad(username, password, new_password):
        flash('Could not update password', 'error')
        return redirect(url_for('auth.login', next=next))

    flash('Password updated - please login again', 'success')
    return redirect(url_for('auth.login', next=next))


def __auth_local(username, password):
    provider = Provider()
    users = provider.users()

    user = users.find_user_login(username, 'local')
    if user and users.validate_password(user.password, password):
        return True
    return False


def __auth_ldap(username, password):
    provider = Provider()
    ldap = provider.ldap()
    result = ldap.authenticate(username, password)

    return result, ldap.error_message


def __auth_radius(username, password):
    provider = Provider()
    radius = provider.radius()
    result = radius.authenticate(username, password)

    return result, radius.error_message


@bp.route('/azure/go', methods=['GET'])
def auth_azure_go():
    if current_user.is_authenticated:
        flash('You are already logged-in', 'success')
        return redirect(url_for('home.index'))

    azure = Provider().azure()
    settings = Provider().settings()

    if int(settings.get('azure_enabled', 0)) != 1:
        flash('The Azure authentication provider is not enabled', 'error')
        return redirect(url_for('auth.login'))

    session['azure_flow'] = azure.build_auth_code_flow()
    return redirect(session['azure_flow']['auth_uri'])


@bp.route('/azure', methods=['GET'])
def auth_azure():
    if current_user.is_authenticated:
        flash('You are already logged-in', 'success')
        return redirect(url_for('home.index'))

    azure = Provider().azure()
    settings = Provider().settings()
    users = Provider().users()
    zones = Provider().dns_zones()

    if int(settings.get('azure_enabled', 0)) != 1:
        flash('The Azure authentication provider is not enabled', 'error')
        return redirect(url_for('auth.login'))

    result = azure.process_response(session.get('azure_flow', {}), request.args)
    if 'error' in result:
        flash("Error: {0} - {1}".format(result['error'], result['error_description']), 'error')
        return redirect(url_for('auth.login'))

    # At this point, the 'result' variable has all the user's information.
    # We need to determine if they exist - if they don't create the user,
    # and then log them in.
    access_token = result['access_token']
    username = result['id_token_claims']['preferred_username']

    graph_user = azure.get_user_info(access_token)
    if 'userPrincipalName' not in graph_user:
        flash('The user graph query returned an empty object - are you sure your Azure AD user is valid?', 'error')
        return redirect(url_for('auth.login'))
    elif graph_user['userPrincipalName'] != username:
        flash(
            'The logged-in user and the graph query confirmation user do not match. Please contact your administrator.',
            'error')
        return redirect(url_for('auth.login'))

    fullname = graph_user['displayName']
    email = graph_user['mail'] if graph_user['mail'] is not None else username
    expires_at = result['id_token_claims']['exp']

    user = users.find_user(username=username)
    if not user:
        # Check to see if the email of the user already exists.
        user = users.find_user(email=email)
        if user:
            flash('This email already exists', 'error')
            return redirect(url_for('auth.login'))

        user = users.save(0, username.lower(), '', fullname, email.lower(), False, 'azure', True)
        if not user:
            flash('Could not create user', 'error')
            return redirect(url_for('auth.login'))

        # Now create the default zone for that user.
        if not zones.create_user_base_zone(user):
            flash('User has been created but there was a problem creating their base domain. Make sure the DNS Base Domain has been set.', 'error')
            return redirect(url_for('auth.login', next=next))

    if user.get_auth_name() != 'azure':
        flash('Your user already exists but there is a mismatch of authentication providers. Please contact your administrator', 'error')
        return redirect(url_for('auth.login'))

    if not user.active:
        # This check has to be after the password validation.
        flash('Your account is disabled.', 'error')
        return redirect(url_for('auth.login', next=next))

    user = users.login_session(user, access_token, expires_at)
    login_user(user)

    # On every login we get the hashcat version and the git hash version.
    system = Provider().system()
    system.run_updates()

    return redirect(url_for('home.index'))
