# strict.py  (c)2022  Henrique Moreira

""" Strict - handling strict schemas
"""

# pylint: disable=missing-function-docstring
import jdba.jcommon

class StrictSchema(jdba.jcommon.GenericData):
    """ Strict database schemas
    """
    def __init__(self, obj, inlist, name="", encoding=None):
        myname = name if name else "schema"
        super().__init__(myname, encoding)
        self._path = obj.name
        self._myself = obj
        self.inlist = inlist

    def boxes(self) -> list:
        return self._myself.dlist.get_case("boxes")

    def saver(self):
        """ This is usually not needed, as it is task of the db manager.
        But for clarity, it is laid down here.
        """
        return self._myself.save(self._path)

    def validate(self, ndexing) -> str:
        """ Returns an empty string if all ok. """
        order = []
        used = {}
        for box in self.inlist:
            an_id, tname, cases = box["Id"], box["Key"], box["Cases"]
            assert box["Title"], tname
            #print(tname, cases); print()
            order.append((tname, cases, box))
            assert tname not in used, tname
            used[tname] = cases
        if not ndexing:
            return "Nothing to validate"
        for tname, cases, box in order:
            dlist, _, ok_code = ndexing["tables"][tname]
            if not ok_code:
                return f"Faulty '{tname}'"
            #print(used[tname])
            for acase in used[tname]:
                for idx, dct in enumerate(acase, 1):
                    an_id, key, field_type = dct["Id"], dct["Key"], dct["FieldType"]
                    infos = (tname, key)
                    #print("infos:", infos, "; an_id:", an_id, field_type)
                    assert an_id == idx, field_type
                    elems = dlist.get_case(key)
                    msg = xvalidate_kinds(field_type, elems, infos)
                    if msg:
                        return msg
        return ""

def xvalidate_kinds(field_type, elems, infos) -> str:
    """ Returns an empty string if basic check succeeded. """
    if not isinstance(elems, list):
        return ""
    if field_type == "u-id":
        msg = validate_unique_id(elems, infos)
    elif field_type == "unique":
        msg = validate_uniqueness(elems, infos, 0)
    else:
        assert False, f"Invalid FieldType: {field_type}"
    return msg

def validate_unique_id(elems, infos) -> str:
    ids = {}
    for elem in elems:
        an_id = elem["Id"]
        if an_id in ids:
            there = ids[an_id]
            return f"Duplicate key {infos}: {an_id}, <<{there}>>"
        ids[an_id] = elem
    return ""

def validate_uniqueness(elems, infos, depth) -> str:
    if depth > 10:
        # Avoid too much recursiveness
        return ""
    if isinstance(elems, list):
        for item in elems:
            # Each one of the lists dicts has to be unique
            msg = validate_uniqueness(item, infos, depth+1)
            if msg:
                return msg
        return ""
    if not isinstance(elems, dict):
        return f"Not a dictionary {infos} (depth={depth}), {type(elems)}"
    ids = {}
    for idx, key in enumerate(sorted(elems), 1):
        elem = elems[key]
        if key in ids:
            there = ids[key]
            return f"Duplicate field idx={idx} {infos}: {key}, <<{there}>>"
        #print(infos, "key:", key, elem)
        ids[key] = elem
    return ""

# Main script
if __name__ == "__main__":
    print("Please import me!")
