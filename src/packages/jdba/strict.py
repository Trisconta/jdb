# strict.py  (c)2022  Henrique Moreira

""" Strict - handling strict schemas
"""

# pylint: disable=missing-function-docstring
import jdba.jcommon
from jdba.jcommon import overview

DEBUG = 0

class StrictSchema(jdba.jcommon.DataSchema):
    """ Strict database schemas
    """
    def __init__(self, obj, inlist, name="", encoding=None):
        myname = name if name else "schema"
        super().__init__(obj.raw(), myname, encoding)
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

    def validate(self, ndexing, debug=DEBUG) -> str:
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
        msg = self._validate_ordr(
            (tname, cases, box, used),
            ndexing, order,
            debug
        )
        return msg

    def _validate_ordr(self, tup:tuple, ndexing, order:list, debug):
        assert isinstance(order, list)
        tname, cases, box, used = tup
        assert box, tname
        if debug > 0:
            print("::: validate_ordr():", overview(cases))
        for tname, cases, box in order:
            if debug > 0:
                print(f"validate() tname={tname}, order is {overview(order)}")
            dlist, _, ok_code = ndexing["tables"][tname]
            if not ok_code:
                return f"Faulty '{tname}'"
            for acase in used[tname]:
                for idx, dct in enumerate(acase, 1):
                    if debug > 0:
                        print(
                            f"validate() acase='{acase}' idx={idx}/{len(acase)}",
                            dct,
                        )
                    an_id, key, field_type = dct["Id"], dct["Key"], dct["FieldType"]
                    infos = (tname, key, an_id, dct["Method"])
                    #print("infos:", infos, "; an_id:", an_id, idx, field_type)
                    msg = f"Failed case={key}, field_type={field_type}, {idx}, got {an_id}"
                    assert an_id == idx, msg
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

def validate_uniqueness(elems, infos, depth, debug=DEBUG) -> str:
    if debug > 0:
        print(
            f"validate_uniqueness(), depth={depth}",
            infos, overview(elems),
        )
    if depth > 10:
        # Avoid too much recursiveness
        return ""
    boxname, acase, c_id, methods = infos
    assert acase, boxname
    assert c_id >= 1, boxname
    #print(":::", boxname, "case id:", c_id, acase, "; method:", methods)
    if methods:
        msg = methods_validate(elems, infos, methods, depth, "uq")
        return msg
    if isinstance(elems, dict):
        return validate_dict_keying(elems, infos)
    if not isinstance(elems, list):
        return f"Not a list {infos} (depth={depth}), {type(elems)}"
    ids = {}
    if not elems:
        return ""
    if len(elems) == 1:
        return validate_uniqueness(elems[0], infos, depth+1)
    for idx, elem in enumerate(sorted(elems), 1):
        #print("idx:", idx, elem)
        if elem in ids:
            there = ids[elem]
            return f"Duplicate field idx={idx} {infos}: <<{there}>>"
        ids[elem] = idx
    return ""

def methods_validate(elems, infos, methods, depth, m_str) -> str:
    """ Before calling micro_validate() """
    assert m_str
    assert depth <= 0
    _, acase, c_id, _ = infos
    assert c_id >= 1
    for methd in methods:
        an_id = methd["Id"]
        if an_id < 1:
            continue
        uqs = methd.get("UniqueFields")
        flds = uqs if uqs else []
        #print("Debug:", acase, "; method:", methd, flds, ">>>", overview(elems), "<<<")
        msg = validate_fields_uq(elems, infos, flds)
        if msg:
            return msg
    return ""

def validate_fields_uq(elems, quad, fields):
    """ Validate field(s) uniqueness
    """
    _, acase, _, _ = quad
    assert acase
    for field in fields:
        msg = micro_validate(elems, acase, field)
        if msg:
            return msg
    return ""

def micro_validate(elems, acase, field):
    #print("VALIDATE:", acase, "; field:", field)
    msgs = []
    used = {}
    for item in elems:
        an_id = item["Id"]
        if an_id < 1:
            continue
        hint = f" ({an_id})"
        fld_val = item[field]
        if fld_val in used:
            #print("Already used:", item, "; by:", used[fld_val])
            msg = f"Duplicate {field}='{fld_val}'{hint}; {used[fld_val]}"
            msgs.append(msg)
        else:
            used[fld_val] = item
    #for key in sorted(used):
    #    print(f":::# {acase}.{field} key={key}, as: {used[key]}")
    if len(msgs) > 1:
        msg = f"{len(msgs)} dups with {acase}.{field}, first: {msgs[0]}"
        return msg
    if msgs:
        msg = msgs[0]
        return msg
    return ""

def validate_dict_keying(elems:dict, infos):
    """ Dictionary has, by nature, unique keys.
    Just checking keying can be sorted, and keys are not empty.
    """
    for key in sorted(elems):
        if not key:
            return f"Bad dictionary: {infos}"
    return ""

# Main script
if __name__ == "__main__":
    print("Please import me!")
