# 薄いDDD

`薄いDDD`とは、合同会社 知的・自転車で採用されている、軽量な開発方針である。

プロダクト仕様・ディレクトリ対応: [main.md](../main.md)（とくに §4.1）  
ユースケース一覧: [usecase.md](../specs/usecase.md)  
テスト方針: [tdd.md](./tdd.md)

## DDDとは

ここでいう`DDD`とは、`ドメイン駆動開発`のことである。

一方、このドメイン駆動開発をベースとした**クリーンアーキテクチャ**というものもある。

しかしクリーンアーキテクチャは肥大になりがちであり、小規模から中規模の開発では足かせになることが多い。

そこで、`DDD`をベースに、肥大にならないよう必要最低限の抽象化を行う開発方式を`薄いDDD(Thin DDD)`と呼称する。

## 薄いDDDの考え方

`薄いDDD`では、DDDの原則と同じく、以下の三層に分ける。

- `Controller層`
- `Service層`
- `Repository層`

本プロジェクトではこれに加え、Controller から呼ぶ **`Validation層`** を置く（[main.md §4.1](../main.md)）。

ディレクトリは概ね次のとおり（詳細は [main.md §4.1](../main.md)）:

`app/src/{config,http,controllers,services,repositories,validations,lib,jobs,views,db,types}/`  
`app/{migrations,scripts,data,frontend,public}/`（`vite.config.ts` は `app/`）

`views/` は **Twig（`.twig`）**。Controller は描画ヘルパ経由でのみ HTML を返し、テンプレ文字列を直書きしない。  
フロントの htmx 等は **Vite でセルフホスト**（[main.md §4](../main.md)）。

## Controller層

`Controller層`は、ユースケースと一対である。ユースケースは、特段の事情がない限り、**主語、述語、目的語**(RDF的な考え方)で表現されるべきである。

したがって、Controller層は、ユースケースを体現する命名とする。

例: ユーザーのサインアップ
- Should be: `UserSignupAccountController()`等。アクターと動詞、目的語で表現される。
- Not should be: `Signup()`　これは具体性を書く。

本プロジェクト例:
- `UserAddManualEntryController`（手動URL + スター）
- `UserListRecentTopicsController`
- `UserOpenEntryController`
- `UserStarEntryController`
- `SystemFetchFeedController`（タイマー起点の取得ユースケース）

Controller層の責務は、ユースケースの実現であり、ここで具体的な処理は行わない。行うのは

- `Validation層`の呼び出し
- `Service層`の呼び出し

であり、すべてのユースケースは、これらに統合されている必要がある。

### ルーティングとの対応（Hono 等）

**1ユースケース ⟷ 1コントローラー ⟷ 1ルート** とする。

- 1つの HTTP ルート（またはジョブ入口）が、ちょうど1つの Controller だけを呼ぶ
- 1つの Controller が、複数ルートから共有されない
- ルートハンドラ内にビジネスロジックや複数ユースケースの分岐を書かない（委譲のみ）

例（イメージ）:

- `POST /feeds` → `UserAddFeedController`
- `POST /feeds/:id/fetch` → `UserFetchFeedController`
- `GET /topics/recent` → `UserListRecentTopicsController`

ジョブ（タイマー）も同様に、1ジョブ入口 ⟷ 1 System Controller。

## Service層

`Service層`は、CRUDを伴わないビジネスロジックの記述層である。

当該アプリケーションの責務外のサービスやライブラリとの接続もここで行う。（APIやSDK等）

ここでの命名も、`UserSignupAccountService()`等が適切である。


## Repository層

各ユースケースに対する、データの永続化を責務とする。

基本的なCRUDは、共通ユーティリティ（`CrudRepository` 等）として外出ししておき、ユースケース／ドメイン Repository から使用する。

**ドメイン Repository（例: `FeedRepository`）は SQL を DB に直書きしない。** 必ず共通 CRUD ユーティリティ経由とする。  
これにより、インメモリ／テスト用 SQLite 上の CRUD ユーティリティ DBテストが、永続化品質の担保になる。

当然、ユースケースによっては、JOINやトランザクションが発生するケースもあるため、その処理もこの箇所（Repository 層）の責務であり。

その場合は、共通ユーティリティの拡張、または Repository 層内の専用メソッドとして、**やはり生の散在 SQL ではなく層の規律を保って**実装する。

[tdd.md](./tdd.md) の DBテストは、**この層のみ**インメモリ（またはテスト用SQLite）で担保する。

### DB層の抽象化

少なくとも、以下の処理は抽象化されているべきである。

- Read
- List
- Create
- Update
- Delete
- bulkCreate
- bulkUpdate
- bulkDelete
- Duplicate
- Search
  - カラムの指定が可能
  - クエリの指定が可能
  - 一般的な条件の指定が可能（`eq`,`lg`,`gt`など）
  - それらが複合して検索できること 

**現在進行中** : [b4moss/crudian](https://github.com/b4moss/crudian)にて、PHP/Node.js/Bun/Goの各ライブラリが開発中。

----

以上
