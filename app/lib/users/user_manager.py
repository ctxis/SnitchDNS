from app.lib.models.user import UserModel, AuthTypeModel
from app.lib.users.instances.authtype import AuthType
from app.lib.dns.helpers.shared import SharedHelper
from app import db
import flask_bcrypt as bcrypt
import random
import string
import datetime
from sqlalchemy import and_, func
from flask_login import logout_user
import pyotp


class UserManager(SharedHelper):
    def __init__(self, password_complexity):
        self.__last_error = ''
        self.password_complexity = password_complexity

    @property
    def last_error(self):
        return self.__last_error

    @last_error.setter
    def last_error(self, value):
        self.__last_error = value

    def __get(self, user_id=None, username=None, email=None, active=None, admin=None, auth_type_id=None):
        query = UserModel.query

        if user_id is not None:
            query = query.filter(UserModel.id == user_id)

        if username is not None:
            query = query.filter(func.lower(UserModel.username) == func.lower(username))

        if email is not None:
            query = query.filter(func.lower(UserModel.email) == func.lower(email))

        if auth_type_id is not None:
            query = query.filter(UserModel.auth_type_id == auth_type_id)

        if active is not None:
            query = query.filter(UserModel.active == active)

        if admin is not None:
            query = query.filter(UserModel.admin == admin)

        query = query.order_by(UserModel.id)

        return query.all()

    def __get_authtype(self, id=None, name=None):
        query = AuthTypeModel.query

        if id is not None:
            query = query.filter(AuthTypeModel.id == id)

        if name is not None:
            query = query.filter(func.lower(AuthTypeModel.name) == func.lower(name))

        return query.all()

    def validate_password(self, hash, password):
        return bcrypt.check_password_hash(hash, password)

    def login_session(self, user, access_token=None, access_token_expiration=None):
        user.session_token = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=64))
        if access_token is not None:
            user.access_token = access_token
        if access_token_expiration is not None:
            user.access_token_expiration = access_token_expiration
        db.session.commit()
        db.session.refresh(user)
        return user

    def logout_session(self, user_id):
        user = self.get_user(user_id)
        if user:
            user.session_token = ''
            user.access_token = ''
            user.access_token_expiration = 0
            db.session.commit()
            db.session.refresh(user)
        logout_user()
        return True

    def validate_user_password(self, user_id, password):
        user = self.get_user(user_id)
        if not user:
            self.last_error = 'Could not load user'
            return False

        return bcrypt.check_password_hash(user.password, password)

    def update_user_password(self, user_id, password, check_complexity=True):
        user = self.get_user(user_id)
        if not user:
            self.last_error = 'Could not load user'
            return False

        if check_complexity:
            if not self.password_complexity.meets_requirements(password):
                self.last_error = 'Password does not meet complexity requirements: ' + self.password_complexity.get_requirement_description()
                return False

        password = self.__hash_password(password)
        user.password = password

        db.session.commit()
        db.session.refresh(user)

        return True

    def __hash_password(self, password):
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def all(self):
        return UserModel.query.order_by(UserModel.id).all()

    def count(self):
        return db.session.query(UserModel).count()

    def username_exists(self, username, return_object=False):
        user = UserModel.query.filter(and_(func.lower(UserModel.username) == func.lower(username))).first()
        if return_object:
            return user
        return True if user else False

    def save(self, user_id, username, password, full_name, email, admin, auth, active, check_complexity=True, hash_password=True):
        auth = auth.lower()
        auth_type = self.get_authtype(name=auth)
        if not auth_type:
            self.last_error = 'Invalid authentication type'
            return False

        if user_id > 0:
            # Editing an existing user.
            user = self.get_user(user_id)
            if not user:
                self.last_error = 'Could not load user'
                return False
        else:
            # Create a user.
            user = UserModel()

        # If it's an existing user and it's the auth type that has changed, update only that and return
        # because otherwise it will clear the fields (as the fields are not posted during the submit).
        if user_id > 0 and user.auth_type_id != auth_type.id:
            user.auth_type_id = auth_type.id
            user.active = True if active else False
            db.session.commit()
            db.session.refresh(user)
            return user

        # If there was a username update, check to see if the new username already exists.
        if username != user.username:
            if self.username_exists(username):
                self.last_error = 'Username already exists'
                return False

        if auth != 'local':
            # This is an external auth, no point in setting their password.
            password = ''
        else:
            if len(password) > 0:
                if check_complexity and not self.password_complexity.meets_requirements(password):
                    self.last_error = 'Password does not meet complexity requirements: ' + self.password_complexity.get_requirement_description()
                    return False

                # If the password is empty, it means it wasn't changed.
                # Via the CLI a user can pass the hash directly, that's why this variable exists.
                if hash_password:
                    password = self.__hash_password(password)

        if (user_id == 0) or (auth == 'local'):
            user.username = username
            if len(password) > 0:
                user.password = password
            user.full_name = full_name
            user.email = email

        user.admin = True if admin else False
        user.auth_type_id = auth_type.id
        user.active = True if active else False

        if user_id == 0:
            user.created_at = datetime.datetime.now()
            db.session.add(user)

        db.session.commit()
        db.session.refresh(user)

        return user

    def update_property(self, user_id, property, value):
        user = self.get_user(user_id)
        if not user:
            return False

        if property == 'email':
            user.email = value
        elif property == 'full_name':
            user.full_name = value

        db.session.commit()
        db.session.refresh(user)

        return user

    def get_authtype(self, id=None, name=None):
        authtypes = self.__get_authtype(id=id, name=name)
        if len(authtypes) == 0:
            return False
        return AuthType(authtypes[0])

    def add_authtype(self, name):
        type = AuthType(AuthTypeModel())
        type.name = name

        type.save()
        return type

    def authtypes_all(self):
        types = {}
        auth_types = self.__get_authtype()
        for type in auth_types:
            types[type.id] = type.name
        return types

    def set_auth_method_by_name(self, user_id, auth_type_name):
        type = self.get_authtype(name=auth_type_name)
        if not type:
            return False

        user = self.get_user(user_id)
        if not user:
            return False

        user.auth_type_id = type.id
        db.session.commit()
        db.session.refresh(user)

        return True

    def get_user(self, user_id):
        users = self.__get(user_id=user_id)
        if len(users) == 0:
            return False
        return users[0]

    def find_user(self, username=None, email=None):
        if username is None and email is None:
            return False

        results = self.__get(username=username, email=email)
        return results[0] if len(results) > 0 else False


    def is_admin(self, user_id):
        user = self.get_user(user_id)
        if not user:
            return False
        return user.admin

    def find_user_login(self, username, auth=None):
        if auth is not None:
            auth_type = self.get_authtype(name=auth)
            if not auth_type:
                return False
            auth = auth_type.id

        users = self.__get(username=username, auth_type_id=auth)
        if len(users) == 0:
            return False
        return users[0]

    def get_admins(self, active=None):
        return self.__get(admin=True, active=active)

    def otp_new(self, user):
        otp_secret = pyotp.random_base32(32)
        otp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(user.username, issuer_name='SnitchDNS')
        return {
            'secret': otp_secret,
            'uri': otp_uri
        }

    def otp_verify(self, otp_secret, code):
        return pyotp.totp.TOTP(otp_secret).verify(code)

    def twofa_enable(self, user_id, otp_secret):
        user = self.get_user(user_id)
        if not user:
            return False

        user.otp_secret = otp_secret
        user.otp_last_used = ''
        db.session.commit()
        db.session.refresh(user)

        return True

    def twofa_disable(self, user_id):
        user = self.get_user(user_id)
        if not user:
            return False

        user.otp_secret = ''
        user.otp_last_used = ''

        db.session.commit()
        db.session.refresh(user)

        return True

    def has_2fa(self, user_id):
        user = self.get_user(user_id)
        if not user:
            return False
        return False if user.otp_secret is None else len(user.otp_secret) > 0

    def otp_verify_user(self, user, code):
        if user.otp_last_used == code:
            # Someone is trying to re-use the previous code.
            return False
        elif not self.otp_verify(user.otp_secret, code):
            return False

        # Save last valid otp.
        user.otp_last_used = code

        db.session.commit()
        db.session.refresh(user)

        return True
