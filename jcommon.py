# jcommon.py  (c)2022  Henrique Moreira

""" Common JSON manipulation
"""

# pylint: disable=missing-function-docstring

import json

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

    def content(self) -> list:
        assert isinstance(self._data, list), self.name
        return self._data

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
