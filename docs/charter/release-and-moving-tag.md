---
okf_version: "0.1"
type: Charter
title: リリースと移動タグ v1
description: VERSION・SemVer タグ・メジャー移動タグ v1 の運用方針。
tags: [charter, versioning]
timestamp: 2026-10-23
---

# リリースと移動タグ `v1`

## VERSION と Git タグ

| もの | 形式 | 例 |
|---|---|---|
| ルート `VERSION` ファイル | `v` 無し | `1.4.0` |
| Git タグ / GitHub Release | `v` 付き | `v1.4.0` |

リリース手順（要約）:

1. `VERSION` を上げる（このファイルと一致させる）
2. 変更を `main` にマージ（レビュー後）
3. `vX.Y.Z` タグを打って GitHub Release を作る
4. メジャーが同じなら移動タグ **`v1`** をそのコミットへ更新する

## 移動タグ `v1`（PO 承認済み方針）

- 各リポの `AGENTS.md` ポインタは **`v1` を指す**（完全固定の `v1.4.0` ではない）。
- MINOR/PATCH リリースでは `v1` を新しい `v1.Y.Z` に動かして全リポへ反映する。
- MAJOR（`v2`）に上げるときだけ、各リポのポインタ更新が必要。
- **`v1` タグの実作成・移動は、PR マージ後に PO（こうきさん）の明示指示を待って行う。** エージェントは勝手に打たない。

## 過去の不整合（記録と解消）

調査時点（2026-10-23）の事実:

| 項目 | 状態 |
|---|---|
| ルート `VERSION` | `1.2.0` のまま残存していた |
| 最新 GitHub Release | `v1.3.0`（2026-10-08） |
| タグ `v1.3.0` のツリー | `scripts/sync-charter/` **無し**（sync はタグ後に `main` へ入った） |
| ブランチ名 `v1.4.0` | タグ名と衝突し得るため `release/v1.4.0` へ改名 |

解消方針（本リリース `1.4.0`）:

1. **`VERSION` を `1.4.0` に合わせる**（このブランチ）。以後、Release 作成時は必ず `VERSION` とタグを同期する。
2. **`v1.3.0` を遡って書き換えない**（タグの force はしない）。sync-charter が無いのは歴史的事実として残す。配信機械は `b4m-inner/charter-ops` へ移す（公開側削除は別 PR）。
3. 構造変更（`docs/charter/tech/`）に伴う旧パスリンクは本 PR で修正する。

## 参照

- バージョン付けの詳細: [`tech/versioning-rule.md`](tech/versioning-rule.md)
- エージェント向け要約: [`agent-brief.md`](agent-brief.md)
