import os
import csv
import ipaddress
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

    def _load_csv_header(self, csvfile):
        with open(csvfile, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)

        return header

    def is_valid_ip_or_range(self, ip_range):
        if '/' in ip_range:
            ip, bits = ip_range.split('/')
            if not self.__is_valid_ip_address(ip):
                return False
            elif not bits.isdigit():
                return False
            bits = int(bits)
            if bits < 8 or bits > 30:
                return False
            return True
        else:
            return self.__is_valid_ip_address(ip_range)

    def __is_valid_ip_address(self, ip):
        try:
            obj = ipaddress.ip_address(ip)
        except ValueError:
            return False

        return True

    def ip_in_range(self, ip, ip_range):
        if ip_range == '0.0.0.0':
            return True
        elif '/' in ip_range:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(ip_range)
        else:
            return str(ip) == str(ip_range)
