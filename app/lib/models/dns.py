from app import db


class DNSZoneModel(db.Model):
    __tablename__ = 'dns_zones'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    domain = db.Column(db.String(255), nullable=True, default='', index=True)
    base_domain = db.Column(db.String(255), nullable=True, default='', index=True)
    full_domain = db.Column(db.String(255), nullable=True, default='', index=True)
    active = db.Column(db.Boolean, default=True, index=True)
    exact_match = db.Column(db.Boolean, default=True, index=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)


class DNSRecordModel(db.Model):
    __tablename__ = 'dns_records'
    id = db.Column(db.Integer, primary_key=True)
    dns_zone_id = db.Column(db.Integer, nullable=True, index=True, default=0)
    ttl = db.Column(db.Integer, nullable=True, default=0)
    rclass = db.Column(db.String(32), nullable=True, default='', index=True)
    type = db.Column(db.String(32), nullable=True, default='', index=True)
    data = db.Column(db.String(255), nullable=True, default='', index=True)
    active = db.Column(db.Boolean, default=True, index=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)


class DNSQueryLogModel(db.Model):
    __tablename__ = 'dns_query_log'
    id = db.Column(db.Integer, primary_key=True)
    source_ip = db.Column(db.String(128), nullable=True, default='', index=True)
    domain = db.Column(db.String(255), nullable=True, default='', index=True)
    rclass = db.Column(db.String(32), nullable=True, default='')
    type = db.Column(db.String(32), nullable=True, default='')
    resolved_to = db.Column(db.String(128), nullable=True, default='', index=True)
    found = db.Column(db.Boolean, default=False, index=True)
    forwarded = db.Column(db.Boolean, default=False, index=True)
    dns_zone_id = db.Column(db.Integer, nullable=True, default=0, index=True)
    dns_record_id = db.Column(db.Integer, nullable=True, default=0, index=True)

    # Required in all models.
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
