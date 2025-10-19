# pyxl.py  (c)2025  Henrique Moreira

""" pyxl.py - Simple Excel operations using openpyxl
"""

# pylint: disable=missing-function-docstring

import copy
from json import dumps
import openpyxl
from openpyxl.utils import get_column_letter
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
    dct = copycat(sht, new_sheet)
    for key, item in dct.items():
        print(key, item)
    wbk.save("/tmp/new.xlsx")


class GenData:
    """ Abstract class for Generic Data
    """
    def __init__(self, data, name, encoding=None):
        self.name = name
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

    def to_string(self) -> str:
        return self._dump_json_string()

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

    def load(self, path:str) -> bool:
        self._data = {}
        try:
            wb1 = openpyxl.open(path, read_only=self._read_only, data_only=True)
        except FileNotFoundError:
            return False
        self._book = wb1
        return True


def copycat(sheet_source, sheet_new=None, bare_width=25):
    """ Copy a sheet into a new Workbook() sheet. """
    sheet_new.title = sheet_source.title
    larg = {}
    dct = {
        "widths": larg,
    }
    # Copy content and formatting
    for row in sheet_source.iter_rows():
        for cell in row:
            if not isinstance(cell, Cell):
                continue
            new_cell = sheet_new.cell(row=cell.row, column=cell.column, value=cell.value)
            if cell.has_style:
                update_cell_style(new_cell, cell)
    last = bare_width	# any reasonable width, if none before was found
    # Copy column widths
    for col_idx in range(1, sheet_source.max_column + 1):
        col_letter = get_column_letter(col_idx)
        if col_letter in sheet_source.column_dimensions:
            width = sheet_source.column_dimensions[col_letter].width
            larg[col_letter] = (width, width)
        else:
            larg[col_letter] = (None, last)
        last = width
    for col_letter in sorted(larg):
        largo = larg[col_letter][1]
        sheet_new.column_dimensions[col_letter].width = largo
    # Copy row heights
    for row_idx, row_dim in sheet_source.row_dimensions.items():
        sheet_new.row_dimensions[row_idx].height = row_dim.height
    copy_page_layout(sheet_source, sheet_new)
    return dct


def copy_page_layout(source_sheet, target_sheet):
    """ Copy page setup and margins from source_sheet to target_sheet.
    Includes orientation, paper size, scaling, and margins.
    """
    # Page setup
    target_sheet.page_setup.orientation = source_sheet.page_setup.orientation
    target_sheet.page_setup.paperSize = source_sheet.page_setup.paperSize
    target_sheet.page_setup.fitToWidth = source_sheet.page_setup.fitToWidth
    target_sheet.page_setup.fitToHeight = source_sheet.page_setup.fitToHeight
    target_sheet.page_setup.scale = source_sheet.page_setup.scale
    # Page margins
    target_sheet.page_margins.left = source_sheet.page_margins.left
    target_sheet.page_margins.right = source_sheet.page_margins.right
    target_sheet.page_margins.top = source_sheet.page_margins.top
    target_sheet.page_margins.bottom = source_sheet.page_margins.bottom
    target_sheet.page_margins.header = source_sheet.page_margins.header
    target_sheet.page_margins.footer = source_sheet.page_margins.footer


def update_cell_style(new_cell, cell):
    new_cell.font = copy.copy(cell.font)
    new_cell.border = copy.copy(cell.border)
    new_cell.fill = copy.copy(cell.fill)
    new_cell.number_format = copy.copy(cell.number_format)
    new_cell.protection = copy.copy(cell.protection)
    new_cell.alignment = copy.copy(cell.alignment)
    return True


# Main script
if __name__ == "__main__":
    print("Please import me!")
    tester("test-input.xlsx")
