# jindex.py  (c)2022  Henrique Moreira

""" AData/ DData indexing
"""

# pylint: disable=missing-function-docstring

COMMON_FIELDS = (
    "idx",	# 0: '!xxx', 1: Case1, 2: Case2, ...
    "case",	# '!': '!xxx', 'Case1': 'Case1', ...
    "ptr",	# byname["ptr"]["Case1"] = [data]
    "hash",	# byname["hash"]["Case1"] = ...(**)...
)

class GeneralIndex():
    """ Abstract class for indexing
    """
    def __init__(self, name=""):
        assert isinstance(name, str)
        self.name = name
        self.byname = {}
        self._hash = {}

    def get_ptr(self, name:str):
        return self.byname["ptr"][name]

class JIndex(GeneralIndex):
    """ J-son based indexing
    """
    do_jstrip = True

    def __init__(self, name=""):
        super().__init__(name)
        self._seqid = {}

    def get_sequence_ids(self) -> dict:
        return self._seqid

    def initialized(self) -> bool:
        return len(self.byname) > 0

    def id_hash(self) -> dict:
        return self._hash

    def id_to_idx(self, acase:str) -> dict:
        """ Returns the dictionary that indexes an 'Id' to the list index of that 'sequence'. """
        dct = self._hash[acase]["id-to-idx"]
        assert isinstance(dct, dict), "Expected dict"
        if None in dct:
            return {}
        return dct

    def do_id_hash(self) -> list:
        """ Returns the list of normalized cases.
        """
        res = []
        if not self.byname:
            return res
        self._hash = {}
        for acase, data in self.byname["ptr"].items():
            mash = {}
            self._hash[acase] = mash
            if isinstance(data, list) and data:
                is_ok = False
                last = data[-1]
                an_id = last.get("Id")
                if an_id == 0:
                    is_ok = self._do_id_index(mash, data, last)
                if is_ok:
                    res.append(acase)
        return res

    def _do_id_index(self, mash, data, last:dict) -> bool:
        """ Indexes:
		"Id": from numerical id to name
		pos.
		pos.
		pos.
        """
        assert last["Id"] == 0, 'Expected last "Id: 0"'
        id_to_name, name_to_id = {}, {}
        knames = {
            "keying": [],
            "dupname": [],
        }
        where = {}
        msgs = []
        for idx, item in enumerate(data):
            an_id = item["Id"]
            if an_id <= 0:
                continue
            if an_id in where:
                msg = f"Duplicate Id={an_id}, is: {data[where[an_id]]}"
                msgs.append(msg)
            else:
                where[an_id] = idx
            whot, namer = self._best_name(item, JIndex.do_jstrip)
            if knames["keying"]:
                if whot not in knames["keying"]:
                    knames["keying"].append(whot)
            id_to_name[an_id] = namer
            if namer in name_to_id:
                shown_ref = ("first", name_to_id[namer])
                #print("# Duplicate name:", an_id, namer, shown_ref)
                knames["dupname"].append((an_id, namer, shown_ref))
            else:
                #print("# Added name:", an_id, namer)
                name_to_id[namer] = an_id
        anyout = [(key, knames[key]) for key in sorted(knames) if knames[key]]
        name_to_id["~"] = anyout if anyout else 0
        mash["id-to-name"] = id_to_name
        mash["name-to-id"] = name_to_id
        if msgs:
            where = {None: msgs}
        mash["id-to-idx"] = where
        return True

    def _best_name(self, dct, j_strip=True):
        if "Name" in dct:
            return "Name", dct["Name"]
        tics, keying = [], []
        for key in sorted(dct):
            if key == "Id":
                continue
            aval = dct[key]
            if isinstance(aval, (str, float, int)):
                keying.append(key)
                tics.append(f"{aval}")
        astr = '|'.join(tics)
        if j_strip:
            astr = astr.rstrip('|')
        res = ('+'.join(keying), astr)
        return res
