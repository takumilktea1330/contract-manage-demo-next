# API作業パッケージ

このディレクトリには、全15 APIの詳細な作業パッケージが含まれています。

## 📦 作業パッケージ一覧

### Phase 1: 認証API（2ファイル）

| ファイル | API | 説明 |
|---------|-----|------|
| `phase1_auth_signin.md` | POST /api/auth/signin | ログイン |
| `phase1_auth_signout.md` | POST /api/auth/signout | ログアウト |

### Phase 2: 契約管理API（6ファイル）

| ファイル | API | 説明 |
|---------|-----|------|
| `phase2_contracts_list.md` | GET /api/contracts | 契約一覧取得 |
| `phase2_contracts_get.md` | GET /api/contracts/[id] | 契約詳細取得 |
| `phase2_contracts_create.md` | POST /api/contracts | 契約作成 |
| `phase2_contracts_update.md` | PUT /api/contracts/[id] | 契約更新 |
| `phase2_contracts_delete.md` | DELETE /api/contracts/[id] | 契約削除 |
| `phase2_contracts_search.md` | POST /api/contracts/search | 契約検索 |

### Phase 3: アップロード・処理API（4ファイル）

| ファイル | API | 説明 |
|---------|-----|------|
| `phase3_upload.md` | POST /api/upload | ファイルアップロード |
| `phase3_upload_status.md` | GET /api/upload/[jobId] | アップロード状態取得 |
| `phase3_ocr.md` | POST /api/ocr | OCR処理 |
| `phase3_extraction.md` | POST /api/extraction | LLM情報抽出 |

### Phase 4: AI機能API（3ファイル）

| ファイル | API | 説明 |
|---------|-----|------|
| `phase4_rag_search.md` | POST /api/rag | RAG検索 |
| `phase4_analysis.md` | POST /api/analysis | AI契約分析 |
| `phase4_rentroll.md` | POST /api/rentroll | レントロール生成 |

## 📋 各作業パッケージの構成

各ファイルには以下のセクションが含まれています：

- **A. 目的・スコープ**: 何を実現するか、MVPの範囲、成功条件
- **B. 仕様**: API仕様（エンドポイント、リクエスト/レスポンス、エラー定義）
- **C. データ設計**: Prismaクエリ、トランザクション
- **D. 非機能要件**: 性能目標、レート制限、セキュリティ、ログ
- **E. 開発ルール**: コーディング規約、PR運用、環境設定
- **F. 連携仕様**: 外部サービス（AWS/OpenAI等）、内部連携
- **開発フロー**: Step 0-5の詳細実装手順
- **チケット詳細**: 受け入れ条件、影響範囲、サンプルコード

## 🚀 使い方

### 1. 担当APIの作業パッケージを確認

```bash
# Phase 1のログインAPIを確認
cat work-packages/phase1_auth_signin.md

# Phase 3のアップロードAPIを確認
cat work-packages/phase3_upload.md
```

### 2. 開発の進め方

1. 作業パッケージを熟読（1〜2時間）
2. 開発環境をセットアップ
3. Step 0-5の開発フローに従って実装
4. 受け入れ条件を確認しながらテスト
5. PRを作成してレビュー依頼

### 3. 並行開発

各APIは独立しているため、複数人で並行開発が可能です。

詳細な作業分担計画は `/docs/api/API開発_作業分担計画.md` を参照してください。

## 📊 進捗管理

実装状況は `/docs/api/API実装状況.md` で管理しています。

## 🔗 関連ドキュメント

- [API開発ロードマップ](../docs/api/API開発ロードマップ.md) - 全体像と開発順序
- [API実装状況](../docs/api/API実装状況.md) - 実装進捗
- [API開発_作業分担計画](../docs/api/API開発_作業分担計画.md) - チーム分担
- [要件定義書](../docs/requirements/要件定義書.md) - 機能要件
- [システム設計書](../docs/design/システム設計書.md) - アーキテクチャ

---

**作成日**: 2025-12-17
**更新日**: 2025-12-17
