#!/usr/bin/env python3
"""Check the invariants that keep this dictionary from quietly hurting the user.

Errors block CI. Warnings land in REVIEW.md for human eyes.

The distinction is deliberate. A wrong reading on a rare term is dead weight — the
entry simply never fires, and nothing is lost. A reading that collides with an
everyday word is what actually costs something: it pushes a mathematical term into
the candidate list every time you type ordinary Japanese. So collisions are surfaced,
never silently dropped, even though we ship them.
"""
import sys
import unicodedata
from pathlib import Path

TERMS = Path(__file__).parent / "terms"
REVIEW = Path(__file__).parent / "REVIEW.md"

POS = {"noun", "noun-suru", "noun-adj", "person", "symbol", "latin"}
FLAGS = {"common", "low-confidence"}

# Small kana carry no mora of their own (っ does, so it is not listed here).
NON_MORAIC = set("ゃゅょぁぃぅぇぉゎ")
KANA = set("ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとど"
           "なにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんー")
KATAKANA = set("ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトド"
               "ナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴー")


def is_kanji(ch: str) -> bool:
    return unicodedata.name(ch, "").startswith("CJK UNIFIED IDEOGRAPH")


def morae(reading: str) -> int:
    return sum(1 for ch in reading if ch not in NON_MORAIC)


def read_entries():
    for path in sorted(TERMS.glob("*.tsv")):
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip() or raw.startswith("#"):
                continue
            cols = raw.split("\t")
            yield path, lineno, cols


def main() -> int:
    errors, warnings, inert, seen = [], [], [], {}

    for path, lineno, cols in read_entries():
        where = f"{path.name}:{lineno}"
        if not 3 <= len(cols) <= 4:
            errors.append(f"{where}: expected 3-4 tab-separated columns, got {len(cols)}")
            continue

        reading, word, pos = cols[0], cols[1], cols[2]
        flags = set(cols[3].split(",")) - {""} if len(cols) == 4 else set()

        bad_kana = [c for c in reading if c not in KANA]
        if bad_kana:
            errors.append(f"{where}: reading {reading!r} must be hiragana only "
                          f"(offending: {''.join(bad_kana)})")
        if not word or "\t" in word:
            errors.append(f"{where}: word must be non-empty and tab-free")
        if pos not in POS:
            errors.append(f"{where}: unknown pos {pos!r} (allowed: {', '.join(sorted(POS))})")
        if flags - FLAGS:
            errors.append(f"{where}: unknown flags {sorted(flags - FLAGS)}")

        # An abbreviation dressed up as a reading. Every kanji is at least one mora,
        # so a reading shorter than the kanji count cannot be a real reading. This is
        # what catches a きのう→数学的帰納法 regression.
        kanji = sum(1 for ch in word if is_kanji(ch))
        if kanji and morae(reading) < kanji:
            errors.append(f"{where}: {reading}→{word} looks like an abbreviation, not a "
                          f"reading ({morae(reading)} morae for {kanji} kanji)")

        # A pure-katakana word has exactly one possible reading: itself, in hiragana.
        # No judgment involved, so a mismatch is always a typo — この規則が
        # ぷあんかれ→ポアンカレ の類のミスを機械的に潰す。
        # ヴ is the exception: Japanese typing accepts both the v-row and the b-row
        # (ヴェイユ is typed うぇいゆ as often as ゔぇいゆ), so it gets a warning, not an error.
        if word and all(c in KATAKANA for c in word):
            expect = "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in word)
            if reading != expect:
                if "ヴ" in word:
                    warnings.append((reading, word, where, "ヴ — check the reading you'd type"))
                else:
                    errors.append(f"{where}: {reading}→{word} — katakana word must be read "
                                  f"exactly as written ({expect})")

        key = (reading, word)
        if key in seen:
            errors.append(f"{where}: duplicate of {seen[key]} — {reading}→{word}")
        else:
            seen[key] = where

        # The IME transliterates any kana input to katakana by itself, so an entry whose
        # word is exactly its own reading in katakana adds no candidate string the IME
        # was not going to offer anyway. Harmless, but it does no work either.
        #
        # These are tracked apart from the warnings table on purpose. They are numerous —
        # every katakana mathematician is one — and they need no decision, so listing them
        # alongside the collisions would bury the entries that do need a human call.
        if word and all(c in KATAKANA for c in word) and reading == "".join(
                chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in word):
            inert.append((reading, word, where))

        if "common" in flags or morae(reading) <= 2:
            warnings.append((reading, word, where, "collides with everyday Japanese"))
        if "low-confidence" in flags:
            warnings.append((reading, word, where, "reading unverified"))

    lines = ["# REVIEW", "",
             "Generated by `validate.py`. These entries ship — nothing here blocks the build —",
             "but each is worth a human glance.", "",
             "**Collisions** are the ones that actually cost you something: the reading is also an",
             "ordinary Japanese word, so this entry will crowd the candidate list when you write",
             "normal prose. They are kept per the completeness decision; delete any that annoy you.",
             "", f"**{len(warnings)} flagged / {len(seen)} entries**", "",
             "| reading | word | source | why |", "|---|---|---|---|"]
    lines += [f"| {r} | {w} | `{src}` | {why} |" for r, w, src, why in sorted(warnings)]

    # Inert entries need no decision, so they sit below the fold rather than in the table.
    lines += ["", "## IMEが自前で変換できる項目", "",
              f"**{len(inert)} entries.** The word is exactly its own reading in katakana, so the",
              "IME already offers that string and the entry adds no new candidate. Nothing to decide",
              "here — they are listed only so the count stays visible.", "",
              "<details><summary>Show all</summary>", "",
              "| reading | word | source |", "|---|---|---|"]
    lines += [f"| {r} | {w} | `{src}` |" for r, w, src in sorted(inert)]
    lines += ["", "</details>"]

    REVIEW.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    print(f"{len(seen)} entries, {len(errors)} errors, "
          f"{len(warnings)} flagged, {len(inert)} inert → REVIEW.md")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
