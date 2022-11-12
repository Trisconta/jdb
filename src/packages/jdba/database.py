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
        self._validate_before_save = True
        self._msg = ""

    def message(self) -> str:
        return self._msg

class Database(GenDatabase):
    """ (JSON) Database handling
    """
    def __init__(self, path, name="", encoding=None, has_schema=True):
        super().__init__(name, encoding)
        self._path = path
        self._init_schema = {} if has_schema else None
        self._schema, self._names, self._paths = self._initializer(path)
        self._index = self._reload()
        self.default_box = ""
        #self._reclassify = True  # -- uncomment if you changed schema, and
        # you want to assure that schema will be indented and sorted properly.
        if self._reclassify:
            self._schema.saver()
        if self._auto_validate:
            self._msg = self._schema.validate(self._index)

    def path_refs(self) -> dict:
        return {} if self._msg else self._paths

    def all_paths(self) -> list:
        return [self._paths[key] for key in sorted(self._paths)]

    def get_indexes(self) -> dict:
        """ Returns all indexes """
        return self._index

    def tables(self) -> dict:
        """ Returns all indexes """
        return self._index["tables"]

    def table(self, name:str=""):
        assert isinstance(name, str)
        tname, tbl = self._get_table(name)
        assert tname, self.name
        return tbl

    def schema(self):
        """ Returns database schema class instance. """
        assert self._schema, self.name
        return self._schema

    def valid_schema(self, debug=0) -> bool:
        """ Returns True if boxes are according to the schema. """
        msg = self._validate_schema()
        if debug > 0:
            print(f"Debug: valid_schema(): {msg if msg else 'OK'}")
        return msg == ""

    def basic_ok(self) -> bool:
        """ Returns True if everything is basically ok. """
        return self._msg == ""

    def save(self, name:str="", debug=0) -> bool:
        """ Saves table(s): if name provided, saves only the corresponding table.
        """
        msg = "; no check"
        if self._validate_before_save:
            msg = self._validate_schema()
            if msg:
                self._msg = msg
                return False
            msg = "; checked schema"
        if debug > 0:
            print("About to save:", sorted(self.tables()), msg)
        is_ok, invalid, _ = self._save_tables(name, debug)
        if debug > 0:
            if invalid:
                print("At least one invalid table:", invalid)
            else:
                print(f"Saved {self.name} all", is_ok)
        return is_ok

    def _save_tables(self, name, debug):
        fails = []
        failed = ""
        if self._msg:
            return False, "", []
        if name:
            path = self._paths[name]
            if debug > 0:
                print(f"Saving {name} at: {path}")
            return self.table(name).save(path), "", []
        for key in sorted(self._paths):
            assert key, self.name
            is_ok = self._save_tables(key, debug)
            if not is_ok:
                if not failed:
                    failed = key
                fails.append(key)
        if fails:
            self._msg = f"Failed Save(s): {'; '.join(fails)}"
            return False, failed, fails
        return True, "", []

    def complain_err(self, msg, opt):
        if opt:
            print(f"{msg}: {opt}")
        else:
            print(msg)

    def _initializer(self, path:str, debug=0):
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
                if debug > 0:
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
            if self._init_schema is not None:
                self._msg = f"No json schema at: {path}"
            schema = StrictSchema(JBox(name="empty"), [])
        return schema, names, paths

    def _get_table(self, name):
        names = sorted(self.tables())
        assert names, f"table() name='{name}'"
        if name:
            tname = name
        else:
            tname = self.default_box if self.default_box else names[0]
        return tname, self._index["tables"][tname][1]

    def _validate_schema(self) -> str:
        """ Validates boxes against schema. Returns empty if all ok. """
        msg = self.schema().validate(self.get_indexes())
        return msg

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

def loader(adir, main_table=""):
    dbx = jdba.database.Database(adir)
    dbx.default_box = main_table
    return dbx

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
