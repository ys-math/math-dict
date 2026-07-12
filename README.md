# math-dict

A Japanese IME dictionary of mathematical terminology.

[日本語版 README](README.ja.md)

Japanese IMEs handle everyday language well but struggle with mathematics. They won't convert
準同型写像 or 冪零元, and ⊗ and グロタンディーク don't come up at all. This dictionary fills that
gap. It's distributed in four formats: **Google 日本語入力 / Mozc, macOS 日本語入力,
Microsoft IME, and ATOK**.

## Installing

Download the file for your IME from [`dist/`](dist/). No cloning or building required.

| IME | File | How to import |
|---|---|---|
| **Google 日本語入力 / Mozc** | [`dist/google/math_dict_ja.txt`](dist/google/math_dict_ja.txt) | 辞書ツール → 管理 → 新規辞書にインポート |
| **macOS 日本語入力** | [`dist/macos/math_dict_ja.plist`](dist/macos/math_dict_ja.plist) | Drag and drop into システム設定 → キーボード → ユーザ辞書 |
| **Microsoft IME** | [`dist/msime/math_dict_ja.txt`](dist/msime/math_dict_ja.txt) | 単語の登録 → ユーザー辞書ツール → ツール → テキストファイルからの登録 |
| **ATOK** | [`dist/atok/math_dict_ja.txt`](dist/atok/math_dict_ja.txt) | 辞書ユーティリティ → ツール → ファイルから登録・削除 |

The dictionary contains **1,964 entries** spanning 23 fields (logic and set theory, algebra,
topology, analysis, category theory, commutative algebra, algebraic geometry, and others), plus
97 mathematical symbols, 397 mathematicians, and 24 Latin-script terms. Mathematicians are
registered under both spellings, so `がろあ` offers ガロア and Galois alike.

### What has actually been tested

So far, only the Google 日本語入力 build has been imported into a real IME and confirmed to work.
The other three have been checked for structural correctness — encoding, BOM, line endings,
part-of-speech names, plist structure — and nothing more. If one of them fails to import, that's
a bug, and an issue would be welcome.

## What goes in

Entries use **the term's actual reading**, never an abbreviation. 数学的帰納法 is keyed
`すうがくてききのうほう`, not `きのう`. Short triggers that expand into long terms are deliberately
avoided: they collide with everyday vocabulary (`きのう` is 昨日) and make ordinary Japanese input
worse.

The dictionary covers kanji compounds (準同型写像, 極大イデアル), symbols (∀ ⊗ ℝ α), サ変 nouns,
mathematicians (ガロア, グロタンディーク), and Latin-script terms (well-defined, mod).

## A note on katakana terms

If you type `こほもろじー` and get `コホモロジー`, that is **not** this dictionary at work. Japanese
IMEs already convert kana input straight to katakana, and `こほもろじー` transliterates one-to-one
into `コホモロジー` — so **pressing the space bar is all you need**. The dictionary entry produces
exactly the same string the IME would have offered on its own, so it adds no candidate that was
not already there. (Whether registering it nudges that candidate up the ranking is not something
we have measured; assume it does nothing.)

**305 entries** fall into this category, 270 of them katakana spellings of mathematicians' names.
They are kept for completeness — a dictionary of mathematicians that omitted アーベル because the
IME can spell it would be a strange dictionary — and they are counted, but not itemized, in
`REVIEW.md` under 「IMEが自前で変換できる項目」.

The line is finer than it looks. `シュヴァレー` is **not** in this category: it is typed
`しゅばれー`, and no IME turns a b-row kana into ヴ on its own. So ヴ-spelled names — ヴェイユ,
シュヴァルツ, シュヴァレー, ローヴェア — are real entries that do real work, even though they look
like plain katakana.

Where the dictionary genuinely helps is with terms the IME cannot produce by itself: kanji
compounds like 準同型写像, 冪零元, and 極大イデアル, but also `コホモロジー群` (a katakana–kanji
mix, so not a straight transliteration), `層コホモロジー`, `クリストッフェル記号`, kanji names like
高木貞治, and Latin spellings such as Galois and Grothendieck. That accounts for the remaining
1,659 entries.

## Adding a term

Edit the appropriate file under [`terms/`](terms/). That is the single source of truth; everything
under `dist/` is generated.

```
reading <TAB> word <TAB> part-of-speech <TAB> flags (optional)
じゅんどうけい	準同型	noun
```

Parts of speech are IME-independent — `noun`, `noun-suru` (takes する), `noun-adj` (takes な),
`person`, `symbol`, `latin` — and the build maps them onto each IME's own scheme. The field is
determined by the filename, so there's no need to repeat it per line. Flags are optional and
comma-separated: `common` (the reading collides with an everyday word) and `low-confidence` (the
reading needs checking).

After editing, run:

```sh
python3 validate.py   # checks the format, regenerates REVIEW.md
python3 build.py      # generates dist/ from terms/
```

Both run in CI. CI additionally checks that the committed `dist/` matches what `terms/` actually
builds to, because a stale build artifact only reveals itself when someone imports the dictionary
and finds the new terms missing — by which point it has gone unnoticed for a while.

`validate.py` rejects abbreviations using the rule that a reading must have at least as many morae
as the word has kanji. This is only a lower bound. It catches `きのう→数学的帰納法` (3 morae, 6
kanji) but lets `こゆう→固有値` (3 morae, 3 kanji) through. Read the diff rather than trusting a
green CI run.

Terms whose readings collide with everyday words, and terms whose readings are unverified, are
collected in [REVIEW.md](REVIEW.md).

## Caveat

The entries in this dictionary were drafted by a language model and then checked mechanically. The
checks catch formal errors — invalid kana, duplicates, katakana words whose reading doesn't match —
and they caught a good number of them. What the checks cannot catch is a **term that is
well-formed but does not exist**.

A wrong reading is harmless: the entry simply never appears as a conversion candidate. But a
**fabricated term converts perfectly well and slips straight into your writing**, which is the
more troublesome failure. If you come across a term that looks wrong, it's a bug — please open an
issue, or just delete the line.

## License

[CC0 1.0](LICENSE), public domain. It is a list of terms and their readings; there is no claim
worth making over it.
