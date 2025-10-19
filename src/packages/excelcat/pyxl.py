# pyxl.py  (c)2025  Henrique Moreira

""" pyxl.py - Simple Excel operations using openpyxl
"""

# pylint: disable=missing-function-docstring

from json import dumps
import openpyxl
from openpyxl.cell.cell import Cell


VALID_CODINGS = (
    "ascii", "utf-8", "ISO-8859-1",
)


def tester(infile):
    mbk = MyBook()
    isok = mbk.load(infile)
    assert isok, infile
    sht = mbk.sheet()
    wbk = openpyxl.Workbook(); new_sheet = wbk.active
    new = copycat(sht, new_sheet)
    wbk.save("/tmp/new.xlsx")


class GenData:
    """ Abstract class for Generic Data
    """
    def __init__(self, data, name, encoding=None):
        self._data, self._encoding = data, "ascii"
        self._enc_type = self.set_encoding(encoding)

    def raw(self):
        return self._data

    def set_encoding(self, encoding) -> int:
        """ Checks whether string encoding is valid. """
        if encoding is None:
            return "ascii"
        try:
            idx = VALID_CODINGS.index(encoding)
        except ValueError:
            idx = -1
        return idx

    def __str__(self) -> str:
        return self.to_string()

    def _dump_json_string(self, ensure_ascii=True):
        """ Dump JSON from data
        """
        cont = self._data	# Content!
        ind, asort, ensure = 2, True, ensure_ascii
        astr = dumps(cont, indent=ind, sort_keys=asort, ensure_ascii=ensure)
        return astr


class MyBook(GenData):
    """ Excel book manipulation.
    """
    def __init__(self, data=None, name="B", encoding=None):
        super().__init__(
            {} if data is None else data, name, encoding,
        )
        self._read_only = False
        self._book = None

    def book(self):
        assert self._book is not None, "book?"
        return self._book

    def sheet(self, which=0):
        """ Returns the sheet by 1..n index; if 0 chosen, returns the first one.
        """
        idx = which - 1 if which > 0 else 0
        name = self._book.sheetnames[idx]
        return self._book[name]

    def to_string(self) -> str:
        return self._dump_json_string()

    def load(self, path:str) -> bool:
        self._data = {}
        try:
            wb1 = openpyxl.open(path, read_only=self._read_only, data_only=True)
        except FileNotFoundError:
            return False
        self._book = wb1
        return True


def copycat(sheet_source, sheet_new=None):
    """ Copy a sheet into a new Workbook() sheet. """
    sheet_new.title = sheet_source.title
    # Copy content and formatting
    for row in sheet_source.iter_rows():
        for cell in row:
            if not isinstance(cell, Cell):
                continue
            new_cell = sheet_new.cell(row=cell.row, column=cell.column, value=cell.value)
            if cell.has_style:
                new_cell.font = cell.font.copy()
                new_cell.border = cell.border.copy()
                new_cell.fill = cell.fill.copy()
                new_cell.number_format = cell.number_format
                new_cell.protection = cell.protection.copy()
                new_cell.alignment = cell.alignment.copy()
    # Copy column widths
    last = 22	# any reasonable width
    for col_letter, col_dim in sheet_source.column_dimensions.items():
        if col_dim.width is None:
            largo = last
        else:
            largo = col_dim.width
        print(f"::: width {col_letter}: {col_dim.width} (largo={largo})")
        sheet_new.column_dimensions[col_letter].width = largo
        last = largo
    # Copy row heights
    for row_idx, row_dim in sheet_source.row_dimensions.items():
        sheet_new.row_dimensions[row_idx].height = row_dim.height
    return sheet_new



# Main script
if __name__ == "__main__":
    print("Please import me!")
    tester("test-input.xlsx")
