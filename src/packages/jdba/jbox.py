# jbox.py  (c)2022  Henrique Moreira

""" JBox - a box of cases

Each box is a json file;
each 'case' designates one list of dictionaries.
"""

# pylint: disable=missing-function-docstring

import os
import json
import jdba.jcommon as jcommon

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

class JBox(IOJData):
    """ Generic manipulation of data, to/ from JSON format.
    """
    def __init__(self, data=None, name="", encoding=None):
        super().__init__(name)
        self.set_encoding(encoding)
        self._data = {} if data is None else data
        enc = jcommon.J_ENSURE_ASCII if encoding is None else encoding
        self._ensure_ascii = enc
        self.dlist = None

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

    def save(self, path:str) -> bool:
        """ Save content to a file, at 'path'. """
        astr = self._dump_json_string(self._ensure_ascii)
        astr += "\n"
        try:
            self._write_content(path, astr)
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

# Main script
if __name__ == "__main__":
    print("Please import me!")
