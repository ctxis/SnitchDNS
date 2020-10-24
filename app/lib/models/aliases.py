from app import db


class AliasModel(db.Model):
    __tablename__ = 'aliases'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    ip = db.Column(db.String(255), nullable=True, default='', unique=True)
    name = db.Column(db.String(255), nullable=True, default='', unique=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
