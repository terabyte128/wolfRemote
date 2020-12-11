import json
import subprocess

class IRRemote:
    def __init__(self, config_file, tries=5):
        with open(config_file) as cf:
            self._config = json.load(cf)
            self._tries = tries

    def commands(self):
        return self._config['codes'].keys()

    def send_command(self, command):
        print("send_command", command)

        if not command in self._config['codes'].keys():
            raise ValueError("command not found in config")

        code = self._config['codes'][command]

        ctl = ['/usr/bin/ir-ctl', '--scancode', '{}:{}'.format(code['protocol'], code['code'])]

        for i in range(self._tries):    
            subprocess.check_call(ctl)

    def get_inputs(self):
        return self._config['inputs']

    def set_input(self, input_):
        if input_ not in self.get_inputs():
            raise ValueError("not in inputs")
    
        self.send_command(input_)