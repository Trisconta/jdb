# jcommon.py  (c)2022  Henrique Moreira

""" Common JSON manipulation
"""

# pylint: disable=missing-function-docstring

import json
import unidecode
from jdba.jindex import JIndex

J_ENSURE_ASCII = True

DEF_ENCODING = "utf-8"

SAMPLE_DLIST = {
    '!null.json': [
        {
            'Id': 0,
            'Key': None,
            'Mark': None,
            'Title': 'null',
        }
    ],
    'sample=$1': [
        {
            'Id': 1001,
            'Key': 'url',
            'Mark': '2022-06-04',
            'Title': 'sample 1',
        },
        {
            'Id': 0,
            'Key': '',
            'Mark': None,
            'Title': ''},
    ],
    '~': [
        {
            'Id': -1,
            'Key': '*',
            'Mark': None,
            'Title': '',
        }
    ],
}


class SingletonIO():
    """ Singleton to handle default encodings.
    """
    _instance = None
    default_encoding = DEF_ENCODING
    max_overview = {
        "str":  60,
        "depth": 3,
    }

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def get_encoding():
        astr = SingletonIO.default_encoding
        assert astr
        assert isinstance(astr, str)
        return astr


class GenericData():
    """ Abstract class for data manipulation
    """
    def __init__(self, name="", encoding=None):
        assert isinstance(name, str)
        self.name = name
        self.set_encoding(encoding)

    def get_encoding(self) -> str:
        """ Returns the used encoding name string.
        """
        astr = self._encoding
        hint = self.name if self.name else "?"
        assert astr, f"No encoding: {hint}"
        if astr in ("latin-1",):
            return "ISO-8859-1"
        return astr

    def set_encoding(self, encoding) -> bool:
        if encoding is None:
            encoding = SingletonIO().default_encoding
        if encoding in ("latin-1",):
            encoding = "ISO-8859-1"
        if encoding is None:
            encoding = "ascii"
        assert encoding, self.name
        assert isinstance(encoding, str)
        self._encoding = encoding
        return True

    @staticmethod
    def default_dlist():
        is_ok, dlist = GenericData.empty_dlist_data(SAMPLE_DLIST)
        assert is_ok
        return dlist

    @staticmethod
    def empty_dlist_data(adict) -> tuple:
        assert isinstance(adict, dict)
        for key, elem in adict.items():
            assert key
            if not isinstance(elem, list):
                return False, {}
            for tag in elem:
                if not isinstance(tag, dict):
                    return False, {}
                for this, item in tag.items():
                    if not item:
                        continue
                    if isinstance(item, str):
                        tag[this] = ""
        return True, adict

    def to_alist(self, adict) -> list:
        if isinstance(adict, list):
            return adict
        if isinstance(adict, tuple):
            return list(adict)
        res = []
        for key in sorted(adict):
            elem = [key, [adict[key]]]
            res.append(elem)
        return res

class DataSchema(GenericData):
    """ Basic data-schema JSON abstract class
    """
    def __init__(self, data, name="", encoding=None):
        self._ptr = data
        super().__init__(name, encoding)

    def to_string(self) -> str:
        if self._ptr is None:
            return ""
        return self._json_dump()

    def __str__(self) -> str:
        return self.to_string()

    def _json_dump(self):
        ind, asort, ensure = 2, True, True
        astr = json.dumps(self._ptr, indent=ind, sort_keys=asort, ensure_ascii=ensure)
        return astr

class AData(GenericData):
    """ Generic manipulation of data, to/ from JSON format.
    """
    def __init__(self, data=None, name="", encoding=None):
        super().__init__(name, encoding)
        self._data = [] if data is None else data
        self._indent = 2
        self._strict = False
        self._do_sort = True
        self.index = JIndex()

    def raw(self):
        return self._data

    def content(self) -> list:
        assert isinstance(self._data, list), self.name
        return self._data

    def get_cases(self) -> list:
        """ Returns the content keys, excluding those starting by '!' or '~'
        """
        excl = ("!", "~")
        res = [name for name in self._data if not name.startswith(excl)]
        return res

    def get_case(self, name:str):
        """ Returns the table, or dictionary, from the 'case' name.
        """
        _, _, res = self.get_case_root(name)
        return res

    def get_case_root(self, name:str) -> tuple:
        """ Returns the key, case root, and the case itself.
        """
        assert isinstance(name, str)
        idxes = self.index
        if idxes.initialized():
            is_ok = True
        else:
            is_ok = self.do_index()
        assert is_ok, f"get_case(): {name}"
        key = idxes.byname["case"][name]
        res = self._data.get(key)
        if res is None:
            return key, [], None
        return key, self._data, res

    def do_index(self) -> bool:
        """ Generates 'byname' indexes.
        """
        data = self._data
        byidx, byname, ptrs = {}, {}, {}
        self.index.byname = {
            "idx": byidx,
            "case": byname,
            "ptr": ptrs,
        }
        for idx, key in enumerate(data):
            if key == "~":
                return True
            byidx[idx] = key
            assert (idx == 0 and key.startswith("!")) or idx, key
            prefix = key.split("=", maxsplit=1)[0]
            name = prefix if idx > 0 else "!"
            byname[name] = key
            if name in data:
                ptrs[name] = data[name]
        return not self._strict

    def __str__(self) -> str:
        return self.string()

    def string(self) -> str:
        return self.dump_json(self._data)

    def load(self, path:str) -> bool:
        with open(path, "r", encoding=self._encoding) as fdin:
            data = read_json(fdin)
        self._data = data
        self.index = JIndex()
        return True

    def to_json(self) -> str:
        return self.dump_json(self._data)

    def dump_json(self, data=None) -> str:
        ind = self._indent
        asort = self._do_sort
        ensure = J_ENSURE_ASCII
        if data is None:
            cont = GenericData.default_dlist()
        else:
            cont = data
        astr = json.dumps(cont, indent=ind, sort_keys=asort, ensure_ascii=ensure)
        return astr + "\n"

    def from_json(self, astring:str) -> bool:
        data = json.loads(astring)
        self._data = data
        return True

class DData(AData):
    """ DList data - Dictionary List items
    """
    def __init__(self, data=None, name="", encoding=None):
        if data is None:
            elems = {}
        else:
            elems = data
        assert isinstance(elems, dict)
        super().__init__(elems, name, encoding=encoding)

    def content(self) -> list:
        if isinstance(self._data, list):
            return self._data
        return [self._data]

def read_json(fdin):
    """ Read JSON from stream """
    data = json.load(fdin)
    return data

def overview(data, depth=0):
    """ Returns an object overview; interesting for tables, etc.
    """
    if depth > SingletonIO.max_overview["depth"]:
        return "(...)"
    if data is None:
        return "<null>"
    maxchrs = SingletonIO.max_overview["str"]
    if isinstance(data, (list, tuple)):
        if depth <= 0:
            res = [
                {
                    "Type": type(item),
                    "Len": len(item),
                    "Cont": overview(item, depth+1),
                } for item in data
            ]
        else:
            res = [
                f"list-len={len(data)}"
            ] + [
                overview(item, depth+1) for item in data
            ]
        return res
    if isinstance(data, dict):
        res = sorted(data)
        return res
    if isinstance(data, str):
        if len(data) > maxchrs:
            return data[:maxchrs] + "..."
        return data
    res = f"(type={type(data)})"
    return res

def to_ascii(astr):
    ustr = unidecode.unidecode(astr)
    return ustr
