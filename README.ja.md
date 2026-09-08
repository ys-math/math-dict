# math-dict

[ys-math/math-study](https://github.com/ys-math/math-study) で使われている数学用語の日本語 IME 辞書です。

[English README](README.md)

`かんしゅけん`、`べきとうぎょうれつ`、`こうとうしゃ` から 関手圏・冪等行列・恒等射 は安定して出てきません。この辞書はその穴を埋めます。**収録語はすべて math-study の `.tex` に実際に現れる語**です。

## 導入方法

[`dist/`](dist/) から使用している IME 用のファイルをダウンロードしてください。

| IME | ファイル | 取り込み方 |
|---|---|---|
| **Google 日本語入力 / Mozc** | [`dist/google/math_dict_ja.txt`](dist/google/math_dict_ja.txt) | 辞書ツール → 管理 → 新規辞書にインポート |
| **macOS 日本語入力** | [`dist/macos/math_dict_ja.plist`](dist/macos/math_dict_ja.plist) | システム設定 → キーボード → ユーザ辞書 にドラッグ＆ドロップ |
| **Microsoft IME** | [`dist/msime/math_dict_ja.txt`](dist/msime/math_dict_ja.txt) | 単語の登録 → ユーザー辞書ツール → ツール → テキストファイルからの登録 |
| **ATOK** | [`dist/atok/math_dict_ja.txt`](dist/atok/math_dict_ja.txt) | 辞書ユーティリティ → ツール → ファイルから登録・削除 |

収録語数は **177 語**です。math-study の `tex/` 以下のディレクトリと 1 対 1 に対応するファイルに分かれています。

| ファイル | 対応する原典 | 語数 |
|---|---|---:|
| [`terms/00-algebraic-k-theory.tsv`](terms/00-algebraic-k-theory.tsv) | `tex/algebraic_k_theory/` | 54 |
| [`terms/01-category-theory.tsv`](terms/01-category-theory.tsv) | `tex/category_theory/` | 60 |
| [`terms/02-commutative-ring-theory.tsv`](terms/02-commutative-ring-theory.tsv) | `tex/commutative_ring_theory/` | 25 |
| [`terms/03-galois-theory.tsv`](terms/03-galois-theory.tsv) | `tex/galois_theory/` | 1 |
| [`terms/04-lambda-calculus.tsv`](terms/04-lambda-calculus.tsv) | `tex/lambda_calculus/` | 24 |
| [`terms/05-manifold.tsv`](terms/05-manifold.tsv) | `tex/manifold/` | 7 |
| [`terms/06-topology.tsv`](terms/06-topology.tsv) | `tex/topology/` | 6 |

内訳は名詞 134 語、形容動詞 12 語、サ変名詞 7 語、数学者名 7 名（米田、グロタンディーク、ハウスドルフ、Nakayama、Morita、Yoneda、Grothendieck）、ラテン文字表記 17 語（原典で実際に使われている作用素名 `Hom` `Ker` `Im` `Ob` `Mor` `dom` `cod` `id` `GL` `Cone` `Nat` `op` `Proj` `Spec` `Map` と `iff`、`well-defined`）です。

**数学記号は収録していません。** ℝ・∀・⊗ は入っておらず、品詞 `symbol` 自体を廃止したので、`validate.py` が記号の行をエラーとして弾きます。ギリシャ文字を含む語はカタカナで表記しています（ラムダ計算、ベータ簡約、アルファ変換）。

> [!NOTE]
> 実際に動作確認したのは Google 日本語入力のみです。残る3形式は文字コード・BOM・改行コード・品詞名・plist の構造を検査しただけにとどまります。取り込みに失敗した場合は [Issue](../../issues) を立ててください。

> [!IMPORTANT]
> IME への取り込みは**追加**であり、削除する手段はありません。math-study ベースに作り直す前の版を取り込んでいる場合、その語は IME に残ったままで、再取り込みしても置き換わりません。IME 側で古い辞書を削除してから取り込んでください。

## 収録の基準

**math-study に現れること**、そして**地の文ではなく用語であること**の両方を満たす語を収録しています。`準同型` は 22 回現れるので収録し、`存在` は 58 回現れますが日常語を日常の意味で使っているだけなので収録しません。用語でないと判断した文字列は [`terms/.rejected`](terms/.rejected) に記録してあり、同じ判断を二度しなくて済むようにしてあります。

**正しい読み**に対して用語を割り当てています。略語による入力は対応していません。日常語と衝突して通常の日本語入力を悪化させるためです。

複合語は全体と部分の両方を登録しています（`全射準同型` と `全射`・`準同型`）。長い語を一発で変換できるようにするためです。

## カタカナ語について

`ほもとぴー` から `ホモトピー` が出るのは、この辞書の働きではありません。IME は仮名入力をそのままカタカナに変換できるので、これらの項目は IME が元から出す候補と同じ文字列を返すだけです。**8 語**がこれに当たります（イデアル、グロタンディーク、シングルトン、ソート、ハウスドルフ、ホモトピー、レトラクト、アルファステップ）。件数だけ [REVIEW.md](REVIEW.md) の「IMEが自前で変換できる項目」に記載しています。

残る 169 語は実際に働きます。恒等射・冪等行列・局所的に小さい圏 のような漢字語、`グロタンディーク群`・`コンパクト開位相` のようなカタカナと漢字の混在、`Hom`・`well-defined` のようなラテン文字表記です。

## 語の追加方法

[`terms/`](terms/) が唯一の原本で、`dist/` 以下は生成物です。math-study に新しい章が増えたら次を実行してください。

```sh
python3 harvest.py            # ../math-study から候補を拾う
python3 validate.py           # 形式を検査し、REVIEW.md を再生成する
python3 build.py              # terms/ から dist/ を生成する
```

`harvest.py` は math-study の作業コピー（既定では `../math-study`、引数でパス指定も可）を読み、`terms/` にも `terms/.rejected` にも無い日本語文字列だけを表示します。採用するなら対応するファイルに行を足し、不採用なら `.rejected` に足してください。`--all` を付けると過去の判断も含めて全件を再提示します。

行はタブ区切りです。

```
読み <TAB> 単語 <TAB> 品詞 <TAB> フラグ（任意）
じゅんどうけい	準同型	noun
```

品詞は IME に依存しない値を使います（`noun`、`noun-suru`（する接続）、`noun-adj`（な接続）、`person`、`latin`）。各 IME の品詞体系への対応づけはビルド側で行います。分野はファイル名から決まるため、行ごとに書く必要はありません。フラグは任意で、`common`（読みが日常語と衝突する）と `low-confidence`（読みに確認が必要）をカンマ区切りで指定できます。

どちらも CI で実行されます。CI はさらに、コミットされている `dist/` が `terms/` から生成される内容と一致するかをチェックします。なお CI は math-study を clone **しません**。他リポジトリの HEAD にビルドを結び付けると、新しい章を書いただけでこちらのビルドが落ちるためです。

`validate.py` は「読みのモーラ数は単語の漢字数以上」という規則で略語を弾きますが、これは下限にすぎません。CI ではなく差分を確認してください。

日常語と衝突する語、および読みが未確認の語は [REVIEW.md](REVIEW.md) にまとめてあります。

## 注意事項

**語そのものは実在します。**すべて `.tex` から拾ったものなので、存在しない語が紛れ込むことはありません。**問題は読みです。**math-study にルビは無いため、読みは以前の版から引き継いだもの（81 語）か、生成したもの（96 語）のいずれかです。うち 17 語は `low-confidence` を付けて [REVIEW.md](REVIEW.md) に挙げてあります。特に怪しいのはラテン文字の作用素名で、`Ob`・`Mor`・`dom`・`cod`・`Proj` には定まった日本語の読みがありません。

読みの誤りはその項目が変換候補に出てこないだけですが、見かけたら不具合です。[Issue](../../issues) を立てるか、該当行を直してください。

## ライセンス

[CC0 1.0](LICENSE)（パブリックドメイン）。用語とその読みの一覧にすぎません。
