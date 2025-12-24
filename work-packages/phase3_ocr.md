# Phase 3: アップロード・処理API 作業パッケージ - OCR処理

**作成日**: 2025-12-17
**対象API**: POST /api/ocr
**優先度**: 高

---

## A. 目的・スコープ

### 何を実現するAPIか
S3に保存されたPDFファイルをOCR処理し、テキストデータを抽出する。

### 今回の範囲
- ✅ MVPでやること
  - Amazon Textract によるPDF OCR処理
  - 抽出テキストを UploadJob.ocrResult に保存
  - status を PROCESSING → COMPLETED / FAILED に更新
  - AuditLog記録
- ❌ やらないこと
  - 画像ファイル（PNG/JPEG）のOCR（v2で対応）
  - 手書き文字認識（Textractの高度機能は将来検討）
- ⚠️ Out of scope
  - OCR結果の校正・修正UI（フロントエンド側で実装）

### 成功条件
- **パフォーマンス**: 1ページあたり2〜5秒（Textract依存）
- **精度**: 印刷文字で95%以上（Textractの標準精度）
- **タイムアウト**: 60秒（Next.js API Routeの制限を考慮、ページ数で調整）

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/ocr
```

### 認証・認可
- **必須**: NextAuth.js セッション
- **権限**: 自分のジョブのみ処理可能

### リクエスト
**Content-Type**: `application/json`

**ボディ**:
```json
{
  "jobId": "cm12345678"
}
```

**バリデーション**:
- `jobId`: 必須、CUID形式
- ジョブのstatus=PENDING であること（PROCESSING/COMPLETEDは再実行不可）
- ジョブの所有者が自分であること

### レスポンス

**成功 (200 OK)** - OCR開始:
```json
{
  "message": "OCR処理を開始しました",
  "job": {
    "id": "cm12345678",
    "status": "PROCESSING",
    "fileName": "contract.pdf",
    "updatedAt": "2025-12-17T12:01:30.000Z"
  }
}
```

**成功後の状態** (ポーリングで GET /api/upload/[jobId] して確認):
```json
{
  "job": {
    "id": "cm12345678",
    "status": "COMPLETED",
    "ocrResult": "賃貸借契約書\n\n契約番号: C-2024-001\n契約期間: 2024年1月1日〜2026年12月31日\n賃料: 月額800,000円...",
    "updatedAt": "2025-12-17T12:03:00.000Z"
  }
}
```

**エラー (400 Bad Request)** - jobId不正:
```json
{
  "error": {
    "code": "INVALID_JOB_ID",
    "message": "ジョブIDが不正です"
  },
  "request_id": "req_abc123"
}
```

**エラー (404 Not Found)** - ジョブが存在しない:
```json
{
  "error": {
    "code": "JOB_NOT_FOUND",
    "message": "指定されたジョブが見つかりません"
  },
  "request_id": "req_abc123"
}
```

**エラー (403 Forbidden)** - 他人のジョブ:
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "このジョブを処理する権限がありません"
  },
  "request_id": "req_abc123"
}
```

**エラー (409 Conflict)** - 既に処理済み:
```json
{
  "error": {
    "code": "JOB_ALREADY_PROCESSED",
    "message": "このジョブは既に処理されています",
    "details": [
      "現在のステータス: COMPLETED"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (500 Internal Server Error)** - Textractエラー:
```json
{
  "error": {
    "code": "OCR_FAILED",
    "message": "OCR処理に失敗しました",
    "details": [
      "Amazon Textractとの通信エラーが発生しました"
    ]
  },
  "request_id": "req_abc123"
}
```

### ステータスコード規約
- `200 OK` - OCR処理開始
- `400 Bad Request` - jobId不正
- `401 Unauthorized` - 認証エラー
- `403 Forbidden` - 権限エラー
- `404 Not Found` - ジョブが存在しない
- `409 Conflict` - 既に処理済み
- `500 Internal Server Error` - Textractエラー、DBエラー

---

## C. データ設計

### 既存テーブル: `upload_jobs`

**更新内容**:
```typescript
// OCR開始時
await prisma.uploadJob.update({
  where: { id: jobId },
  data: { status: 'PROCESSING' },
})

// OCR成功時
await prisma.uploadJob.update({
  where: { id: jobId },
  data: {
    status: 'COMPLETED',
    ocrResult: extractedText, // 長文テキスト（@db.Text）
  },
})

// OCR失敗時
await prisma.uploadJob.update({
  where: { id: jobId },
  data: {
    status: 'FAILED',
    errorMessage: 'OCR処理に失敗しました: ...',
  },
})
```

### トランザクション
- AuditLog記録とステータス更新を同一トランザクション内で実行:
```typescript
await prisma.$transaction([
  prisma.uploadJob.update({
    where: { id: jobId },
    data: { status: 'COMPLETED', ocrResult: extractedText },
  }),
  prisma.auditLog.create({
    data: {
      action: 'OCR_COMPLETED',
      entityType: 'UploadJob',
      entityId: jobId,
      userId: session.user.id,
      details: { fileName: job.fileName, textLength: extractedText.length },
    },
  }),
])
```

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: 1ページあたり2〜5秒（Textract依存）
- **タイムアウト**: 60秒（10ページ程度まで）
- **同時実行**: 5ジョブまで（Textractのスループット制限考慮）

### レート制限
- **ユーザーごと**: 同時実行中のOCRジョブ3個まで
- **429エラー**: `Retry-After: 60`

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **認可**: 自分のジョブのみ処理可能
- **S3アクセス**: IAMロールで制限

### ログ
```json
{
  "level": "info",
  "timestamp": "2025-12-17T12:01:30.000Z",
  "request_id": "req_abc123",
  "user_id": "user123",
  "action": "ocr_start",
  "job_id": "cm12345678",
  "file_name": "contract.pdf",
  "file_size": 2048000
}
```

```json
{
  "level": "info",
  "timestamp": "2025-12-17T12:03:00.000Z",
  "request_id": "req_abc123",
  "user_id": "user123",
  "action": "ocr_completed",
  "job_id": "cm12345678",
  "text_length": 5420,
  "duration_ms": 90000
}
```

---

## E. 開発ルール・運用ルール

### リポジトリ
- **URL**: `/home/ryom/contract-manage-demo-next/app`
- **ブランチ戦略**: trunk-based（mainブランチに直接コミット、本番運用時はGitFlowに移行）

### コーディング規約
- TypeScript Strict Mode
- ESLint + Prettier（既存設定に従う）
- 命名規則:
  - ファイル名: `route.ts`（Next.js API Route）
  - 関数名: camelCase
  - 定数: UPPER_SNAKE_CASE

### コミット規約
```
feat(api): Add OCR processing endpoint

- Implement POST /api/ocr with Textract integration
- Add status update logic (PENDING → PROCESSING → COMPLETED/FAILED)
- Add transaction for audit logging
- Add error handling for Textract failures
```

### PR運用
- **レビュー観点**:
  - セキュリティ（認証、認可）
  - エラーハンドリング
  - トランザクション処理
  - ログ出力
- **マージ条件**:
  - ESLint/Prettier通過
  - ビルド成功
  - 最低1名のApprove

### 環境
| 環境 | URL | データベース |
|-----|-----|------------|
| local | http://localhost:3001 | SQLite (dev.db) |
| dev | （未設定） | PostgreSQL |
| stg | （未設定） | PostgreSQL |
| prod | （未設定） | PostgreSQL |

---

## F. 連携仕様

### 外部連携: Amazon Textract

**SDK**: `@aws-sdk/client-textract` v3

**認証**: S3と同じAWS認証情報

**処理フロー**:
```typescript
import { TextractClient, DetectDocumentTextCommand } from '@aws-sdk/client-textract'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

const textractClient = new TextractClient({
  region: process.env.AWS_REGION!,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
})

// S3からPDF取得
const s3Response = await s3Client.send(
  new GetObjectCommand({
    Bucket: process.env.S3_BUCKET_NAME!,
    Key: job.s3Key,
  })
)

const pdfBuffer = await streamToBuffer(s3Response.Body)

// Textractで処理
const textractResponse = await textractClient.send(
  new DetectDocumentTextCommand({
    Document: {
      Bytes: pdfBuffer,
    },
  })
)

// テキスト抽出
const extractedText = textractResponse.Blocks
  ?.filter(block => block.BlockType === 'LINE')
  .map(block => block.Text)
  .join('\n') || ''

// DBに保存
await prisma.uploadJob.update({
  where: { id: jobId },
  data: { status: 'COMPLETED', ocrResult: extractedText },
})
```

**エラーハンドリング**:
- Textractエラー時はステータスをFAILEDに更新
- エラーメッセージをerrorMessageに保存

### 非同期処理
- このAPIは同期的にOCR処理を実行（タイムアウト60秒以内に完了想定）
- 将来的にバックグラウンドジョブ化も検討（Lambda + SQS等）

---

## 開発フロー

### Step 0: キックオフ
- スコープ: Textract連携 + OCR処理 + DB更新
- DoD: OCR成功率95%以上、エラーハンドリング完備

### Step 1: 仕様確定
- ✅ 上記仕様で確定

### Step 2: 土台構築
1. Textract SDK インストール:
   ```bash
   npm install @aws-sdk/client-textract
   ```
2. Textract IAMポリシー設定（`textract:DetectDocumentText` 権限）

### Step 3: 実装
1. **Textract連携関数** (`lib/textract.ts`):
   - `extractTextFromPDF(s3Key: string)`
2. **API Route実装** (`app/api/ocr/route.ts`):
   - 認証・認可チェック
   - ジョブ取得 + statusチェック
   - status → PROCESSING 更新
   - Textract処理
   - status → COMPLETED / FAILED 更新
   - AuditLog記録

### Step 4: テスト
1. **ユニットテスト**:
   - `textract.ts` のモック
2. **API統合テスト**:
   - 正常系: PDF → テキスト抽出成功
   - 異常系: 存在しないジョブ（404）、既に処理済み（409）、Textractエラー（500）
3. **実ファイルテスト**:
   - 実際の契約書PDFでOCR精度確認

### Step 5: デプロイ
- local環境でテスト
- AWS Textractの利用申請（必要に応じて）
- 監視設定（Textractエラー率）

---

## 🔧 環境変数

Phase 3 - API-3 で必要な環境変数:

```env
# AWS Textract (S3と同じ認証情報)
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=ap-northeast-1
S3_BUCKET_NAME=contract-management-uploads
```

---

## 📦 依存パッケージ

```bash
npm install @aws-sdk/client-textract
```

---

## ✅ チケット詳細

### タイトル
`[Phase3-3] POST /api/ocr - OCR処理実装`

### 目的
S3に保存されたPDFをOCR処理し、テキストデータを抽出する。

### 対象エンドポイント
`POST /api/ocr`

### 受け入れ条件
- [ ] PENDING状態のジョブがOCR処理される
- [ ] OCR成功時、ocrResultにテキストが保存される
- [ ] OCR成功時、statusがCOMPLETEDになる
- [ ] OCR失敗時、statusがFAILEDになり、errorMessageが保存される
- [ ] 既に処理済みのジョブは409エラー
- [ ] 他人のジョブは403エラー
- [ ] AuditLogに記録される
- [ ] 実際の契約書PDFでテキスト抽出できることを確認
- [ ] ESLint/Prettierエラーなし

### 影響範囲
- **新規ファイル**:
  - `app/api/ocr/route.ts`
  - `lib/textract.ts`
- **既存テーブル**: `upload_jobs`（ocrResult更新）

### 依存
- API-1（POST /api/upload）実装完了
- AWS Textractの利用申請完了
- IAMポリシー設定完了

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/ocr \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{"jobId": "cm12345678"}'
```

### サンプルレスポンス
```json
{
  "message": "OCR処理を開始しました",
  "job": {
    "id": "cm12345678",
    "status": "PROCESSING",
    "fileName": "contract.pdf",
    "updatedAt": "2025-12-17T12:01:30.000Z"
  }
}
```

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
