from app.lib.models.user import UserModel
from app import db
from flask import current_app
import flask_bcrypt as bcrypt
import random
import string
import datetime
import os
from sqlalchemy import and_, func
from flask_login import logout_user
import pyotp


class UserManager:
    def __init__(self, password_complexity):
        self.__last_error = ''
        self.password_complexity = password_complexity

    @property
    def last_error(self):
        return self.__last_error

    @last_error.setter
    def last_error(self, value):
        self.__last_error = value

    def __get(self, user_id=None, username=None, email=None, ldap=None, active=None, admin=None):
        query = UserModel.query

        if user_id is not None:
            query = query.filter(UserModel.id == user_id)

        if username is not None:
            query = query.filter(func.lower(UserModel.username) == func.lower(username))

        if email is not None:
            query = query.filter(func.lower(UserModel.email) == func.lower(email))

        if ldap is not None:
            query = query.filter(UserModel.ldap == ldap)

        if active is not None:
            query = query.filter(UserModel.active == active)

        if admin is not None:
            query = query.filter(UserModel.admin == admin)

        query = query.order_by(UserModel.id)

        return query.all()

    def validate_password(self, hash, password):
        return bcrypt.check_password_hash(hash, password)

    def login_session(self, user):
        user.session_token = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=64))
        db.session.commit()
        db.session.refresh(user)
        return user

    def logout_session(self, user_id):
        user = self.get_user(user_id)
        if user:
            user.session_token = ''
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

    def save(self, user_id, username, password, full_name, email, admin, ldap, active, check_complexity=True):
        if user_id > 0:
            # Editing an existing user.
            user = self.get_user(user_id)
            if not user:
                self.last_error = 'Could not load user'
                return False
        else:
            # Create a user.
            user = UserModel()

        # If it's an existing user and it's the LDAP status that has changed, update only that and return
        # because otherwise it will clear the fields (as the fields are not posted during the submit.
        if user_id > 0 and user.ldap != ldap:
            user.ldap = True if ldap else False
            user.active = True if active else False
            db.session.commit()
            db.session.refresh(user)
            return user

        # If there was a username update, check to see if the new username already exists.
        if username != user.username:
            if self.username_exists(username):
                self.last_error = 'Username already exists'
                return False

        if ldap:
            # This is an LDAP user, no point in setting their password.
            password = ''
        else:
            if len(password) > 0:
                if check_complexity and not self.password_complexity.meets_requirements(password):
                    self.last_error = 'Password does not meet complexity requirements: ' + self.password_complexity.get_requirement_description()
                    return False

                # If the password is empty, it means it wasn't changed.
                password = self.__hash_password(password)

        if (user_id == 0) or (ldap is False):
            user.username = username
            if len(password) > 0:
                user.password = password
            user.full_name = full_name
            user.email = email

        user.admin = True if admin else False
        user.ldap = True if ldap else False
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

    def get_user(self, user_id):
        users = self.__get(user_id=user_id)
        if len(users) == 0:
            return False
        return users[0]

    def is_admin(self, user_id):
        user = self.get_user(user_id)
        if not user:
            return False
        return user.admin

    def find_user_login(self, username, ldap):
        users = self.__get(username=username, ldap=ldap)
        if len(users) == 0:
            return False
        return users[0]

    def get_user_data_path(self, user_id, filename=''):
        path = os.path.join(current_app.root_path, '..', 'data', 'users', str(user_id))
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            if not os.path.isdir(path):
                return False

        if len(filename) > 0:
            filename = filename.replace('..', '').replace('/', '')
            path = os.path.join(path, filename)

        return os.path.realpath(path)

    def get_admins(self, active=None):
        return self.__get(admin=True, active=active)

    def otp_new(self, user):
        otp_secret = pyotp.random_base32(16)
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
