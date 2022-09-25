from app import db, login
from flask_login import UserMixin
import datetime


class UserModel(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, default='', index=True, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    full_name = db.Column(db.String(255), nullable=True, default='')
    email = db.Column(db.String(255), nullable=True, default='')
    session_token = db.Column(db.String(255), nullable=True, index=True, default='')
    admin = db.Column(db.Boolean, default=False, index=True)
    active = db.Column(db.Boolean, default=True, index=True)
    ldap = db.Column(db.Boolean, default=True, index=True)
    otp_secret = db.Column(db.String(255), nullable=True, default='')
    otp_last_used = db.Column(db.String(255), nullable=True, default='')
    auth_type_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    access_token = db.Column(db.Text, nullable=True, index=True, default='')
    access_token_expiration = db.Column(db.Integer, nullable=True, index=True, default=0)
    created_at = db.Column(db.DateTime, nullable=True)

    def get_id(self):
        return str(self.session_token)

    def has_2fa(self):
        return False if self.otp_secret is None else len(self.otp_secret) > 0

    def get_auth_name(self):
        auth_type = AuthTypeModel.query.filter(AuthTypeModel.id == self.auth_type_id).first()
        if auth_type:
            return auth_type.name.lower()
        return ''


class AuthTypeModel(db.Model):
    __tablename__ = 'auth_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True, default='', index=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)


@login.user_loader
def load_user(session_token):
    user = UserModel.query.filter_by(session_token=session_token).first()

    if user.get_auth_name() == 'azure':
        if datetime.datetime.utcnow().timestamp() > user.access_token_expiration or len(user.access_token) == 0:
            return None
    return user
