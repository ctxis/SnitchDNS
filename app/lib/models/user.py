from app import db, login
from flask_login import UserMixin


class UserModel(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, default='', index=True, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    full_name = db.Column(db.String(255), nullable=True, default='')
    email = db.Column(db.String(255), nullable=True, default='')
    session_token = db.Column(db.String(255), nullable=True, index=True, default='')
    admin = db.Column(db.Boolean, default=False, index=True)
    active = db.Column(db.Boolean, default=True, index=True)
    ldap = db.Column(db.Boolean, default=True, index=True)

    def get_id(self):
        return str(self.session_token)


@login.user_loader
def load_user(session_token):
    return UserModel.query.filter_by(session_token=session_token).first()
