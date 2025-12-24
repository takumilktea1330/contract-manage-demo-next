# 契約管理アプリケーション

AI支援による不動産賃貸契約管理システム（Next.js 15 + React 19 + TypeScript + Prisma）

## 📋 プロジェクト概要

不動産賃貸契約の管理を効率化するためのフルスタックWebアプリケーションです。

### 主な機能

- 📄 **契約書アップロード**: PDF契約書をOCR + AI抽出で自動データ化
- 🔍 **AI契約検索**: 自然言語による高精度な契約検索（RAG）
- 📊 **AI契約分析**: Text-to-SQLによる統計・集計分析
- ✅ **契約検証**: AI抽出結果の確認・修正ワークフロー
- 📅 **期限管理**: 契約満了日のカレンダー表示・アラート
- 📋 **レントロール**: Excel/CSV/PDF形式でのレポート出力

---

## 🚀 クイックスタート

### 必要な環境

- Node.js 18以上
- npm 9以上
- SQLite（開発環境）/ PostgreSQL（本番環境）

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/your-org/contract-manage-demo-next.git
cd contract-manage-demo-next/app

# 依存パッケージをインストール
npm install

# 環境変数を設定
cp .env.example .env.local
# .env.local を編集

# データベースをセットアップ
npx prisma generate
npx prisma migrate dev
npx prisma db seed

# 開発サーバーを起動
npm run dev
```

### アクセス

- **ローカル**: http://localhost:3001
- **デフォルトログイン**:
  - Email: `admin@example.com`
  - Password: `password123`

---

## 📁 プロジェクト構造

```
contract-manage-demo-next/
├── app/                          # Next.jsアプリケーション
│   ├── (auth)/                   # 認証画面
│   ├── (dashboard)/              # ダッシュボード機能
│   ├── api/                      # API Routes
│   ├── components/               # Reactコンポーネント
│   ├── lib/                      # ユーティリティ
│   ├── prisma/                   # Prismaスキーマ・マイグレーション
│   └── stores/                   # Zustand状態管理
│
├── docs/                         # ドキュメント
│   ├── requirements/             # 要件定義書
│   ├── design/                   # システム設計書
│   ├── api/                      # API仕様・ロードマップ
│   ├── guides/                   # 開発ガイド
│   └── reports/                  # 分析レポート
│
├── work-packages/                # API作業パッケージ（全15 API）
│   ├── phase1_*.md               # Phase 1: 認証API
│   ├── phase2_*.md               # Phase 2: 契約管理API
│   ├── phase3_*.md               # Phase 3: アップロード・処理API
│   └── phase4_*.md               # Phase 4: AI機能API
│
└── references/                   # 参考資料
    ├── api-dev-docs.txt          # API開発ベストプラクティス
    └── git運用ルール.txt         # Git運用ルール
```

---

## 🛠️ 技術スタック

### フロントエンド
- **Next.js 15.5.4** - App Router, Server Components
- **React 19** - 最新React
- **TypeScript 5.9** - 型安全性
- **Tailwind CSS 3.4** - スタイリング
- **Zustand 5.0.9** - 状態管理

### バックエンド
- **Next.js API Routes** - RESTful API
- **Prisma 5.22.0** - ORM
- **NextAuth.js 4.24.13** - 認証
- **SQLite / PostgreSQL** - データベース

### AI・外部サービス
- **OpenAI API** - GPT-4, Embeddings（RAG検索）
- **Claude API** - 情報抽出（オプション）
- **Amazon Textract** - OCR処理
- **AWS S3** - ファイルストレージ

### 開発ツール
- **ESLint + Prettier** - コード品質
- **GitHub Actions** - CI/CD
- **Docker Compose** - PostgreSQL（オプション）

---

## 📚 ドキュメント

### 要件・設計
- [要件定義書](docs/requirements/要件定義書.md) - 機能要件・非機能要件
- [システム設計書](docs/design/システム設計書.md) - アーキテクチャ・DB設計

### API開発
- [API開発ロードマップ](docs/api/API開発ロードマップ.md) - 全15 APIの開発計画
- [API実装状況](docs/api/API実装状況.md) - 実装進捗管理
- [API開発_作業分担計画](docs/api/API開発_作業分担計画.md) - チーム作業分担
- [作業パッケージ一覧](work-packages/README.md) - 各APIの詳細仕様

### 開発ガイド
- [GIT運用ガイド](docs/guides/GIT運用ガイド.md) - Git/GitHubの使い方
- [PostgreSQL移行ガイド](docs/guides/PostgreSQL移行ガイド.md) - SQLite → PostgreSQL
- [デプロイメントガイド](docs/guides/DEPLOYMENT.md) - 本番環境へのデプロイ

### レポート
- [実装整合性分析レポート](docs/reports/実装整合性分析レポート.md) - 実装状況の分析
- [改善完了レポート](docs/reports/改善完了レポート.md) - 改善履歴
- [レビュー対応状況](docs/reports/レビュー対応状況.md) - コードレビュー対応

---

## 🎯 開発フェーズ

### Phase 1: 基盤構築 ✅
- [x] データベースセットアップ（Prisma + SQLite）
- [x] NextAuth.js認証
- [x] シードデータ作成

### Phase 2: 契約管理API ✅
- [x] 契約CRUD API（5エンドポイント）
- [x] 契約検証API
- [x] 統計情報API

### Phase 3: アップロード・処理API 🚧
- [ ] ファイルアップロード（AWS S3）
- [ ] OCR処理（Amazon Textract）
- [ ] LLM情報抽出（OpenAI/Claude）

### Phase 4: AI機能API 📅
- [ ] RAG検索（OpenAI Embeddings + pgvector）
- [ ] AI契約分析（Text-to-SQL）
- [ ] レントロール生成（Excel/CSV/PDF）

進捗状況は [API実装状況](docs/api/API実装状況.md) を参照してください。

---

## 🤝 コントリビューション

このプロジェクトへの貢献を歓迎します。

### 開発の進め方

1. [GIT運用ガイド](docs/guides/GIT運用ガイド.md) を読む
2. 作業ブランチを作成（`feat/your-feature`）
3. [作業パッケージ](work-packages/) から担当APIを選択
4. 実装・テスト
5. Pull Requestを作成

詳細は [CONTRIBUTING.md](app/.github/CONTRIBUTING.md) を参照してください。

---

## 🔒 セキュリティ

- パスワードは bcrypt でハッシュ化
- JWT セッション管理（NextAuth.js）
- API認証・認可チェック
- 監査ログ記録
- 入力バリデーション

セキュリティ上の問題を発見した場合は、直接報告してください。

---

## 📊 進捗状況

| カテゴリ | API数 | 実装済み | 進捗率 |
|---------|------|---------|--------|
| 認証 | 2 | 2 | 100% |
| 契約管理 | 6 | 6 | 100% |
| アップロード・処理 | 4 | 0 | 0% |
| AI機能 | 3 | 0 | 0% |
| **合計** | **15** | **8** | **53%** |

※最新の進捗は [API実装状況](docs/api/API実装状況.md) を参照

---

## 📄 ライセンス

このプロジェクトはデモンストレーション用です。

---

## 🙋 サポート

- **技術的な質問**: GitHub Issues
- **ドキュメント**: [docs/](docs/) ディレクトリ
- **作業パッケージ**: [work-packages/](work-packages/) ディレクトリ

---

**作成日**: 2025-12-17
**最終更新**: 2025-12-17
