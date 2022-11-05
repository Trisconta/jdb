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

    def saver(self):
        return self._myself.save(self._path)

    def validate(self, ndexing) -> str:
        """ Returns an empty string if all ok. """
        for box in self.inlist:
            an_id, tname, cases = box["Id"], box["Key"], box["Cases"]
            assert box["Title"], tname
            #print(tname, cases); print()
        if not ndexing:
            return "Nothing to validate"
        #print(ndexing) --> TODO
        return ""

# Main script
if __name__ == "__main__":
    print("Please import me!")
