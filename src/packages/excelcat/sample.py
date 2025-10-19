# sample.py  (c)2025  Henrique Moreira

""" sample.py - Sample usage of
"""

# pylint: disable=missing-function-docstring

import sys
import openpyxl
import excelcat
from excelcat.pyxl import show_w


MY_PAGE_SCALE = 98.0
HDR_RIGHT_STR = "(act.)"
HAS_TIME_IN_DATE = False


def main():
    msg = script(sys.argv[1:])
    if msg:
        print(msg)


def script(args):
    """ I used this at sumula_ordem.xlsx the first time.
    Print Preview: A4 Landscape props ok, but saving as automatic didn't work well.
    """
    out_save = "/tmp/new.xlsx"
    time_suffix = " &T" if HAS_TIME_IN_DATE else ""
    opts = {
        "out": out_save,
        "page-header": [
            "&L$101",
            "&C",
            f"&R{HDR_RIGHT_STR}&D{time_suffix}" if HDR_RIGHT_STR else "",
        ],
        "page-footer": [
            "&L",
            "&CPag.&P/&N",
            "&R",
        ],
    }
    param = args if args else ["test-input.xlsx"]
    while param and param[0].startswith("-"):
        if param[0].startswith(("-o", "--out-file")):
            out_save = param[1]
            del param[:2]
            continue
        return f"Bad choice: {[param[0]]}"
    infile, rest = param[0], param[1:]
    assert not rest, "Cowardly exiting, unknown extra parameters"
    tup = copy_first(infile, opts, save_to=out_save)
    _, _, msg = tup
    if msg:
        print(msg)
    return ""


def copy_first(infile, opts=None, do_save=True, save_to=""):
    opts = {} if opts is None else opts
    hdr = opts.get("page-header", [None, None, None])
    ftr = opts.get("page-footer", [None, None, None])
    new_scale = MY_PAGE_SCALE
    mbk = excelcat.pyxl.MyBook()
    isok = mbk.load(infile)
    assert isok, infile
    wbk = openpyxl.Workbook()
    new_sheet = wbk.active
    dct = mbk.copy_sheet(1, new_sheet)
    show_w(dct, "widths")
    if not do_save:
        return None, None, ""
    # Updating for 1 page wide, and 2 pages height
    print("Updating and saving:", save_to)
    mbk.update_fits(new_sheet, 1, 2)
    #mbk.update_new_scale(new_sheet, 98.0)
    if any((hdr[0], ftr[0])):
        print("Update headers:", hdr, ftr)
        mbk.update_headers(new_sheet, hdr, ftr)
    if new_scale > 0.0:
        new_sheet.page_setup.scale = new_scale
    wbk.save(save_to)
    return mbk, wbk, f"Saved xlsx, updated scale: {new_scale}"


# Main script
if __name__ == "__main__":
    main()
