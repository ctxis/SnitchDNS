from app.lib.models.user import UserModel
from app import db
import flask_bcrypt as bcrypt
import random
import string
from sqlalchemy import and_, func


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

    def __get(self, user_id=None, username=None, email=None):
        query = UserModel.query

        if user_id is not None:
            query = query.filter(UserModel.id == user_id)

        if username is not None:
            query = query.filter(UserModel.username == username)

        if email is not None:
            query = query.filter(UserModel.email == email)

        return query.first()

    def validate_password(self, hash, password):
        return bcrypt.check_password_hash(hash, password)

    def login_session(self, user):
        user.session_token = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=64))
        db.session.commit()
        db.session.refresh(user)
        return user

    def logout_session(self, user_id):
        user = self.__get(user_id=user_id)
        if user:
            user.session_token = ''
            db.session.commit()
            db.session.refresh(user)
        return True

    def validate_user_password(self, user_id, password):
        user = self.__get(user_id=user_id)
        if not user:
            self.last_error = 'Could not load user'
            return False

        return bcrypt.check_password_hash(user.password, password)

    def update_user_password(self, user_id, password, check_complexity=True):
        user = self.__get(user_id=user_id)
        if not user:
            self.last_error = 'Could not load user'
            return False

        if check_complexity:
            if not self.password_complexity.meets_requirements(password):
                self.last_error = 'Password does not meet complexity requirements: ' + self.password_complexity.get_requirement_description()
                return False

        password = bcrypt.generate_password_hash(password)
        user.password = password

        db.session.commit()
        db.session.refresh(user)

        return True

    def all(self):
        return UserModel.query.order_by(UserModel.id).all()

    def username_exists(self, username, return_object=False):
        user = UserModel.query.filter(and_(func.lower(UserModel.username) == func.lower(username))).first()
        if return_object:
            return user
        return True if user else False

    def save(self, user_id, username, password, full_name, email, admin, ldap, active, check_complexity=True):
        if user_id > 0:
            # Editing an existing user.
            user = self.__get(user_id=user_id)
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
            return True

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
                password = bcrypt.generate_password_hash(password)

        if not ldap:
            # There is no point in updating these if it's an LDAP user.
            user.username = username
            if len(password) > 0:
                user.password = password
            user.full_name = full_name
            user.email = email

        user.admin = True if admin else False
        user.ldap = True if ldap else False
        user.active = True if active else False

        if user_id == 0:
            db.session.add(user)

        db.session.commit()
        db.session.refresh(user)

        return True

    def get_user(self, user_id):
        return self.__get(user_id=user_id)
