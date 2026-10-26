# 合同会社 知的・自転車　プロジェクト開発憲章

このリポジトリは、合同会社 知的・自転車で開発を行うリポジトリにおける、開発憲章です。

共有する正本は **`main` ブランチの `docs/`** です（OKF v0.1）。かつての `docs` 専用ブランチは使いません。

## 各リポでの参照方法

各プロダクトリポは憲章本文をコピーせず、移動タグ **`v1`** を参照します。

- 各リポの `AGENTS.md` に「## 開発憲章（charter）」節を置く。
- その節から、本リポの `v1` 上の [`agent-brief.md`](https://raw.githubusercontent.com/b4moss/charter/v1/docs/charter/agent-brief.md)（要約）と [`index.md`](https://raw.githubusercontent.com/b4moss/charter/v1/docs/charter/index.md)（詳細の入口）を参照する。
- リポ固有の上書きがある場合は `docs/override-charter.md` に書く（憲章に反する場合はその範囲のみ優先）。
- リポ内に `docs/charter/` のコピーは置かない。

節の文面の例:

```markdown
## 開発憲章（charter）
- 最上位の憲章はこのリポの外にあります。作業を始める前に必ず読むこと（毎回、キャッシュに頼らず取得）。
  1. 要約: https://raw.githubusercontent.com/b4moss/charter/v1/docs/charter/agent-brief.md
  2. 詳細（必要な文書だけ）: https://raw.githubusercontent.com/b4moss/charter/v1/docs/charter/index.md
- 参照する版: `v1`（メジャー版）。PR 本文の先頭に、読んだ VERSION とコミット SHA 先頭 7 桁を 1 行で書くこと。例: `charter: 1.4.2 (abc1234)`
- 取得できない場合は、推測で進めず作業を止めて報告すること。
- このリポ固有の上書きは `docs/override-charter.md` を優先する（憲章に反する場合はその範囲のみ）。
```

**`v1` タグの作成・移動は PO の明示指示後**（マージ後に実施。エージェントは打たない）。

憲章本文: [`docs/charter/`](docs/charter/)。  
エージェント向け要約: [`docs/charter/agent-brief.md`](docs/charter/agent-brief.md)。  
版と移動タグ `v1`: [`docs/charter/release-and-moving-tag.md`](docs/charter/release-and-moving-tag.md)。

# charter の内容について

- 憲章本文・ルール類はすべて `docs/` 配下で管理する。
- リポジトリルートの `README.md` / `LICENSE` はこのリポジトリ自体の説明用である。

# ライセンス

このリポジトリは、**MIT LICENSE** によって提供されます。

----

以上

----

Copyright 2026 [Bicycle for Mind LLC.](https://b4m.co.jp/)
