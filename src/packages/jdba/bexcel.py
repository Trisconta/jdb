# bexcel.py  (c)2022  Henrique Moreira

""" Basic Excel, relying on openpyxl *abstraction*
"""

# pylint: disable=missing-function-docstring

import jdba.jcommon

class Sheet(jdba.jcommon.GenericData):
    """ Excel Sheet general parsing
    """
    def __init__(self, obj, name="", encoding=None):
        myname = name if name else "sheet"
        super().__init__(myname, encoding)
        self._myself = obj
        self.inlist = []

    def raw(self):
        return self._myself

    def parse(self) -> bool:
        """ Eases iteration from an Excel sheet """
        sht = self._myself
        there = [[self._get_pyxl(cell) for cell in row] for row in sht]
        self.inlist = there
        return True

    def _get_pyxl(self, cell):
        tup = WCell(cell, encoding=self._encoding)
        return tup

class WCell(jdba.jcommon.GenericData):
    """ Generic openpyxl cell """
    def __init__(self, cell, encoding=None):
        super().__init__(cell.coordinate, encoding)
        self.tup = (cell.value, cell.data_type, cell.coordinate, cell)
        self._mystr = None

    def string(self) -> str:
        return self._cached()

    def _cached(self) -> str:
        if self._mystr is None:
            a_val = self.tup[0]
        else:
            a_val = self._mystr
        astr = f"{a_val}"
        return astr

    def __str__(self) -> str:
        return self.string()

    def __repr__(self) -> str:
        astr = self.string()
        return f"'{astr}'"

class Workbook(jdba.jcommon.GenericData):
    """ Workbook """
    def __init__(self, obj, name="", encoding=None):
        myname = name if name else "wbk"
        super().__init__(myname, encoding)
        self._myself = obj
        try:
            sheet_names = obj.sheetnames
        except AttributeError:
            sheet_names = []
        assert isinstance(sheet_names, list)
        self._sheet_names = sheet_names
        self.inlist = self._get_sheets(sheet_names)

    def raw(self):
        return self._myself

    def first(self):
        assert self.inlist, self.name
        return self.inlist[0]

    def parse(self) -> list:
        """ Calls parse() of each Sheet """
        res = [(sht.parse(), sht.name) for sht in self.inlist]
        print("parse():", self.name, res)
        return res

    def get_sheet_names(self) -> list:
        return self._sheet_names

    def _get_sheets(self, sheet_names:list) -> list:
        obj = self._myself
        enc = self._encoding
        res = [Sheet(obj[sname], obj[sname].title, enc) for sname in sheet_names]
        return res

# Main script
if __name__ == "__main__":
    print("Please import me!")
