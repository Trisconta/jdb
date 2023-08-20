# doptions.py  (c)2022  Henrique Moreira

""" Database options
"""

# pylint: disable=missing-function-docstring

import os
from jdba.jbox import JBox

class AConfig():
    def __init__(self):
        self._os_type = int(os.name == "nt")
        self._confbox = JBox("my")
        self._path = ""

    def config(self):
        return self._confbox

    def fetch_config(self, filebase:str="") -> str:
        """ Returns the path for the configuration """
        home = self._get_home()
        sufname = filebase if filebase else self._confbox.name
        self._path = os.path.realpath(os.path.join(home, sufname))
        self._confbox.load(self._path)
        return self._path

    def _get_home(self) -> str:
        env = os.environ
        res = env.get("USERPROFILE") if self._os_type else env.get("HOME")
        if res is None:
            return os.path.sep
        return res
