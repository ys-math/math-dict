#!/usr/bin/env python3
"""Assert each dist/ artifact is byte-for-byte what its IME demands.

Worth being pedantic here: MS-IME and ATOK reject UTF-8 outright, and the failure is
silent — the import just doesn't happen, or arrives as mojibake. Nothing downstream
would catch it.

Note that these must be checked on *decoded* text. In UTF-16 a CRLF is the four bytes
0d 00 0a 00, so grepping raw bytes for \\r\\n never matches even when the file is
perfectly correct.
"""
import plistlib
import sys

failures = []


def check(cond, msg):
    print(("  ok    " if cond else "  FAIL  ") + msg)
    if not cond:
        failures.append(msg)


for name in ("msime", "atok"):
    path = f"dist/{name}/math_dict_ja.txt"
    raw = open(path, "rb").read()
    print(path)
    check(raw[:2] in (b"\xff\xfe", b"\xfe\xff"), "UTF-16 BOM present (UTF-8 would not import)")
    try:
        text = raw.decode("utf-16")
    except UnicodeDecodeError as e:
        check(False, f"decodes as UTF-16 ({e})")
        continue
    check(text.count("\n") == text.count("\r\n"), "every line ends CRLF, no bare LF")
    if name == "atok":
        head = text.splitlines()[0].strip()
        check(head == "!ATOK_TANGO_TEXT_HEADER_1", f"ATOK header line (got {head!r})")

path = "dist/google/math_dict_ja.txt"
raw = open(path, "rb").read()
print(path)
try:
    raw.decode("utf-8")
    check(True, "valid UTF-8")
except UnicodeDecodeError as e:
    check(False, f"valid UTF-8 ({e})")
check(b"\r" not in raw, "LF only, no CR")

path = "dist/macos/math_dict_ja.plist"
print(path)
try:
    entries = plistlib.load(open(path, "rb"))
    check(all({"shortcut", "phrase"} <= set(e) for e in entries),
          f"well-formed plist, {len(entries)} entries with shortcut+phrase")
except Exception as e:
    check(False, f"parses as a plist ({e})")

print(f"\n{len(failures)} failures")
sys.exit(1 if failures else 0)
