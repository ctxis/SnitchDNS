from app import db


class TagModel(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    name = db.Column(db.String(255), nullable=True, default='', index=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)

