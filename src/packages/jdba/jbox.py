# jbox.py  (c)2022  Henrique Moreira

""" JBox - a box of cases

Each box is a json file;
each 'case' designates one list of dictionaries.
"""

# pylint: disable=missing-function-docstring

import os
import json
from copy import deepcopy
import jdba.jcommon as jcommon

BASIC_DICT_TAIL = {
    "Id": 0,
    "Name": None,
}


class IOJData(jcommon.GenericData):
    """ Input/ output operations for JSON data.
    """
    def _write_content(self, path:str, astr:str) -> bool:
        """ Write content, Linux text (no CR-LF, but only LF)
        """
        if os.name == "nt":
            with open(path, "wb") as fdout:
                fdout.write(astr.encode(self._encoding))
            return True
        with open(path, "w", encoding=self._encoding) as fdout:
            fdout.write(astr)
        return True

    def _write_stream(self, fdout, astr:str) -> bool:
        fdout.write(astr)
        return True

class JBox(IOJData):
    """ Generic manipulation of data, to/ from JSON format.
    """
    def __init__(self, data=None, name="", encoding=None):
        super().__init__(name)
        self.set_encoding(encoding)
        if data is None:
            self._data = {}
        else:
            self._data = data._data if isinstance(data, JBox) else data
        enc = jcommon.J_ENSURE_ASCII if encoding is None else encoding
        self._ensure_ascii = enc
        self.dlist = None
        self.new_idx = {}

    def to_string(self) -> str:
        return self._dump_json_string()

    def raw(self):
        return self._data

    def add_to(self, acase:str, new:dict) -> bool:
        data = self._data.get(acase)
        if data is None:
            return False
        is_ok, _, new_idx = self._inject_new(acase, data, new, "APP")
        self.new_idx[acase] = new_idx
        return is_ok

    def _inject_new(self, acase, data, new, s_append) -> tuple:
        assert acase, self.name
        assert s_append and isinstance(s_append, str), acase
        alen = len(data)
        if alen <= 0:
            # Should have at least one element
            return False, BASIC_DICT_TAIL, -1
        last_id = 900
        last = data[-1]
        an_id = last["Id"]
        assert an_id == 0, f"{acase}: bad last elem Id={an_id}"
        mine = deepcopy(last)
        del mine["Id"]
        for key, aval in new.items():
            mine[key] = aval
        if "Id" not in mine:
            mine["Id"] = last_id
        new_idx = alen - 1
        if s_append == "APP":
            data.insert(new_idx, mine)
        else:
            return False, None, -1
        return True, mine, new_idx

    def load(self, path:str) -> bool:
        self._data = {}
        try:
            with open(path, "r", encoding=self._encoding) as fdin:
                astr = fdin.read()
        except FileNotFoundError:
            return False
        data = json.loads(astr)
        self.dlist = jcommon.DData(data, path)
        self._data = data
        return True

    def flush(self) -> bool:
        self.new_idx = {}
        return True

    def save(self, path:str) -> bool:
        """ Save content to a file, at 'path'. """
        self.flush()
        astr = self._dump_json_string(self._ensure_ascii)
        astr += "\n"
        try:
            self._write_content(path, astr)
        except FileNotFoundError:
            return False
        return True

    def save_stream(self, fdout) -> bool:
        astr = self._dump_json_string(self._ensure_ascii)
        astr += "\n"
        try:
            self._write_stream(fdout, astr)
        except FileNotFoundError:
            return False
        return True

    def to_json(self) -> str:
        """ Converts existing dlist to json. """
        this = self.dlist
        if this is None:
            self.dlist = jcommon.DData(self._data, self.name)
        this = self.dlist
        return this.to_json()

    def _dump_json_string(self, ensure_ascii=True):
        """ Dump JSON from data
        """
        cont = self._data	# Content!
        ind, asort, ensure = 2, True, ensure_ascii
        astr = json.dumps(cont, indent=ind, sort_keys=asort, ensure_ascii=ensure)
        return astr

    def __str__(self) -> str:
        return self.to_string()

# Main script
if __name__ == "__main__":
    print("Please import me!")
