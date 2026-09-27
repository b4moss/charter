# 合同会社 知的・自転車　プロジェクト開発憲章

このリポジトリは、合同会社 知的・自転車で開発を行うリポジトリにおける、開発憲章です。

共有する正本は **`main` ブランチの `docs/`** です（OKF v0.1）。かつての `docs` 専用ブランチは使わず、プロダクトは `main` 上の `docs/` を取り込みます。

- 取り込みは `git merge` / `git subtree` / `git submodule` のいずれでもよい（PO が判断）。
- 取り込まれた先では、各プロダクトによって文言やディレクトリ構造の修正を許容します。
- 取り込まれた先からこのリポジトリへの push は、原則として行いません。

## 取り込み方（例）

```shell
# charter を取り込みたい先の git root にて
git remote add charter https://github.com/b4moss/charter.git
git fetch charter main

# 方式 A: main をマージ（共有対象は docs/。ルートの README/LICENSE は競合し得る）
git merge charter/main --allow-unrelated-histories

# 方式 B: docs/ だけ subtree で取り込む
git subtree add --prefix=docs charter main --squash
# （既に docs/ がある場合は add ではなく pull を使う）

# 方式 C: submodule として追加し、必要なら docs/ を参照・同期する
git submodule add https://github.com/b4moss/charter.git vendor/charter
```

詳細な共有方針は [`docs/charter/README.md`](docs/charter/README.md)。OKF の定義と執筆サンプルは [`docs/charter/okf/`](docs/charter/okf/)。

# charter の内容について

- 憲章本文・OKF・ルール類はすべて `docs/` 配下で管理する。
- リポジトリルートの `README.md` / `LICENSE` はこのリポジトリ自体の説明用である。

# ライセンス

このリポジトリは、**MIT LICENSE** によって提供されます。

----

以上

----

Copyright 2026 [Bicycle for Mind LLC.](https://b4m.co.jp/)
