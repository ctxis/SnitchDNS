from app import db


class NotificationTypeModel(db.Model):
    __tablename__ = 'notification_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True, default='')
    description = db.Column(db.String(255), nullable=True, default='')

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)


class NotificationSubscriptionModel(db.Model):
    __tablename__ = 'notification_subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    type_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    enabled = db.Column(db.Boolean, default=True, index=True)
    data = db.Column(db.Text, nullable=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)


class NotificationLogModel(db.Model):
    __tablename__ = 'notification_logs'
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    sent_at = db.Column(db.DateTime, nullable=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
