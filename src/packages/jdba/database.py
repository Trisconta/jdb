# database.py  (c)2022  Henrique Moreira

""" Database - a set of boxes

Each box is a json file; database is a set of boxes;
each 'case' designates one list of dictionaries.
"""

# pylint: disable=missing-function-docstring

import os
import json
import jdba.jcommon
from jdba.jbox import JBox
from jdba.strict import StrictSchema

class GenDatabase(jdba.jcommon.GenericData):
    """ Generic database operations
    """
    def __init__(self, name="", encoding=None):
        myname = name if name else "dbx"
        super().__init__(myname, encoding)
        self._reclassify = False
        self._auto_validate = False
        self._msg = ""

    def message(self) -> str:
        return self._msg

class Database(GenDatabase):
    """ (JSON) Database handling
    """
    def __init__(self, path, name="", encoding=None):
        super().__init__(name, encoding)
        self._path = path
        self._schema, self._names, self._paths = self._initializer(path)
        self._index = self._reload()
        #self._reclassify = True  # -- uncomment if you changed schema, and
        # you want to assure that schema will be indented and sorted properly.
        if self._reclassify:
            self._schema.saver()
        if self._auto_validate:
            self._msg = self._schema.validate(self._index)

    def get_indexes(self) -> dict:
        """ Returns all indexes """
        return self._index

    def tables(self) -> dict:
        """ Returns all indexes """
        return self._index["tables"]

    def table(self, name:str):
        return self._index["tables"][name][1]

    def schema(self):
        """ Returns database schema class instance. """
        assert self._schema, self.name
        return self._schema

    def basic_ok(self) -> bool:
        """ Returns True if everything is basically ok. """
        return self._msg == ""

    def save(self, name:str="", debug=0) -> bool:
        """ Saves table(s): if name provided, saves only the corresponding table.
        """
        fails = []
        if self._msg:
            return False
        if name:
            path = self._paths[name]
            if debug > 0:
                print(f"Saving {name} at: {path}")
            return self.table(name).save(path)
        for key in sorted(self._paths):
            assert key, self.name
            is_ok = self.save(key)
            if not is_ok:
                fails.append(key)
        if fails:
            self._msg = f"Failed Save(s): {'; '.join(fails)}"
            return False
        if debug > 0:
            print(f"Saved {self.name} all")
        return True

    def complain_err(self, msg, opt):
        if opt:
            print(f"{msg}: {opt}")
        else:
            print(msg)

    def _initializer(self, path:str):
        assert isinstance(path, str)
        adir = path
        try:
            listed = os.listdir(path)
        except NotADirectoryError:
            adir, listed = self._listed_dir(path)
        schema, names, paths = {}, {}, {}
        for filename in listed:
            cpath = os.path.realpath(os.path.join(adir, filename))
            if filename.endswith(".json"):
                print("Loading:", filename)
                tname = filename[:-len(".json")]
                if tname in ("schema",):
                    new = JBox(name=cpath)
                    try:
                        new.load(cpath)
                    except json.decoder.JSONDecodeError as what:
                        self.complain_err(f"Unable to read schema: {cpath}", what)
                        continue
                    alist = new.dlist.get_case("boxes")
                    schema = StrictSchema(new, slim_list(alist))
                else:
                    names[tname], paths[tname] = filename, cpath
        #print("Read:", path, "; encoding:", self.get_encoding())
        #print("- NAMES:", names, "\n- PATHS:", paths)
        if not schema:
            self._msg = f"No json at: {path}"
            schema = StrictSchema(JBox(name="empty"), [])
        return schema, names, paths

    def _reload(self) -> dict:
        res = {
            "tables": {},
            "indexes": {},
        }
        boxes = self._schema.inlist
        if not boxes:
            return res
        for box in boxes:
            an_id, key = box["Id"], box["Key"]
            path = self._paths[key]
            assert an_id, key
            new = JBox(name=f"{an_id}:{key}")
            assert key not in res["tables"], key
            is_ok = new.load(path)
            res["tables"][key] = (new.dlist, new, int(is_ok))
        return res

    def _listed_dir(self, path:str) -> tuple:
        adir = os.path.dirname(os.path.realpath(path))
        return adir, os.listdir(adir)

def slim_list(alist):
    assert isinstance(alist, list)
    if not alist:
        return []
    last = alist[-1]
    an_id = last["Id"]
    if an_id == 0:
        return alist[:-1]
    return alist

# Main script
if __name__ == "__main__":
    print("Please import me!")
