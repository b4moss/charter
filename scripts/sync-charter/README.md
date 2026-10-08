# charter sync

`docs/charter/` を、固定リスト（`targets.yaml`）の各リポジトリへ配布し、PR を作成するツールです。

## トリガー

GitHub Actions ワークフロー: [`.github/workflows/sync-charter.yml`](../../.github/workflows/sync-charter.yml)

| トリガー | 動作 |
|---------|------|
| Release `published` | そのタグの `docs/charter/` を全ターゲットへ同期して PR 作成 |
| `workflow_dispatch` | 指定タグ/ref で手動実行（dry-run / forge 限定可） |

## Secrets / Vars

Repository secrets（`b4moss/charter`）:

| Name | 必須 | 説明 |
|------|------|------|
| `SYNC_GITHUB_TOKEN` | GitHub 向け | 全 GitHub ターゲットに `contents:write` と `pull_requests:write` がある PAT または GitHub App token |
| `SYNC_GITEA_TOKEN` | Gitea 向け | `git.b4m.jp` で write + PR 可能な token |

Optional repository variable:

| Name | Default | 説明 |
|------|---------|------|
| `SYNC_GITEA_URL` | `https://git.b4m.jp` | Gitea ベース URL |

## ターゲット追加

`targets.yaml` に追記する。

```yaml
github:
  - repo: b4moss/example
    base: main

gitea:
  - repo: b4m-inner/example
    base: develop   # main が無い場合のみ
```

- `base` は原則 `main`
- `main` が存在しないリポジトリだけ `develop` を使う

## ローカル実行

```bash
pip install pyyaml
export SYNC_GITHUB_TOKEN=...
export SYNC_GITEA_TOKEN=...

# 変更なし確認
python3 scripts/sync-charter/sync.py \
  --version v1.3.0 \
  --dry-run

# 本番相当
python3 scripts/sync-charter/sync.py \
  --version v1.3.0
```

## 動作概要

1. 正本の `docs/charter/` を各リポへコピー（既存は削除して置換）
2. 上書き前に、既知の `v*` タグ内容と照合してローカル改変を検出
3. ブランチ `update-charter-<version>` を force-push
4. ベースブランチ向け PR を作成（既存があれば再利用）
5. サマリとローカル改変 JSON を Artifact / Job Summary に出力

各プロダクト側で charter を改変しない方針のため、検出された差分は正本で上書きされます。改変内容は PR 本文と Artifact に残ります。
