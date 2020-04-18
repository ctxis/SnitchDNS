from app.lib.models.config import ConfigModel
from app import db


class SettingsManager:
    def save(self, name, value):
        setting = ConfigModel.query.filter(ConfigModel.name == name).first()
        if setting is None:
            setting = ConfigModel(name=name, value=value)
            db.session.add(setting)
        else:
            setting.value = value

        db.session.commit()

        return True

    def get(self, name, default=None):
        setting = ConfigModel.query.filter(ConfigModel.name == name).first()
        if setting is None:
            return default
        return setting.value

    def get_list(self, name, sep=","):
        items = self.get(name, '').strip().split(sep)
        values = []
        for item in items:
            item = item.strip()
            if len(item) > 0:
                values.append(item)

        return values

    def save_list(self, name, values, sep=","):
        return self.save(name, sep.join(values))
