# math-dict

日本語IME用の数学用語辞書 — a Japanese IME dictionary of mathematical terminology.

Japanese IMEs are good at everyday Japanese and bad at mathematics. They will not give you
準同型写像, they will not give you 冪零元, and they have no idea what ⊗ or グロタンディーク are.
This is a dictionary that fixes that, published for **Google 日本語入力 / Mozc, macOS 日本語入力,
Microsoft IME, and ATOK**.

## Install

Grab the file for your IME from [`dist/`](dist/) — no cloning or building required.

| IME | file | how |
|---|---|---|
| **Google 日本語入力 / Mozc** | [`dist/google/math_dict_ja.txt`](dist/google/math_dict_ja.txt) | 辞書ツール → 管理 → 新規辞書にインポート |
| **macOS 日本語入力** | [`dist/macos/math_dict_ja.plist`](dist/macos/math_dict_ja.plist) | システム設定 → キーボード → ユーザ辞書 にドラッグ＆ドロップ |
| **Microsoft IME** | [`dist/msime/math_dict_ja.txt`](dist/msime/math_dict_ja.txt) | 単語の登録 → ユーザー辞書ツール → ツール → テキストファイルからの登録 |
| **ATOK** | [`dist/atok/math_dict_ja.txt`](dist/atok/math_dict_ja.txt) | 辞書ユーティリティ → ツール → ファイルから登録・削除 |

**Tested honestly:** only the macOS build has been import-tested end to end. The Google, MS-IME,
and ATOK builds are verified *structurally* — correct encoding, BOM, line endings, and POS names
drawn from each vendor's documented list — but nobody has run them through a Windows or ATOK
install. If one fails to import, that is a bug and an issue is welcome.

## What's in it, and what isn't

Entries are **true readings**, not abbreviations. 数学的帰納法 is keyed `すうがくてききのうほう`,
not `きのう`. Short triggers that expand to long terms are explicitly *not* what this is: they
collide with everyday words (`きのう` is 昨日) and quietly degrade ordinary typing.

Included: kanji compounds (準同型写像, 極大イデアル), symbols (∀ ⊗ ℝ α), サ変 nouns, mathematician
names (ガロア, グロタンディーク), and Latin-script terms (well-defined, mod).

## Contributing a term

Edit the right file in [`terms/`](terms/) — that is the source of truth. `dist/` is generated.

```
reading <TAB> word <TAB> pos <TAB> flags?
じゅんどうけい	準同型	noun
```

`pos` is IME-neutral — `noun`, `noun-suru` (takes する), `noun-adj` (takes な), `person`, `symbol`,
`latin` — and the build maps it to each IME's vocabulary. Category comes from the filename; never
repeat it per row. `flags` is optional and comma-separated: `common` (the reading is also an
everyday word), `low-confidence` (the reading wants a second pair of eyes).

Then:

```sh
python3 validate.py   # invariants; regenerates REVIEW.md
python3 build.py      # terms/ -> dist/
```

Both run in CI, and CI additionally asserts that the committed `dist/` matches what `terms/`
actually builds to. That check exists because a stale generated file is the one failure mode
nobody notices until their import silently lacks the new terms.

`validate.py` rejects abbreviations by requiring a reading to have at least as many morae as the
term has kanji. It is a floor, not a proof — it catches `きのう→数学的帰納法` (3 morae, 6 kanji)
but not `こゆう→固有値` (3 for 3). Read the diff; don't just trust the green check.

See [REVIEW.md](REVIEW.md) for entries flagged as collision-prone or unverified. They ship — a
wrong reading merely never fires, which costs nothing — but they are worth a glance.

## License

[CC0 1.0](LICENSE) — public domain. It is a list of words and how they are read.
