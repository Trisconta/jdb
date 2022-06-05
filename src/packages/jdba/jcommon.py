# jcommon.py  (c)2022  Henrique Moreira

""" Common JSON manipulation
"""

# pylint: disable=missing-function-docstring

import json
from jdba.jindex import JIndex

J_ENSURE_ASCII = True

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


class GenericData():
    """ Abstract class for data manipulation
    """
    def __init__(self, name=""):
        assert isinstance(name, str)
        self.name = name

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

class AData(GenericData):
    """ Generic manipulation of data, to/ from JSON format.
    """
    def __init__(self, data=None, name=""):
        super().__init__(name)
        self._data = [] if data is None else data
        self._indent = 2
        self._do_sort = True
        self.index = JIndex()

    def raw(self):
        return self._data

    def content(self) -> list:
        assert isinstance(self._data, list), self.name
        return self._data

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
        byidx, byname = {}, {}
        self.index.byname["idx"] = byidx
        self.index.byname["case"] = byname
        for idx, key in enumerate(data):
            if key == "~":
                return True
            byidx[idx] = key
            assert (idx == 0 and key.startswith("!")) or idx, key
            prefix = key.split("=", maxsplit=1)[0]
            name = prefix if idx > 0 else "!"
            byname[name] = key
        return False

    def string(self) -> str:
        return self.dump_json(self._data)

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
    def __init__(self, data=None, name=""):
        if data is None:
            elems = {}
        else:
            elems = data
        assert isinstance(elems, dict)
        super().__init__(elems, name)

    def content(self) -> list:
        if isinstance(self._data, list):
            return self._data
        return [self._data]

def read_json(fdin):
    """ Read JSON from stream """
    data = json.load(fdin)
    return data
