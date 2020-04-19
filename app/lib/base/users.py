from app.lib.models.user import UserModel
from app import db
import flask_bcrypt as bcrypt
import random
import string


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
