import subprocess
import shlex


class ShellManager:
    def __init__(self, venv_bash_script):
        self.__venv_bash_script = venv_bash_script

    def execute(self, command, wait=True, venv=False):
        if isinstance(command, dict):
            command = self.__build_command_from_dict(command)

        if venv:
            command = [self.__venv_bash_script] + command

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
