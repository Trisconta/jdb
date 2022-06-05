# function_add.py  (c)2022  Henrique Moreira

""" Example of adding elements to DLISTs
"""

# pylint: disable=missing-function-docstring

import sys
from copy import deepcopy
import jdba.jcommon as jcommon

def main():
    msg = do_add(sys.argv[1:])
    is_ok = msg == ""
    assert is_ok, msg

def do_add(args) -> str:
    param = args if args else ["yes.json"]
    io_fname = param[0]
    del param[0]
    if param:
        return "Too many params"
    msg = process_io(io_fname)
    return msg

def process_io(io_fname:str) -> str:
    with open(io_fname, "r", encoding="utf-8") as fdin:
        data = jcommon.read_json(fdin)
    mydata = jcommon.AData(data, name="test1")
    altdata = jcommon.DData(data, name="dlist")
    #print("Content:", altdata.content(), end="---\n\n")
    entries = mydata.get_case("youtube-index")
    print("mydata index, byname:", mydata.index.byname["case"])
    assert mydata.index.initialized(), mydata.name
    there = [one for one in entries if one["Id"]]
    for one in there:
        key = one["Id"]
        print("Entry:", key, one)
    return ""

if __name__ == "__main__":
    main()
