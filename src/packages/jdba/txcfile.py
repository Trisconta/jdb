# txcfile.py  (c)2022  Henrique Moreira

""" TxcFile - a simple text file sequence
See also: tinycode/waxpage/txc.py
"""

# pylint: disable=missing-function-docstring

import jdba.jbox as jbox

class TxcFile(jbox.IOJData):
    """ Input/ output operations for TXC (TeXt with Context) files
    """
    def __init__(self, fname="", name=""):
        super().__init__(name, encoding="ISO-8859-1")
        self._path = fname
        self._astring = ""
        self._header = ""
        self._data = []
        self._num_lines_sep = 1
        self._in_encode = ""

    def contents(self) -> str:
        """ Return string-based contents. """
        return self._astring

    def structure(self) -> list:
        return self._data

    def header(self) -> str:
        """ Returns the header, if any. """
        return self._header

    def load(self, path:str) -> bool:
        self._path = path
        try:
            with open(path, "r", encoding=self._encoding) as fdin:
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
        """ Parse TXC formatting. """
        errs = 0
        hdr, idx = "", 0
        spl = self._astring.splitlines()
        if not spl:
            return False
        if spl[0].startswith("#"):
            hdr = spl[0] + "\n"
            idx = 1
            if spl[idx].startswith("#"):
                hdr += spl[idx] + "\n"
                idx += 1
        last_empty = -1
        res, last = [], []
        for num, line in enumerate(spl[idx:], idx+1):
            #print(num, f"(idx={idx})\t{line}", end="!\n")
            astr = line.lstrip()
            if astr:
                last.append(astr)
            else:
                if last:
                    res.append(last)
                last = []
                if last_empty+1 == num:
                    errs += 1
                    hint = info_from_content(res)
                    if hint:
                        hint = f" (last was: '{hint}')"
                    if err is not None:
                        err.write(f"Useless empty line at: {num}{hint}\n")
                last_empty = num
        if last:
            res.append(last)
        self._header = hdr
        enc = get_coding_str(hdr)
        self._in_encoding = "" if enc.startswith(":") else enc
        self._data = res
        return errs == 0

    def from_parse(self) -> bool:
        """ Sets _astring according structured contents. """
        if not isinstance(self._data, list):
            return False
        astr = "\n" if self._header else ""
        for item in self._data:
            new = '\n'.join(item)
            astr += new + "\n"
            astr += '\n' * self._num_lines_sep
        self._astring = self._header + astr
        return True

def get_coding_str(astr:str) -> str:
    """ Returns ':msg' upon error, or the corresponding interpreted coding:
		e.g. '#-*- coding: iso-8859-1 -*-'
    """
    spl = astr.split("coding:", maxsplit=1)
    if len(spl) < 2:
        return ":Invalid"
    last = spl[-1].strip().split(" ", maxsplit=1)[0].strip()
    return last

def info_from_content(blocks, max_line=40) -> str:
    if not blocks:
        return ""
    last = blocks[-1]
    if isinstance(last, list):
        return info_from_content(last, max_line) if last else ""
    if max_line <= 0:
        return last
    if len(last) > max_line:
        return last[:max_line] + "..."
    return last

# Main script
if __name__ == "__main__":
    print("Please import me!")
