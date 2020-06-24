import os


class EnvironmentManager:
    def get_data_path(self):
        default_data_path = os.path.realpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..', 'data'))
        path = self.env('SNITCHDNS_DATA_PATH', default='').strip()
        return path if len(path) > 0 else default_data_path

    def env(self, name, default=None, must_exist=False):
        if not name in os.environ:
            if must_exist:
                raise Exception("Environment variable not found: {0}".format(name))
            return default
        return os.environ[name]
