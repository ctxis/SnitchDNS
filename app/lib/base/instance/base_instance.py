import datetime
from app import db
from app.lib.base.settings import SettingsManager


class BaseInstance:
    def __init__(self, item):
        self.item = item
        self._uses_cache = False

    def save(self):
        self.item.updated_at = datetime.datetime.now()
        if not self.id:
            self.item.created_at = datetime.datetime.now()
            db.session.add(self.item)
        self.commit()
        db.session.refresh(self.item)

        if self._uses_cache:
            SettingsManager().save('dns_clear_cache', True)

    def delete(self):
        db.session.delete(self.item)
        self.commit()

    def commit(self):
        db.session.commit()

    @property
    def id(self):
        return self.item.id

    @property
    def created_at(self):
        # This is a required property for consistency.
        return self.item.created_at

    @property
    def updated_at(self):
        # This is a required property for consistency.
        return self.item.updated_at
