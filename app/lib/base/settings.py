from app.lib.models.config import ConfigModel
from app import db


class SettingsManager:
    def save(self, name, value, list_separator=','):
        setting = ConfigModel.query.filter(ConfigModel.name == name).first()
        if setting is None:
            setting = ConfigModel(name=name)
            db.session.add(setting)

        # Ensure the value that will be saved is of the right type.
        setting.value = self.__process_input_value(value, list_separator)
        db.session.commit()
        return True

    def get(self, name, default, type=None, list_separator=','):
        setting = ConfigModel.query.filter(ConfigModel.name == name).first()
        if setting is None:
            return default
        return self.__process_return_value(setting.value, type, list_separator)

    def __process_return_value(self, value, type, list_separator):
        if (type is list) or (isinstance(type, str) and type == 'list'):
            values = []
            items = value.strip().split(list_separator)
            for item in items:
                item = item.strip()
                if len(item) > 0:
                    values.append(item)
            return values
        elif isinstance(type, str) and value.lower() in ['true', 'false']:
            # This is a generic fix for boolean values across DBMSs.
            return value.lower() == 'true'
        elif (type is bool) or (isinstance(type, str) and type == 'bool'):
            # If it's all digits, convert to int and cast to bool.
            if value.isdigit():
                return bool(int(value))
            elif value.lower() in ['true', 'false', 'yes', 'no']:
                return (value.lower() == 'true') or (value.lower() == 'yes')
            else:
                # I've no idea what to do, probably it's the wrong type.
                raise Exception("Config value type error. Value {0} is not a valid bool.".format(value))
        elif (type is int) or (isinstance(type, int) and type == 'int'):
            if value.isdigit():
                return int(value)
            else:
                # Probably an invalid value, return as is.
                raise Exception("Config value type error. Value {0} is not a valid int.".format(value))

        return value

    def __process_input_value(self, value, list_separator):
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        elif isinstance(value, list):
            value = list_separator.join(value)
        return str(value)
