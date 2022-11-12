# csvfile.py  (c)2022  Henrique Moreira

""" a simple class to handle CSV files
"""

# pylint: disable=missing-function-docstring

import jdba.jbox

class CsvFile(jdba.jbox.IOJData):
    """ Input/ output operations for CSV files
    """
    _split_str = ","

    def __init__(self, fname="", name="", encoding=None):
        enc = "ISO-8859-1" if encoding is None else encoding
        super().__init__(name, encoding=enc)
        self._path = fname
        self._astring = ""
        self._header = ""
        self._data = []
        self._num_lines_sep = 0
        self._in_encoding = ""
        self._maxsplit = -1

    def contents(self) -> str:
        """ Return string-based contents. """
        return self._astring

    def structure(self) -> list:
        return self._data

    def header(self) -> str:
        """ Returns the header, if any. """
        return self._header

    def load(self, path:str="") -> bool:
        if path:
            self._path = path
        fname = self._path
        try:
            with open(fname, "r", encoding=self._encoding) as fdin:
                astr = fdin.read()
        except FileNotFoundError:
            return False
        self._astring = astr
        return True

    def save(self, path:str) -> bool:
        """ Save content to a file, at 'path'. """
        astr = self._astring
        new = astr if astr.endswith("\n") else astr + "\n"
        try:
            self._write_content(path, new)
        except FileNotFoundError:
            return False
        return True

    def parse(self, err=None) -> bool:
        """ Parse CSV formatting. """
        assert err is None
        errs = 0
        hdr, idx = "", 0
        spl = self._astring.splitlines()
        self._data = []
        if not spl:
            return False
        if spl[0].startswith("#"):
            hdr = spl[0] + "\n"
            idx = 1
        res = []
        for line in spl[idx:]:
            astr = line.rstrip()
            res.append(self._from_str_split(astr))
        self._header = hdr
        self._in_encoding = self._encoding
        assert self._encoding, self.name
        self._data = res
        return errs == 0

    def set_split(self, astr=",", maxsplit=-1):
        CsvFile._split_str = astr
        self._maxsplit = maxsplit

    def set_tab_split(self):
        self.set_split("\t")

    def _from_str_split(self, astr):
        c_split = CsvFile._split_str
        if c_split:
            if self._maxsplit <= 0:
                elem = astr.split(c_split)
            else:
                elem = astr.split(c_split, maxsplit=self._maxsplit)
        else:
            elem = astr
        return elem


# Main script
if __name__ == "__main__":
    print("Please import me!")
