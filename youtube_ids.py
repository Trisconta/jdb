# youtube_ids.py  (c)2022  Henrique Moreira

""" Show youtube ids
"""

# pylint: disable=missing-function-docstring

import sys
import base64


def main():
    is_ok = do_run(sys.argv[1:])
    assert is_ok, "test1"
    print("""

Thanks also to Tom Scott:
	https://www.youtube.com/watch?v=gocwRvLhDf8
""")
    return 0

def youtube_part(astr:str):
    res = base64.urlsafe_b64decode(astr)
    return res

def do_run(args):
    param = args if args else ["m63NZMgZZsc"]
    ten = [chr(ord('0')+val) for val in range(0, 10)]
    t23 = [chr(ord('a')+val) for val in range(0, 26)]
    t46 = [chr(ord('A')+val) for val in range(0, 26)] + t23
    xtr = ["-", "_"]
    ids = ten + t46 + xtr
    astr = ''.join(ids)
    alen = len(astr)
    assert alen == 64, astr
    for one in param:
        show_ytb(one)
    return True

def show_ytb(one:str):
    if len(one) == 11:
        pad = one + "="
    else:
        pad = one
    res = youtube_part(pad)
    print(pad, ":", res)
    back = base64.urlsafe_b64encode(res).decode("ascii")
    simpler = back.rstrip("=")
    print("Back to form:", simpler)
    assert one == simpler, one

if __name__ == "__main__":
    main()
