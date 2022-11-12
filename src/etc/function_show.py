# function_add.py  (c)2022  Henrique Moreira

""" Example of adding elements to DLISTs
"""

# pylint: disable=missing-function-docstring

import sys
import os.path
import jdba
import jdba.jcommon as jcommon
from jdba.jbox import JBox

def main():
    msg = do_add(sys.argv[1:])
    if msg is None:
        print(f"""Usage:
{__file__} json-file [field]
""")
        return 0
    is_ok = msg == ""
    assert is_ok, msg
    return 0

def do_add(args):
    param = args if args else ["yes.json"]
    first = param[0]
    field = ""
    io_fname = first
    if first.startswith("-"):
        return None
    del param[0]
    if param:
        field = param[0]
        del param[0]
    if param:
        return "Too many params"
    if not field:
        field = "youtube-index"
    msg = process_io(io_fname, field)
    return msg

def process_io(io_fname:str, field:str, is_utf=False) -> str:
    enc_in = "utf-8" if is_utf else "ISO-8859-1"
    jdba.jcommon.SingletonIO().default_encoding = enc_in
    print("# Reading:", io_fname)
    with open(io_fname, "r", encoding=enc_in) as fdin:
        data = jcommon.read_json(fdin)
    mydata = jcommon.AData(data, name="test1")
    altdata = jcommon.DData(data, name="dlist")
    #print("Content:", altdata.content(), end="---\n\n")
    entries = mydata.get_case(field)
    shown = sorted(mydata.index.byname["case"])
    print("mydata index, byname:", shown)
    assert mydata.index.initialized(), mydata.name
    print()
    there = [one for one in entries if one["Id"]]
    for one in there:
        key = one["Id"]
        print("Entry:", key, one)
    print()
    entries = altdata.get_case(field)
    there = [one for one in entries if one["Id"]]
    print("altdata Entries:", there)
    print()
    header = altdata.get_case("!")[0]
    print("\n" + "Header:", header["Title"])
    assert header["Id"] == 0, f'Id expected 0, got {header["Id"]}'
    jbox = JBox()
    jbox.load(io_fname)
    print("\n" + "dlist:", jbox.dlist.raw())
    new_name = os.path.basename(io_fname) + "~"
    key = input(f"Enter YES to write file '{new_name}' ...")
    if key.lower() == "yes":
        print("Writing:", new_name)
        jbox.save(new_name)
    return ""

if __name__ == "__main__":
    main()
