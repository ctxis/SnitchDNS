import subprocess
import shlex


class ShellManager:
    def execute(self, command, wait=True):
        if isinstance(command, dict):
            command = self.__build_command_from_dict(command)

        return self.__execute(command, wait)

    def __execute(self, command, wait):
        if wait:
            return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode().strip()

        return subprocess.Popen(command)

    def __build_command_from_dict(self, command):
        sanitised = []
        for key, value in command.items():
            item = shlex.quote(key)
            if isinstance(value, str) and len(value) > 0:
                item = item + ' ' + shlex.quote(value)
            else:
                item = item + ' ' + str(value)

            sanitised.append(item.strip())

        return sanitised
