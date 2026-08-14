# 憲章（charter）

各プロジェクトで守る開発ルール。[doc-rule.md](./doc-rule.md) 参照。  
改訂はあり得るが、**`_archived` へは移さない**（履歴は git または版注記）。

各プロジェクトでは本リポジトリの内容を `docs/charter/` に置く。プロダクト固有の上書きがある場合は、そのプロジェクトの docs に別ファイルで明示する。

| 文書 | 内容 |
|------|------|
| [tdd.md](./tdd.md) | TDD 方針（氷山パターン、テスト仕様書） |
| [thin-ddd.md](./thin-ddd.md) | 薄い DDD（Controller / Service / Repository / Validation） |
| [git-rule.md](./git-rule.md) | git の運用について |
| [versioning-rule.md](./versioning-rule.md) | バージョンの運用方法について |
| [doc-rule.md](./doc-rule.md) | ドキュメント運用方針 |
| README.md | 本ドキュメント |

プロダクト要件の正本は、各プロジェクトの `docs/main.md` および `docs/specs/` とする。憲章には詰め込まない。

## 適用範囲

### すべてのプロジェクト

- TDD
- Gitルール
- バージョニングルール
- ドキュメントルール

### Webアプリケーション / デスクトップアプリケーション

- 薄いDDD

### CLI、パッケージ、ブラウザ拡張

- 薄いDDDは意識しつつ、CRUDを伴わないものはCRUD Traitを採用しなくとも良い。

### 例外

開発初期状態などは、憲章に沿わない状態を許容する。POが適宜判断。
バージョンを重ねるうちに整えていく。

## GitHub / Gitea 等の Issue や Project について

- 開発時は、LLMとの親和性を考え、`docs/`ベースの記述・開発で良い。
- 開発が進むと、複雑化するため、仕様は`docs/`に残しつつ、実装課題やTODOは、Issueを活用していく。
- ただし、Wikiは用いない。（仕様はコードリポジトリを正とするため）


----

以上
