#!/usr/bin/env python3
"""Propose dictionary terms from a ys-math/math-study checkout.

Every entry in terms/ is attested in that corpus, and this is what does the
attesting. What the script cannot do is decide what counts as terminology:
存在 and 準同型 are both strings the author typed, and only one of them belongs
in a dictionary. So it emits candidates and remembers the verdicts — accepted
ones land in terms/*.tsv, rejected ones in terms/.rejected — and a rerun after a
new chapter shows the handful of genuinely new strings rather than all 180 again.

    python3 harvest.py [path/to/math-study] [--all]

--all ignores both verdict sets and re-proposes everything, which is what a
from-scratch rebuild or a re-audit of past decisions needs.
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
TERMS = ROOT / "terms"
REJECTED = TERMS / ".rejected"

# tex/<dir>/ ⟷ terms/<stem>.tsv. The mirror is the whole provenance story: a term
# lives in the file named after the directory it was harvested from, so "where did
# this come from" is answerable without a per-entry source column.
SUBJECTS = {
    "algebraic_k_theory": "00-algebraic-k-theory",
    "category_theory": "01-category-theory",
    "commutative_ring_theory": "02-commutative-ring-theory",
    "galois_theory": "03-galois-theory",
    "lambda_calculus": "04-lambda-calculus",
    "manifold": "05-manifold",
    "topology": "06-topology",
}

# Greek read as part of the term rather than as a symbol: λ計算 is ラムダ計算 when
# written in prose, and the dictionary holds no symbols.
GREEK = {"alpha": "アルファ", "beta": "ベータ", "gamma": "ガンマ", "delta": "デルタ",
         "epsilon": "イプシロン", "lambda": "ラムダ", "mu": "ミュー", "sigma": "シグマ",
         "phi": "ファイ", "psi": "プサイ", "omega": "オメガ", "eta": "イータ",
         "theta": "シータ", "rho": "ロー", "tau": "タウ", "xi": "クシー"}

JP = r"[\u4e00-\u9fff\u30a0-\u30ff\u3005ー]"


def group(s: str, i: int) -> tuple[str, int]:
    """Content of the brace group starting at s[i] == '{', and the index past it.

    A naive [^}]* stops at the first close brace, which truncates
    \\section{$C^{\\infty}$級多様体} to "$C^{\\infty" — the exact bug that would
    silently drop 多様体 from the dictionary.
    """
    depth, out = 0, []
    while i < len(s):
        if s[i] == "{":
            depth += 1
            if depth == 1:
                i += 1
                continue
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return "".join(out), i + 1
        out.append(s[i])
        i += 1
    return "".join(out), i


def marks(raw: str):
    """Terms the author explicitly marked: \\textbf definitions and section titles."""
    for m in re.finditer(r"\\(textbf|section|subsection)\s*(?=\{)", raw):
        yield group(raw, m.end())[0]


def strip_math(raw: str) -> str:
    """Prose with math, commands and comments removed.

    Single-letter math is deleted rather than blanked: 有限生成射影$R$加群 is one
    term interrupted by a bound variable, and blanking it would harvest two
    fragments instead. Longer math spans do separate words, so those become space.
    """
    raw = "\n".join(l for l in raw.splitlines() if not l.lstrip().startswith("%"))
    raw = re.sub(r"\\\[.*?\\\]", " ", raw, flags=re.S)
    raw = re.sub(r"\$[A-Za-z]\$", "", raw)
    raw = re.sub(r"\$[^$]*\$", " ", raw)
    raw = re.sub(r"\\[a-zA-Z]+\*?", " ", raw)
    return re.sub(r"[{}\[\]]", " ", raw)


def normalize(term: str) -> str | None:
    r"""A marked-up term as it should be written in prose, or None to discard.

    Bound variables go ($R$加群 is 加群 — the R is a placeholder, not part of the
    name), Greek is spelled out, and anything left with no Japanese in it was
    never a Japanese term: \LaTeX, GitHub, $K_0$, Yoneda lemma.
    """
    term = re.sub(r"\\texorpdfstring\s*\{", "{", term)
    for name, kana in GREEK.items():
        term = re.sub(r"\$?\\" + name + r"\b\$?", kana, term)
    term = re.sub(r"\$[^$]*\$?", "", term)          # bound variables, C^\infty, K_0
    term = re.sub(r"\\[a-zA-Z]+\*?|[{}\\]", "", term).strip()
    term = re.sub(r"^級", "", term)                  # C^∞級多様体 → 級多様体 → 多様体
    if not re.search(JP, term):
        return None
    return term or None


def verdicts() -> set[str]:
    """Everything already decided — accepted into terms/, or listed in .rejected."""
    known = set()
    for path in TERMS.glob("*.tsv"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                known.add(line.split("\t")[1])
    if REJECTED.exists():
        known |= {l.strip() for l in REJECTED.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.startswith("#")}
    return known


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--all"]
    source = Path(args[0]) if args else ROOT.parent / "math-study"
    tex = source / "tex"
    if not tex.is_dir():
        print(f"no tex/ under {source} — pass the path to a math-study checkout",
              file=sys.stderr)
        return 1

    known = set() if "--all" in sys.argv[1:] else verdicts()
    # term → subject dir → count. A term used in two chapters belongs to the file
    # for the one that uses it most; ties break alphabetically, via max()'s stability.
    tally: dict[str, Counter] = {}
    for subject in SUBJECTS:
        for path in sorted((tex / subject).glob("ch*.tex")):
            raw = path.read_text(encoding="utf-8")
            found = [normalize(t) for t in marks(raw)]
            found += re.findall(JP + "{2,}", strip_math(raw))
            for term in found:
                if term and term not in known:
                    tally.setdefault(term, Counter())[subject] += 1

    print(f"{len(tally)} candidates from {source}\n")
    for subject, stem in SUBJECTS.items():
        rows = sorted(((t, c.total()) for t, c in tally.items()
                       if max(c, key=c.get) == subject), key=lambda r: (-r[1], r[0]))
        if not rows:
            continue
        print(f"# {stem}.tsv  ← tex/{subject}/  ({len(rows)})")
        for term, n in rows:
            print(f"  {n:3d}  {term}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
