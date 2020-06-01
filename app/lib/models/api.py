from app import db


class ApiKeyModel(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    name = db.Column(db.String, default='', nullable=True)
    apikey = db.Column(db.String, nullable=True, index=True, default='')
    enabled = db.Column(db.Boolean, default=True, index=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
