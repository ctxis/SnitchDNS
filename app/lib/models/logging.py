from app import db


class LoggingErrors(db.Model):
    __tablename__ = 'logging_errors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    description = db.Column(db.Text, nullable=True)
    details = db.Column(db.Text, nullable=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
