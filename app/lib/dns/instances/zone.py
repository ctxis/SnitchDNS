import datetime
from app import db


class DNSZone:
    def __init__(self, item):
        self.item = item

    def save(self):
        self.item.updated_at = datetime.datetime.now()
        if not self.id:
            self.item.created_at = datetime.datetime.now()
            db.session.add(self.item)
        db.session.commit()
        db.session.refresh(self.item)

    @property
    def id(self):
        return self.item.id

    @property
    def domain(self):
        return self.item.domain

    @domain.setter
    def domain(self, value):
        self.item.domain = value

    @property
    def ttl(self):
        return self.item.ttl

    @ttl.setter
    def ttl(self, value):
        self.item.ttl = value

    @property
    def rclass(self):
        return self.item.rclass

    @rclass.setter
    def rclass(self, value):
        self.item.rclass = value

    @property
    def type(self):
        return self.item.type

    @type.setter
    def type(self, value):
        self.item.type = value

    @property
    def address(self):
        return self.item.address

    @address.setter
    def address(self, value):
        self.item.address = value

    @property
    def created_at(self):
        # This is a required property for consistency.
        return self.item.created_at

    @property
    def updated_at(self):
        # This is a required property for consistency.
        return self.item.updated_at
