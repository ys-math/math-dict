#!/usr/bin/env python3
"""Build one importable dictionary per IME from the neutral sources in terms/.

There is no single portable file. The IMEs disagree on encoding, line endings, and
part-of-speech vocabulary, and two of them reject UTF-8 outright — so portability has
to live here, in the build, rather than in the file format.

Where an IME's POS vocabulary is not something we could pin to a published list, the
mapping falls back to 名詞. A suboptimal POS still imports; an invalid POS name makes
the IME reject the row.
"""
import plistlib
import sys
from pathlib import Path

ROOT = Path(__file__).parent
TERMS = ROOT / "terms"
DIST = ROOT / "dist"

# Google IME / Mozc publishes its full POS list in the dictionary tool.
GOOGLE = {"noun": "名詞", "noun-suru": "名詞サ変", "noun-adj": "名詞形動",
          "person": "人名", "symbol": "記号", "latin": "アルファベット"}

# MS-IME and ATOK: only 名詞 and 人名 are confidently in both published 品詞 lists,
# so everything else degrades to 名詞 rather than risk a rejected row.
MSIME = {k: ("人名" if k == "person" else "名詞") for k in GOOGLE}
ATOK = {k: ("人名" if k == "person" else "名詞") for k in GOOGLE}

ATOK_HEADER = "!ATOK_TANGO_TEXT_HEADER_1"


def load():
    """Read terms/*.tsv → [(category, reading, word, pos)], sorted by category then reading."""
    entries = []
    for path in sorted(TERMS.glob("*.tsv")):
        lines = path.read_text(encoding="utf-8").splitlines()
        # The first comment line names the category: "# 圏論 / Category theory"
        category = next((l.lstrip("# ").split(" / ")[0] for l in lines if l.startswith("#")),
                        path.stem)
        rows = [l.split("\t") for l in lines if l.strip() and not l.startswith("#")]
        entries += [(category, r[0], r[1], r[2]) for r in rows]
    return sorted(entries, key=lambda e: (e[0], e[1]))


def write(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"  {path.relative_to(ROOT)}  ({len(data):,} bytes)")


def main() -> int:
    entries = load()
    print(f"{len(entries)} entries →")

    # Google IME / Mozc: UTF-8, LF, 4th column is a comment shown in the dictionary tool.
    rows = [f"{r}\t{w}\t{GOOGLE[p]}\t{cat}" for cat, r, w, p in entries]
    write(DIST / "google" / "math_dict_ja.txt",
          ("\n".join(rows) + "\n").encode("utf-8"))

    # MS-IME: UTF-16 + BOM (UTF-8 is rejected), CRLF.
    rows = [f"{r}\t{w}\t{MSIME[p]}\t{cat}" for cat, r, w, p in entries]
    write(DIST / "msime" / "math_dict_ja.txt",
          ("\r\n".join(rows) + "\r\n").encode("utf-16"))

    # ATOK: UTF-16, CRLF, and the header line is mandatory — it tells ATOK the POS
    # names are ATOK's own.
    rows = [ATOK_HEADER] + [f"{r}\t{w}\t{ATOK[p]}" for cat, r, w, p in entries]
    write(DIST / "atok" / "math_dict_ja.txt",
          ("\r\n".join(rows) + "\r\n").encode("utf-16"))

    # macOS Apple IM: XML plist, drag-and-drop into ユーザ辞書. Lossy by design —
    # the format has no POS field at all.
    plist = [{"shortcut": r, "phrase": w} for _, r, w, _ in entries]
    write(DIST / "macos" / "math_dict_ja.plist", plistlib.dumps(plist))

    return 0


if __name__ == "__main__":
    sys.exit(main())
