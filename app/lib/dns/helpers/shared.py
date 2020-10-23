import os
import csv
from app.lib.base.environment import EnvironmentManager


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

    def get_user_data_path(self, user_id, folder=None, filename=None):
        path = os.path.join(EnvironmentManager().get_data_path(), 'users', str(user_id))
        if folder is not None:
            path = os.path.join(path, folder)

        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            if not os.path.isdir(path):
                return False

        if filename is not None:
            filename = filename.replace('..', '').replace('/', '')
            path = os.path.join(path, filename)

        return os.path.realpath(path)

    def _load_csv(self, csvfile):
        with open(csvfile, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)

        if len(data) == 0:
            return []

        # Remove the first row and map each header to an index position.
        first_row = data.pop(0)
        header = {}
        for i, name in enumerate(first_row):
            header[name.strip().lower()] = i

        rows = []
        for item in data:
            row = {}
            for name, position in header.items():
                # Using the index position we extracted before, get the appropriate column for this header.
                row[name] = item[position] if position < len(item) else ''
            rows.append(row)

        return rows
