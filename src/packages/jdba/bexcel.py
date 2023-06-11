# bexcel.py  (c)2022, 2023  Henrique Moreira

""" Basic Excel, relying on openpyxl *abstraction*
"""

# pylint: disable=missing-function-docstring

import jdba.jcommon
from jdba.jbox import JBox
from jdba.jcommon import to_ascii

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

    def new_box(self, name="", method="L"):
        """ Returns a new JBox() from data """
        cont = self._linearize(self.inlist, method)
        data = {self.name: cont}
        jbx = JBox(data, self.name, encoding=self._encoding)
        jbx.dlist = jdba.jcommon.DData(data, name if name else jbx.name)
        assert jbx.dlist is not None, name
        return jbx

    def _linearize(self, alist, method:str):
        assert method
        cont = []
        stt_from = 1
        if method[0] == "L":
            if method == "L1":  # one heading-line
                scope = alist[1:]
            else:
                scope = alist
            for idx, row in enumerate(scope, stt_from):
                seq = [ala.shown() for ala in row]
                cont.append(
                    {
                        "Id": idx,
                        "Line": seq,
                    }
                )
            return cont
        for row in alist:
            line = [
                {
                    "Cell": ala.tup[2],
                    "Value": ala.shown(),
                } for ala in row
            ]
            cont.append(line)
        return cont

    def _get_pyxl(self, cell):
        tup = WCell(cell, encoding=self._encoding)
        return tup

class WCell(jdba.jcommon.GenericData):
    """ Generic openpyxl cell """
    def __init__(self, cell, encoding=None):
        """ Cell Initializer
        Note: openpyxl.cell.read_only.EmptyCell has no coordinate
        """
        try:
            coord = cell.coordinate
        except AttributeError:
            coord = "??"  # or vars(cell).get("coordinate")
        name = coord
        super().__init__(name, encoding)
        self.tup = (cell.value, cell.data_type, coord, cell)
        self.dec_places = 2
        self._mystr = None
        self._myself = cell

    def raw(self):
        return self._myself

    def shown(self, as_int="d"):
        assert isinstance(as_int, str)
        assert len(as_int) <= 1, as_int
        assert as_int in "adf", as_int
        a_val, dtype, _, _ = self.tup
        if dtype == "n":
            if as_int == "a":  # always
                return int(a_val)
            if as_int == "d":  # show decimal when applicable
                if isinstance(a_val, int):
                    return int(a_val)
            num_fmt, _ = self._num_format(a_val)
            if a_val is None:
                a_val = 0.0
            astr = ("{" + num_fmt + "}").format(a_val)
            return float(astr)
        return self._cached()

    def value(self, def_value=None):
        """ Returns value if possible """
        a_val, dtype, _, _ = self.tup
        if dtype != "n":
            return def_value
        assert isinstance(a_val, (int, float))
        return a_val

    def string(self) -> str:
        return self._cached()

    def _cached(self) -> str:
        c_value, dtype, coord, _ = self.tup
        assert dtype, coord
        if self._mystr is None:
            astr = self._formatted_str(dtype, c_value)
        else:
            astr = self._mystr
        return astr

    def _formatted_str(self, dtype, c_value) -> str:
        obj = self._myself
        if dtype == "f":  # formula
            return str(c_value)
        if dtype == "s":  # string
            return jdba.jcommon.to_ascii(c_value)
        attrs = [v for v in dir(obj) if v[0] != "_" and not callable(getattr(obj,v))]
        style = obj.style if "style" in attrs else "Normal"
        fmt = obj.number_format if "number_format" in attrs else "General"
        astr = str(c_value)
        if dtype in "n":
            if style == "Normal":
                if fmt != "General":
                    astr = f"{c_value:f}"
        # ToDo, use self._myself.number_format
        #astr = f"{coord}:{dtype}={astr}"
        return astr

    def __str__(self) -> str:
        return self.string()

    def __repr__(self) -> str:
        c_value, dtype, _, _ = self.tup
        if dtype in "n":
            if c_value is None:
                return ""
            fmt_dec, suf = self._num_format(c_value)
            fmt_str = "{" + fmt_dec + "}" + suf
            return fmt_str.format(c_value)
        if dtype in "f":
            # Formula!
            return f'"{c_value}"'
        astr = self.string()
        return f"'{astr}'"

    def _num_format(self, c_value) -> tuple:
        if self.dec_places is None:
            return "0", ""
        if isinstance(c_value, int):
            return "0", ""
        return f"0:0.{self.dec_places}f", ""

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
        self._sht_idx = {}

    def raw(self):
        return self._myself

    def sheet_by_name(self, name:str):
        """ Returns the sheet index by name """
        return self._sht_idx["byname"][name]

    def sheet_by_index(self, idx:int):
        """ Returns the sheet name by index """
        assert idx >= 1, self.name
        return self._sht_idx["bynum"][name]

    def first(self):
        assert self.inlist, self.name
        return self.inlist[0]

    def parse(self) -> list:
        """ Calls parse() of each Sheet """
        res = [(sht.parse(), sht.name) for sht in self.inlist]
        #print("parse():", self.name, res)
        self._sht_idx = {
            "byname": {},
            "bynum": {},
        }
        for idx, sheet in enumerate(self.inlist, 1):
            self._sht_idx["byname"][sheet.name] = idx
            self._sht_idx["byname"][to_ascii(sheet.name)] = idx
            self._sht_idx["bynum"][idx] = to_ascii(sheet.name)
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
