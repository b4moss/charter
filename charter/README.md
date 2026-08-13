# 憲章（charter）

このプロジェクトで守る開発ルール。[doc_rule.md](../doc_rule.md) 参照。  
改訂はあり得るが、**`_archived` へは移さない**（履歴は git または版注記）。

| 文書 | 内容 |
|------|------|
| [tdd.md](./tdd.md) | TDD 方針（氷山パターン、テスト仕様書） |
| [thin-ddd.md](./thin-ddd.md) | 薄い DDD（Controller / Service / Repository / Validation） |
| [git-rule.md](./git-rule.md) | gitの運用について） |
| [versioning-rule.md](./versioning-rule.md) | バージョンの運用方法について |
| [doc-rule.md](./doc-rule.md) | ドキュメント運用方針 |
| README.md | 本ドキュメント |

プロダクト要件の正本は [../main.md](../main.md) / [../specs/usecase.md](../specs/usecase.md)。

# 適用範囲

## すべてのプロジェクト

- TDD
- Gitルール
- バージョニングルール
- ドキュメントルール

## Webアプリケーション / デスクトップアプリケーション

- 薄いDDD

## CLI、パッケージ、ブラウザ拡張

- 薄いDDDは意識しつつ、CRUDを伴わないものはCRUD Traitを採用しなくとも良い。

## 例外

開発初期状態などは、憲章に沿わない状態を許容する。POが適宜判断。
バージョンを重ねるうちに整えていく。


----

以上