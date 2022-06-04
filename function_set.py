# function_set.py  (c)2022  Henrique Moreira

""" Example of handling DLISTs
"""

# pylint: disable=missing-function-docstring

from copy import deepcopy
import jcommon

def main():
    is_ok = do_test1()
    assert is_ok, "test1"

def do_test1() -> bool:
    mydata = jcommon.AData(name="test1")
    assert mydata.name
    a_default = mydata.default_dlist()
    seq = mydata.to_alist(a_default)
    obj = jcommon.AData(seq, name="alist-sample")
    astr = obj.to_json()
    assert astr
    assert astr[-1] == "\n", f"Last char is not new-line: {ord(astr[-1])}d/0x{ord(astr[-1]):02x}"
    #print(astr)
    cont = obj.content()
    assert cont
    #print("Content:", cont)
    last = seq[-1]
    key, cpy = deepcopy(last)
    assert key == "~", key
    assert cpy
    print(cpy)
    return True

if __name__ == "__main__":
    main()
