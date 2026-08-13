# 合同会社 知的・自転車　プロジェクト開発憲章

このリポジトリは、合同会社 知的・自転車で開発を行うリポジトリにおける、開発憲章です。

- 当リポジトリは、`git merge`機能によって、各リポジトリに取り込まれることを想定しています。
  - 状況に応じて`git subtree`や`git submodule`でもいいでしょう。 
- 取り込まれた先では、各プロダクトによって文言やディレクトリ構造の修正を許容します。
- 取り込まれた先からこのリポジトリへのpushは、原則として行いません。

## 取り込み方
```shell
# charterを取り込みたい先のgit rootにて
git remote add charter https://github.com/b4moss/charter.git
git merge charter/docs --allow-unrelated-histories

# charterリポジトリのdocsブランチが取り込まれます
```

# charterの内容について
全ては`docs`ブランチで管理します。
mainブランチは、README.mdとLICENCEしか置きません。

# ライセンス

このリポジトリは、**MIT LICENSE** によって提供されます。

----

以上

----

Copyright 2026 [Bicycle for Mind LLC.](https://b4m.co.jp/)