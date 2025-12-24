# API開発ロードマップ

**作成日**: 2025-12-17
**対象**: 契約管理APP バックエンドAPI開発

このドキュメントでは、開発すべきAPI一覧を優先度順に整理し、実装手順を示します。

---

## 📋 目次

1. [開発すべきAPI全体像](#開発すべきapi全体像)
2. [フェーズ1: 基盤構築（必須）](#フェーズ1-基盤構築必須)
3. [フェーズ2: 契約管理機能](#フェーズ2-契約管理機能)
4. [フェーズ3: アップロード・処理機能](#フェーズ3-アップロード処理機能)
5. [フェーズ4: AI機能](#フェーズ4-ai機能)
6. [各APIの詳細仕様](#各apiの詳細仕様)

---

## 開発すべきAPI全体像

### 📊 進捗状況

| カテゴリ | API数 | 実装済み | 未実装 | 進捗率 |
|---------|-------|---------|--------|--------|
| 認証 | 2 | 0 | 2 | 0% |
| 契約管理 | 5 | 0 | 5 | 0% |
| アップロード・処理 | 4 | 0 | 4 | 0% |
| RAG検索 | 1 | 0 | 1 | 0% |
| AI分析 | 1 | 0 | 1 | 0% |
| レントロール | 1 | 0 | 1 | 0% |
| **合計** | **14** | **0** | **14** | **0%** |

---

## フェーズ1: 基盤構築（必須）

このフェーズを完了しないと、他のAPIは動作しません。

### ✅ 1.1 データベースセットアップ

#### タスク
- [ ] Prismaスキーマの実装
- [ ] PostgreSQLデータベースの作成
- [ ] マイグレーション実行
- [ ] シードデータ作成（テスト用）

#### ファイル
- `prisma/schema.prisma` - データベーススキーマ
- `prisma/seed.ts` - シードデータ

#### 所要時間
約2-3時間

#### 参考
システム設計書 3章「データベース設計」

---

### ✅ 1.2 認証API

認証がないと、すべてのAPIが使えません。

#### API一覧

##### 1. POST /api/auth/signin
**優先度**: 🔴 最高

**説明**: ログイン

**ファイル**: `app/api/auth/[...nextauth]/route.ts`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "user": {
    "id": "user_xxx",
    "email": "user@example.com",
    "name": "山田太郎",
    "role": "USER"
  },
  "token": "jwt_token_xxx"
}
```

**実装内容**:
- NextAuth.js統合
- bcryptでパスワードハッシュ検証
- JWTトークン発行

**所要時間**: 2-3時間

---

##### 2. POST /api/auth/signout
**優先度**: 🟡 中

**説明**: ログアウト

**ファイル**: `app/api/auth/[...nextauth]/route.ts`

**実装内容**:
- セッション削除
- トークン無効化

**所要時間**: 30分

---

### ✅ 1.3 環境変数設定

**ファイル**: `app/.env.local`

```env
# データベース
DATABASE_URL="postgresql://user:password@localhost:5432/contract_manage"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-here"

# AWS（後で設定）
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_REGION=
# AWS_S3_BUCKET=

# OpenAI（後で設定）
# OPENAI_API_KEY=
```

---

## フェーズ2: 契約管理機能

基本的なCRUD操作を実装します。

### ✅ 2.1 契約管理API

#### API一覧

##### 1. GET /api/contracts
**優先度**: 🔴 最高

**説明**: 契約一覧取得（ページネーション付き）

**ファイル**: `app/api/contracts/route.ts`

**Query Parameters**:
- `page`: ページ番号 (default: 1)
- `limit`: 取得件数 (default: 20, max: 100)
- `status`: 契約ステータス (ACTIVE | EXPIRED | TERMINATED)
- `type`: 契約種別 (RENTAL | RENEWAL | MEMORANDUM)
- `keyword`: キーワード検索

**Response**:
```json
{
  "data": [
    {
      "id": "contract_xxx",
      "contractNumber": "C-2025-001",
      "type": "RENTAL",
      "status": "ACTIVE",
      "verificationStatus": "VERIFIED",
      "startDate": "2025-01-01",
      "endDate": "2027-12-31",
      "propertyName": "東京オフィスビル 5F",
      "monthlyRent": 500000,
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "totalPages": 5
  }
}
```

**実装内容**:
- Prismaでデータ取得
- フィルタリング（status, type）
- キーワード検索（propertyName, contractNumber）
- ページネーション
- 認証チェック

**所要時間**: 2-3時間

---

##### 2. GET /api/contracts/[id]
**優先度**: 🔴 最高

**説明**: 契約詳細取得

**ファイル**: `app/api/contracts/[id]/route.ts`

**Response**:
```json
{
  "id": "contract_xxx",
  "contractNumber": "C-2025-001",
  "type": "RENTAL",
  "status": "ACTIVE",
  "verificationStatus": "VERIFIED",
  "startDate": "2025-01-01",
  "endDate": "2027-12-31",
  "renewalType": "自動更新",
  "noticePeriodMonths": 3,
  "pdfUrl": "https://s3.amazonaws.com/...",
  "pdfFileName": "contract.pdf",
  "details": {
    "propertyAddress": "東京都千代田区丸の内1-1-1",
    "propertyName": "東京オフィスビル 5F",
    "propertyArea": 120.5,
    "propertyUsage": "事務所",
    "monthlyRent": 500000,
    "deposit": 1500000,
    "keyMoney": 1000000,
    "managementFee": 50000,
    "confidenceScore": 0.95
  },
  "parties": [
    {
      "partyType": "LESSOR",
      "name": "株式会社丸の内不動産",
      "address": "東京都千代田区丸の内2-2-2",
      "phoneNumber": "03-1234-5678",
      "confidenceScore": 0.92
    },
    {
      "partyType": "LESSEE",
      "name": "株式会社サンプル商事",
      "address": "東京都港区赤坂1-1-1",
      "phoneNumber": "03-9876-5432",
      "confidenceScore": 0.98
    }
  ],
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-01-15T10:30:00Z",
  "verifiedAt": "2025-01-02T14:00:00Z",
  "verifiedBy": "user_yyy"
}
```

**実装内容**:
- Prismaで契約データ取得
- リレーション（details, parties）を含める
- 存在チェック（404処理）
- 認証チェック

**所要時間**: 1-2時間

---

##### 3. POST /api/contracts
**優先度**: 🟡 中

**説明**: 契約新規作成（手動入力用）

**ファイル**: `app/api/contracts/route.ts`

**Request**:
```json
{
  "contractNumber": "C-2025-100",
  "type": "RENTAL",
  "status": "ACTIVE",
  "startDate": "2025-04-01",
  "endDate": "2027-03-31",
  "renewalType": "自動更新",
  "noticePeriodMonths": 3,
  "details": {
    "propertyAddress": "東京都渋谷区...",
    "propertyName": "渋谷ビル 3F",
    "propertyArea": 85.0,
    "propertyUsage": "店舗",
    "monthlyRent": 300000,
    "deposit": 900000
  },
  "parties": [
    {
      "partyType": "LESSOR",
      "name": "不動産会社A",
      "address": "...",
      "phoneNumber": "..."
    }
  ]
}
```

**Response**:
```json
{
  "id": "contract_xxx",
  "contractNumber": "C-2025-100",
  "message": "契約が正常に作成されました"
}
```

**実装内容**:
- バリデーション（Zod）
- Prismaでトランザクション作成
- 重複チェック（contractNumber）
- 認証チェック

**所要時間**: 2-3時間

---

##### 4. PUT /api/contracts/[id]
**優先度**: 🟡 中

**説明**: 契約更新

**ファイル**: `app/api/contracts/[id]/route.ts`

**Request**:
```json
{
  "status": "ACTIVE",
  "details": {
    "monthlyRent": 550000
  }
}
```

**Response**:
```json
{
  "id": "contract_xxx",
  "message": "契約が正常に更新されました"
}
```

**実装内容**:
- 部分更新対応
- 更新履歴記録（AuditLog）
- バリデーション
- 認証・権限チェック

**所要時間**: 2-3時間

---

##### 5. DELETE /api/contracts/[id]
**優先度**: 🟢 低

**説明**: 契約削除

**ファイル**: `app/api/contracts/[id]/route.ts`

**Response**:
```json
{
  "message": "契約が正常に削除されました"
}
```

**実装内容**:
- ソフトデリート（論理削除）推奨
- 関連データも削除（CASCADE）
- 認証・権限チェック（管理者のみ）

**所要時間**: 1-2時間

---

##### 6. POST /api/contracts/search
**優先度**: 🟡 中

**説明**: 契約検索（通常検索）

**ファイル**: `app/api/contracts/search/route.ts`

**Request**:
```json
{
  "keyword": "渋谷",
  "filters": {
    "type": "RENTAL",
    "status": "ACTIVE",
    "startDateFrom": "2024-01-01",
    "startDateTo": "2025-12-31",
    "minRent": 100000,
    "maxRent": 1000000
  },
  "page": 1,
  "limit": 20
}
```

**Response**: GET /api/contracts と同じ形式

**実装内容**:
- 複合条件検索
- 金額範囲検索
- 日付範囲検索
- 全文検索（PostgreSQL Full-Text Search）

**所要時間**: 3-4時間

---

## フェーズ3: アップロード・処理機能

PDFアップロードとOCR・LLM処理を実装します。

**📦 作業パッケージ作成完了**: 2025-12-17
- `API開発作業パッケージ_Phase3.md` - 詳細な実装ガイド
- `API開発_作業分担計画.md` - チーム作業分担計画

### ✅ 3.1 アップロード・処理API

#### API一覧

##### 1. POST /api/upload
**優先度**: 🔴 最高

**説明**: PDFファイルアップロード

**ファイル**: `app/api/upload/route.ts`

**Request**: multipart/form-data
- `file`: PDFファイル（最大20MB）
- `contractType`: 契約種別（任意）

**Response**:
```json
{
  "jobId": "job_xxx",
  "fileName": "contract.pdf",
  "fileSize": 1048576,
  "status": "UPLOADING",
  "message": "アップロードが開始されました"
}
```

**実装内容**:
1. ファイル検証（PDF, サイズ）
2. AWS S3にアップロード（Presigned URL使用）
3. UploadJobレコード作成
4. 非同期処理キューに登録
5. 認証チェック

**依存サービス**:
- AWS S3

**所要時間**: 4-5時間

---

##### 2. GET /api/upload/status
**優先度**: 🔴 最高

**説明**: 処理状況取得（ポーリング用）

**ファイル**: `app/api/upload/status/route.ts`

**Query Parameters**:
- `jobId`: ジョブID（必須）

**Response**:
```json
{
  "jobId": "job_xxx",
  "fileName": "contract.pdf",
  "status": "OCR_PROCESSING",
  "progress": 45,
  "currentStep": "OCR",
  "errorMessage": null,
  "contractId": null,
  "createdAt": "2025-01-01T10:00:00Z",
  "updatedAt": "2025-01-01T10:05:30Z"
}
```

**ステータス一覧**:
- `UPLOADING` - アップロード中
- `UPLOADED` - アップロード完了
- `OCR_PROCESSING` - OCR処理中
- `OCR_COMPLETED` - OCR完了
- `EXTRACTING` - LLM抽出中
- `EXTRACTION_COMPLETED` - 抽出完了
- `FAILED` - 失敗
- `COMPLETED` - 完了

**実装内容**:
- UploadJobレコード取得
- 認証チェック（自分のジョブのみ）

**所要時間**: 1時間

---

##### 3. POST /api/ocr
**優先度**: 🟡 中

**説明**: OCR処理実行（内部API）

**ファイル**: `app/api/ocr/route.ts`

**Request**:
```json
{
  "jobId": "job_xxx",
  "pdfUrl": "s3://bucket/contracts/xxx.pdf"
}
```

**Response**:
```json
{
  "jobId": "job_xxx",
  "ocrText": "賃貸借契約書\n契約番号: C-2025-001\n...",
  "pageCount": 5,
  "processingTime": 12.5,
  "status": "OCR_COMPLETED"
}
```

**実装内容**:
1. S3からPDF取得
2. Amazon Textractで OCR実行
3. テキスト抽出・整形
4. UploadJob更新
5. 次のステップ（LLM抽出）をキューに登録

**依存サービス**:
- AWS S3
- Amazon Textract

**所要時間**: 5-6時間

---

##### 4. POST /api/extraction
**優先度**: 🟡 中

**説明**: LLM情報抽出（内部API）

**ファイル**: `app/api/extraction/route.ts`

**Request**:
```json
{
  "jobId": "job_xxx",
  "ocrText": "賃貸借契約書\n...",
  "contractType": "RENTAL"
}
```

**Response**:
```json
{
  "jobId": "job_xxx",
  "contractId": "contract_xxx",
  "extractedData": {
    "contractNumber": "C-2025-001",
    "type": "RENTAL",
    "startDate": "2025-04-01",
    "endDate": "2027-03-31",
    "details": { ... },
    "parties": [ ... ]
  },
  "confidenceScore": 0.92,
  "processingTime": 8.3,
  "status": "EXTRACTION_COMPLETED"
}
```

**実装内容**:
1. プロンプト構築
2. OpenAI/Claude API呼び出し
3. JSON抽出・バリデーション
4. 信頼度スコア計算
5. Contractレコード作成（verificationStatus: UNVERIFIED）
6. UploadJob更新

**依存サービス**:
- OpenAI API または Claude API

**所要時間**: 6-8時間

---

## フェーズ4: AI機能

RAG検索とAI分析を実装します。

### ✅ 4.1 RAG検索API

##### 1. POST /api/rag
**優先度**: 🟡 中

**説明**: RAG検索（自然言語による契約検索）

**ファイル**: `app/api/rag/route.ts`

**Request**:
```json
{
  "query": "来年3月末に満了する賃貸契約を教えて"
}
```

**Response**:
```json
{
  "answer": "2026年3月末（2026-03-31）に満了する賃貸契約は5件見つかりました。以下がその一覧です：\n\n1. C-2024-089: 渋谷店舗 1F（賃料: ¥800,000）\n2. C-2024-102: 品川オフィス 7F（賃料: ¥620,000）\n...",
  "contracts": [
    {
      "id": "contract_xxx",
      "contractNumber": "C-2024-089",
      "relevanceScore": 0.98,
      "propertyName": "渋谷店舗 1F",
      "endDate": "2026-03-31",
      "monthlyRent": 800000
    }
  ],
  "tokensUsed": 1250
}
```

**実装内容**:
1. クエリのEmbedding生成（OpenAI Embeddings）
2. PostgreSQL pgvectorでベクトル検索
3. 関連契約取得（Top 10）
4. コンテキスト構築
5. LLMで回答生成
6. SearchHistoryレコード作成

**依存サービス**:
- OpenAI Embeddings API
- PostgreSQL pgvector拡張

**前提条件**:
- 契約データのEmbedding事前生成が必要

**所要時間**: 8-10時間

---

### ✅ 4.2 AI分析API

##### 1. POST /api/analysis
**優先度**: 🟢 低

**説明**: AI契約分析（統計・集計）

**ファイル**: `app/api/analysis/route.ts`

**Request**:
```json
{
  "question": "A社がオーナーの物件の、一店舗あたりの賃料平均を計算して"
}
```

**Response**:
```json
{
  "answer": "A社がオーナーの物件は23件あり、平均賃料は¥584,348です。",
  "statistics": {
    "count": 23,
    "averageRent": 584348,
    "totalRent": 13440000,
    "minRent": 250000,
    "maxRent": 980000
  },
  "contracts": [
    {
      "id": "contract_xxx",
      "contractNumber": "C-2024-010",
      "propertyName": "渋谷店舗",
      "monthlyRent": 650000
    }
  ],
  "query": "SELECT AVG(monthly_rent) FROM contracts WHERE ...",
  "tokensUsed": 800
}
```

**実装内容**:
1. 自然言語からSQL生成（Text-to-SQL）
2. SQL実行（セキュリティチェック付き）
3. 結果を元に回答生成
4. グラフ用データ整形
5. AnalysisHistoryレコード作成

**依存サービス**:
- OpenAI API（GPT-4）

**所要時間**: 6-8時間

---

### ✅ 4.3 レントロール生成API

##### 1. POST /api/rentroll
**優先度**: 🟢 低

**説明**: レントロール生成（Excel/CSV/PDF出力）

**ファイル**: `app/api/rentroll/route.ts`

**Request**:
```json
{
  "filters": {
    "startDate": "2025-01-01",
    "endDate": "2025-12-31",
    "statuses": ["ACTIVE"],
    "types": ["RENTAL"]
  },
  "fields": [
    "contractNumber",
    "propertyName",
    "propertyAddress",
    "monthlyRent",
    "deposit",
    "startDate",
    "endDate"
  ],
  "sortBy": "contractNumber",
  "sortOrder": "asc",
  "format": "xlsx"
}
```

**Response**:
```json
{
  "downloadUrl": "https://s3.amazonaws.com/.../rentroll_20250117.xlsx",
  "fileName": "rentroll_20250117.xlsx",
  "recordCount": 987,
  "fileSize": 102400,
  "expiresAt": "2025-01-18T00:00:00Z"
}
```

**実装内容**:
1. フィルタリング・ソート
2. データ取得
3. Excel生成（xlsx）
4. S3にアップロード
5. Presigned URL発行（有効期限24時間）

**依存ライブラリ**:
- `exceljs` (Excel生成)
- `csv-writer` (CSV生成)
- `pdfkit` (PDF生成)

**所要時間**: 4-5時間

---

## 各APIの詳細仕様

### 📁 ディレクトリ構造

```
app/
├── api/
│   ├── auth/
│   │   └── [...nextauth]/
│   │       └── route.ts          # 認証API
│   ├── contracts/
│   │   ├── route.ts               # GET, POST /api/contracts
│   │   ├── [id]/
│   │   │   └── route.ts           # GET, PUT, DELETE /api/contracts/[id]
│   │   └── search/
│   │       └── route.ts           # POST /api/contracts/search
│   ├── upload/
│   │   ├── route.ts               # POST /api/upload
│   │   └── status/
│   │       └── route.ts           # GET /api/upload/status
│   ├── ocr/
│   │   └── route.ts               # POST /api/ocr (内部API)
│   ├── extraction/
│   │   └── route.ts               # POST /api/extraction (内部API)
│   ├── rag/
│   │   └── route.ts               # POST /api/rag
│   ├── analysis/
│   │   └── route.ts               # POST /api/analysis
│   └── rentroll/
│       └── route.ts               # POST /api/rentroll
├── lib/
│   ├── prisma.ts                  # Prismaクライアント
│   ├── auth.ts                    # 認証ヘルパー
│   ├── s3.ts                      # S3クライアント
│   ├── textract.ts                # Textractクライアント
│   ├── openai.ts                  # OpenAI APIクライアント
│   ├── claude.ts                  # Claude APIクライアント
│   └── email.ts                   # メール送信
└── services/
    ├── contractService.ts         # 契約管理ロジック
    ├── uploadService.ts           # アップロード処理
    ├── ocrService.ts              # OCR処理
    ├── extractionService.ts       # LLM抽出
    ├── ragService.ts              # RAG検索
    ├── analysisService.ts         # AI分析
    └── rentrollService.ts         # レントロール生成
```

---

## 🔧 共通実装パターン

### エラーハンドリング

すべてのAPIで統一したエラーレスポンスを返します：

```typescript
// lib/apiError.ts
export class ApiError extends Error {
  statusCode: number

  constructor(message: string, statusCode: number = 500) {
    super(message)
    this.statusCode = statusCode
  }
}

// APIルートでの使用例
export async function GET(request: Request) {
  try {
    // 処理...
  } catch (error) {
    if (error instanceof ApiError) {
      return Response.json(
        { error: error.message },
        { status: error.statusCode }
      )
    }
    return Response.json(
      { error: '内部サーバーエラー' },
      { status: 500 }
    )
  }
}
```

### 認証チェック

```typescript
// lib/auth.ts
import { auth } from '@/lib/auth'

export async function requireAuth() {
  const session = await auth()
  if (!session?.user) {
    throw new ApiError('認証が必要です', 401)
  }
  return session
}

// APIルートでの使用例
export async function GET(request: Request) {
  const session = await requireAuth()
  // 処理...
}
```

### バリデーション

```typescript
// schemas/contractSchema.ts
import { z } from 'zod'

export const createContractSchema = z.object({
  contractNumber: z.string().min(1),
  type: z.enum(['RENTAL', 'RENEWAL', 'MEMORANDUM']),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  // ...
})

// APIルートでの使用例
export async function POST(request: Request) {
  const body = await request.json()
  const validatedData = createContractSchema.parse(body)
  // 処理...
}
```

---

## 📊 開発スケジュール目安

| フェーズ | 内容 | 所要時間 | 累計 |
|---------|------|---------|------|
| フェーズ1 | 基盤構築（DB + 認証） | 5-8時間 | 5-8時間 |
| フェーズ2 | 契約管理API（5本） | 10-15時間 | 15-23時間 |
| フェーズ3 | アップロード・処理API（4本） | 16-22時間 | 31-45時間 |
| フェーズ4 | AI機能（3本） | 18-23時間 | 49-68時間 |
| **合計** | **14本のAPI** | **49-68時間** | - |

**実働日数換算**:
- 1日8時間作業: 約6-9日
- 1日4時間作業: 約12-17日

---

## 🎯 推奨開発順序

### 第1週: 基盤構築
1. ✅ Prismaスキーマ実装
2. ✅ PostgreSQL接続
3. ✅ NextAuth.js統合
4. ✅ シードデータ作成

### 第2週: 契約管理
5. ✅ GET /api/contracts（一覧）
6. ✅ GET /api/contracts/[id]（詳細）
7. ✅ POST /api/contracts（作成）
8. ✅ PUT /api/contracts/[id]（更新）

### 第3週: アップロード機能
9. ✅ AWS S3統合
10. ✅ POST /api/upload
11. ✅ GET /api/upload/status
12. ✅ POST /api/ocr（Textract統合）

### 第4週: AI機能
13. ✅ POST /api/extraction（LLM統合）
14. ✅ POST /api/rag（RAG検索）
15. ✅ POST /api/analysis（AI分析）
16. ✅ POST /api/rentroll（レポート生成）

---

## 📚 参考ドキュメント

- **システム設計書**: `/契約管理APP システム設計書.md`
  - 3章: データベース設計
  - 4章: API設計
  - 5章: 主要機能の実装方針

- **要件定義書**: `/契約管理APP 要件定義書.md`
  - 5章: 機能要件
  - 7章: セキュリティ要件

- **実装整合性分析レポート**: `/実装整合性分析レポート.md`
  - 未実装機能の詳細

---

## 🔥 クイックスタート

まずはフェーズ1から始めましょう！

### ステップ1: Prismaセットアップ

```bash
cd /home/ryom/contract-manage-demo-next/app

# Prismaインストール
npm install prisma @prisma/client
npm install -D prisma

# Prisma初期化
npx prisma init
```

### ステップ2: スキーマ作成

`prisma/schema.prisma` を作成します（システム設計書3.2を参照）

### ステップ3: マイグレーション

```bash
# マイグレーション生成
npx prisma migrate dev --name init

# Prismaクライアント生成
npx prisma generate
```

### ステップ4: 最初のAPI作成

`app/api/contracts/route.ts` を作成して、GET /api/contracts を実装します。

---

**作成日**: 2025-12-17
**更新日**: 2025-12-17
**バージョン**: 1.0.0
