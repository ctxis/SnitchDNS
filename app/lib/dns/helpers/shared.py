import os


class SharedHelper:
    def _prepare_path(self, save_as, overwrite, create_path):
        if save_as != os.path.realpath(save_as):
            raise Exception("Coding error: Passed path must be absolute.")

        # Check if the path exists.
        path = os.path.dirname(save_as)
        if not os.path.isdir(path):
            if not create_path:
                return False
            os.makedirs(path, exist_ok=True)
            if not os.path.isdir(path):
                # If it still doesn't exist.
                return False

        # Check if the file exists.
        if os.path.isfile(save_as):
            if not overwrite:
                return False

            os.remove(save_as)
            if os.path.isfile(save_as):
                # If the file still exists.
                return False

        return True

    def _sanitise_csv_value(self, value):
        if len(value) > 0:
            if value[0] in ['=', '+', '-', '@']:
                value = "'" + value
        return value
