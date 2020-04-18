from app import db


class DNSZoneModel(db.Model):
    __tablename__ = 'dns_zones'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=True, default='', index=True)
    ttl = db.Column(db.Integer, nullable=True, default=0)
    rclass = db.Column(db.String(32), nullable=True, default='', index=True)
    type = db.Column(db.String(32), nullable=True, default='', index=True)
    address = db.Column(db.String(255), nullable=True, default='', index=True)
    active = db.Column(db.Boolean, default=True, index=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
