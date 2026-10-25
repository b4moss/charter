---
okf_version: "0.1"
type: AgentBrief
title: エージェント向け憲章要約
description: 作業開始時に読む要約。詳細は正本リンクへ。
tags: [charter, agent]
timestamp: 2026-10-25
---

# エージェント向け憲章要約（agent-brief）

このファイルは **要約**です。判断に迷ったら推測せず、下の正本を開くこと。

## 正本（このリポジトリ）

| 用途 | URL（移動タグ `v1`） |
|---|---|
| 索引 | https://raw.githubusercontent.com/b4moss/charter/v1/docs/charter/index.md |
| 憲章本体 | https://raw.githubusercontent.com/b4moss/charter/v1/docs/charter/README.md |
| 技術系索引 | https://raw.githubusercontent.com/b4moss/charter/v1/docs/charter/tech/index.md |
| 文書ルール | https://raw.githubusercontent.com/b4moss/charter/v1/docs/charter/doc-rule.md |

リポジトリ: https://github.com/b4moss/charter  
`v1` タグがまだ無い場合は、指示された ref（例: `main` / `release/v1.4.0`）に読み替える。

## 版の読み方

1. ポインタはメジャー移動タグ **`v1`** を指す（MINOR/PATCH では各リポのポインタを更新しない）。
2. 作業開始時に要約を **毎回取得**する（キャッシュに頼らない）。
3. PR 本文の先頭に次を 1 行書く。`VERSION` ファイルの値と、読んだ**コミット**の SHA 先頭 7 桁を書く（タグオブジェクトの SHA ではなく、そのタグが指すコミットの SHA）。  
   例: `charter: 1.4.1 (abc1234)`
4. `VERSION` はリポジトリルートの [`VERSION`](../../VERSION) ファイル。Git タグは `v` 付き（`v1.4.1`）。
5. 取得できない／版が読めない場合は **推測で進めず停止して報告**する。

## 守ること（要約）

- **憲章が最上位。** リポ固有の例外だけ `docs/override-charter.md` が優先（その範囲のみ）。
- **TDD / 薄い DDD:** 氷山パターン。Repository 層以外で DB に依存したテストを増やさない。詳細は `tech/tdd.md` / `tech/thin-ddd.md`。
- **Git:** 機能は短命ブランチ → PR。`main` へ直接 push しない。詳細は `tech/git-rule.md`。
- **バージョン:** SemVer。タグと `VERSION` を一致させる。詳細は `tech/versioning-rule.md`。
- **CI/CD:** PR で CI。本番 CD は保護された経路のみ。詳細は `tech/ci-cd.md`。
- **ドキュメント:** 置き場とライフサイクルは `doc-rule.md`（OKF）。

## やってはいけないこと（要約）

- 憲章コピーを勝手に改変して「正本」扱いすること
- 取得失敗時に憲章内容を推測して続行すること
- 指示されていない本番デプロイ・全リポ配信・タグの無断移動

## 作業の進め方（推奨）

1. この要約を取得する  
2. 作業に関係する個別文書だけ正本から読む  
3. リポの `docs/override-charter.md` があれば読む  
4. 実装・PR。PR 本文に `charter:` 行
