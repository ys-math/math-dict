# math-dict

A Japanese IME dictionary for the terminology in [ys-math/math-study](https://github.com/ys-math/math-study).

[日本語版 README](README.ja.md)

Japanese IMEs handle everyday language well but struggle with mathematics. `かんしゅけん`,
`べきとうぎょうれつ` and `こうとうしゃ` do not reliably produce 関手圏, 冪等行列 or 恒等射. This
dictionary fills that gap for one specific corpus: **every term in it appears in the `.tex`
sources of math-study.** It is distributed in four formats: **Google 日本語入力 / Mozc, macOS
日本語入力, Microsoft IME, and ATOK**.

## Installing

Download the file for your IME from [`dist/`](dist/). No cloning or building required.

| IME | File | How to import |
|---|---|---|
| **Google 日本語入力 / Mozc** | [`dist/google/math_dict_ja.txt`](dist/google/math_dict_ja.txt) | 辞書ツール → 管理 → 新規辞書にインポート |
| **macOS 日本語入力** | [`dist/macos/math_dict_ja.plist`](dist/macos/math_dict_ja.plist) | Drag and drop into システム設定 → キーボード → ユーザ辞書 |
| **Microsoft IME** | [`dist/msime/math_dict_ja.txt`](dist/msime/math_dict_ja.txt) | 単語の登録 → ユーザー辞書ツール → ツール → テキストファイルからの登録 |
| **ATOK** | [`dist/atok/math_dict_ja.txt`](dist/atok/math_dict_ja.txt) | 辞書ユーティリティ → ツール → ファイルから登録・削除 |

The dictionary contains **177 entries**, one file per subject in math-study's `tex/`:

| file | source | entries |
|---|---|---:|
| [`terms/00-algebraic-k-theory.tsv`](terms/00-algebraic-k-theory.tsv) | `tex/algebraic_k_theory/` | 54 |
| [`terms/01-category-theory.tsv`](terms/01-category-theory.tsv) | `tex/category_theory/` | 60 |
| [`terms/02-commutative-ring-theory.tsv`](terms/02-commutative-ring-theory.tsv) | `tex/commutative_ring_theory/` | 25 |
| [`terms/03-galois-theory.tsv`](terms/03-galois-theory.tsv) | `tex/galois_theory/` | 1 |
| [`terms/04-lambda-calculus.tsv`](terms/04-lambda-calculus.tsv) | `tex/lambda_calculus/` | 24 |
| [`terms/05-manifold.tsv`](terms/05-manifold.tsv) | `tex/manifold/` | 7 |
| [`terms/06-topology.tsv`](terms/06-topology.tsv) | `tex/topology/` | 6 |

That is 134 plain nouns, 12 な-adjectives, 7 サ変 nouns, 7 mathematicians (米田, グロタンディーク,
Nakayama, Morita, Yoneda, Grothendieck, ハウスドルフ) and 17 Latin-script terms — the operator
names actually used in the sources (`Hom` `Ker` `Im` `Ob` `Mor` `dom` `cod` `id` `GL` `Cone` `Nat`
`op` `Proj` `Spec` `Map`) plus `iff` and `well-defined`.

**There are no symbols.** ℝ, ∀ and ⊗ are not here, and `symbol` is not a valid part of speech, so
`validate.py` rejects one on sight rather than leaving it to good intentions. Terms that contain a
Greek letter are spelled out instead: ラムダ計算, ベータ簡約, アルファ変換.

### What has actually been tested

So far, only the Google 日本語入力 build has been imported into a real IME and confirmed to work.
The other three have been checked for structural correctness — encoding, BOM, line endings,
part-of-speech names, plist structure — and nothing more. If one of them fails to import, that's
a bug, and an issue would be welcome.

### Upgrading from an earlier version

IME imports are **additive**, and there is no removal path. If you imported a build from before
this dictionary was rebuilt around math-study, those entries are still in your IME and re-importing
will not displace them. Delete the old dictionary inside the IME first, then import.

## What goes in

A term earns a place by **appearing in math-study**, and by being terminology rather than prose.
Both halves matter. `準同型` appears 22 times and is in; `存在` appears 58 times and is not, because
it is an ordinary word being used ordinarily. Strings judged not to be terminology are recorded in
[`terms/.rejected`](terms/.rejected) so the decision does not have to be made twice.

Entries use **the term's actual reading**, never an abbreviation. Short triggers that expand into
long terms are deliberately avoided: they collide with everyday vocabulary and make ordinary
Japanese input worse.

Compounds are registered whole *and* in parts — `全射準同型` sits next to `全射` and `準同型` — so
a long term converts in one shot instead of relying on the IME to segment it.

## A note on katakana terms

If you type `ほもとぴー` and get `ホモトピー`, that is **not** this dictionary at work. Japanese
IMEs already convert kana input straight to katakana, so the entry produces exactly the string the
IME would have offered anyway. **8 entries** fall into this category — イデアル, グロタンディーク,
シングルトン, ソート, ハウスドルフ, ホモトピー, レトラクト, アルファステップ. They are counted, but
not itemized, in `REVIEW.md` under 「IMEが自前で変換できる項目」.

The other 169 do real work: kanji compounds like 恒等射, 冪等行列 and 局所的に小さい圏, katakana–kanji
mixes like `グロタンディーク群` and `コンパクト開位相`, and Latin spellings such as `Hom` and
`well-defined`.

## Adding a term

`terms/` is the single source of truth; everything under `dist/` is generated. To pull in terms
from new math-study chapters:

```sh
python3 harvest.py            # propose candidates from ../math-study
python3 validate.py           # check the format, regenerate REVIEW.md
python3 build.py              # generate dist/ from terms/
```

`harvest.py` reads a math-study checkout (`../math-study` by default, or a path you pass) and
prints every Japanese string it finds that is neither already in `terms/` nor listed in
`terms/.rejected`. Accept one by adding a row to the matching file; reject one by adding it to
`.rejected`. Pass `--all` to re-propose everything and re-audit past decisions.

Rows are tab-separated:

```
reading <TAB> word <TAB> part-of-speech <TAB> flags (optional)
じゅんどうけい	準同型	noun
```

Parts of speech are IME-independent — `noun`, `noun-suru` (takes する), `noun-adj` (takes な),
`person`, `latin` — and the build maps them onto each IME's own scheme. The subject is determined
by the filename, so there's no need to repeat it per line. Flags are optional and comma-separated:
`common` (the reading collides with an everyday word) and `low-confidence` (the reading needs
checking).

Both scripts run in CI. CI additionally checks that the committed `dist/` matches what `terms/`
actually builds to, because a stale build artifact only reveals itself when someone imports the
dictionary and finds the new terms missing — by which point it has gone unnoticed for a while. CI
does **not** clone math-study: coupling this repo's builds to another repo's HEAD would turn a new
chapter into a red build here.

`validate.py` rejects abbreviations using the rule that a reading must have at least as many morae
as the word has kanji. This is only a lower bound. Read the diff rather than trusting a green CI run.

Terms whose readings collide with everyday words, and terms whose readings are unverified, are
collected in [REVIEW.md](REVIEW.md).

## Caveat

The terms are real: each one was lifted from a `.tex` file, so a fabricated term cannot get in.
**The readings are a different matter.** math-study has no furigana, so every reading was either
carried over from an earlier hand-checked version of this dictionary (81 of them) or generated
(96). 17 are marked `low-confidence` and listed in `REVIEW.md`; the Latin operator names are the
shakiest of them, since `Ob`, `Mor`, `dom`, `cod` and `Proj` have no settled Japanese reading.

A wrong reading is harmless — the entry simply never appears as a conversion candidate. But if you
come across one, it's a bug: please open an issue, or just fix the line.

## License

[CC0 1.0](LICENSE), public domain. It is a list of terms and their readings; there is no claim
worth making over it.
