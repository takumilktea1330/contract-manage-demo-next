# Phase 3: アップロード・処理API 作業パッケージ - ファイルアップロード

**作成日**: 2025-12-17
**対象API**: POST /api/upload
**優先度**: 高

---

## A. 目的・スコープ

### 何を実現するAPIか
契約書PDFファイルをアップロードし、後続のOCR・LLM処理のための非同期ジョブを開始する。

### 今回の範囲
- ✅ MVPでやること
  - PDFファイルのマルチパートアップロード
  - AWS S3へのファイル保存
  - UploadJobレコードの作成（status: PENDING）
  - ファイルサイズ・拡張子バリデーション
  - 監査ログの記録
- ❌ やらないこと（将来対応）
  - 複数ファイル同時アップロード（v2で対応）
  - Word/Excel等の他形式サポート（v2で対応）
  - ドラッグ&ドロップUI（フロント側で実装済み）
- ⚠️ Out of scope
  - ファイルの自動削除（別途クリーンアップジョブで対応）
  - ウイルススキャン（セキュリティ要件で必要になったら追加）

### 成功条件
- **パフォーマンス**: p95 < 3秒（5MBファイル）
- **タイムアウト**: 30秒
- **最大ファイルサイズ**: 20MB
- **同時アップロード**: 最大10ファイル/ユーザー（保留中のジョブ）
- **ログ監査**: 全てのアップロードをAuditLogに記録

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/upload
```

### 認証・認可
- **必須**: NextAuth.js セッション（Cookie: next-auth.session-token）
- **ロール**: USER, MANAGER, ACCOUNTANT, ADMIN（全ロールOK）

### リクエスト
**Content-Type**: `multipart/form-data`

**フォームフィールド**:
| フィールド名 | 型 | 必須 | 説明 | バリデーション |
|------------|---|-----|------|--------------|
| `file` | File | ✅ | PDFファイル | .pdf, 最大20MB |
| `description` | string | ❌ | アップロードの説明 | 最大500文字 |

**リクエスト例**（curl）:
```bash
curl -X POST http://localhost:3001/api/upload \
  -H "Cookie: next-auth.session-token=xxx" \
  -F "file=@/path/to/contract.pdf" \
  -F "description=2024年度オフィス賃貸契約"
```

### レスポンス

**成功 (201 Created)**:
```json
{
  "message": "ファイルがアップロードされました",
  "job": {
    "id": "cm12345678",
    "status": "PENDING",
    "fileName": "contract.pdf",
    "fileSize": 2048000,
    "s3Key": "uploads/2024/12/cm12345678_contract.pdf",
    "s3Url": "https://your-bucket.s3.ap-northeast-1.amazonaws.com/uploads/2024/12/cm12345678_contract.pdf",
    "description": "2024年度オフィス賃貸契約",
    "createdAt": "2025-12-17T12:00:00.000Z",
    "userId": "user123"
  }
}
```

**エラー (400 Bad Request)** - ファイルなし:
```json
{
  "error": {
    "code": "FILE_REQUIRED",
    "message": "ファイルがアップロードされていません"
  },
  "request_id": "req_abc123"
}
```

**エラー (400 Bad Request)** - ファイル形式不正:
```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "PDFファイルのみアップロード可能です",
    "details": [
      "許可されている形式: .pdf"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (413 Payload Too Large)** - ファイルサイズ超過:
```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "ファイルサイズが上限を超えています",
    "details": [
      "最大サイズ: 20MB",
      "アップロードされたファイル: 25MB"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (429 Too Many Requests)** - 同時アップロード制限:
```json
{
  "error": {
    "code": "TOO_MANY_PENDING_JOBS",
    "message": "保留中のアップロードジョブが上限に達しています",
    "details": [
      "上限: 10ジョブ",
      "現在の保留中ジョブ: 10"
    ]
  },
  "request_id": "req_abc123",
  "retry_after": 300
}
```

**エラー (401 Unauthorized)** - 未認証:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "認証が必要です"
  },
  "request_id": "req_abc123"
}
```

**エラー (500 Internal Server Error)** - S3アップロード失敗:
```json
{
  "error": {
    "code": "UPLOAD_FAILED",
    "message": "ファイルのアップロードに失敗しました",
    "details": [
      "内部エラーが発生しました。しばらく経ってから再度お試しください。"
    ]
  },
  "request_id": "req_abc123"
}
```

### ステータスコード規約
- `201 Created` - アップロード成功、UploadJob作成完了
- `400 Bad Request` - ファイルなし、形式不正、バリデーションエラー
- `401 Unauthorized` - 認証エラー
- `413 Payload Too Large` - ファイルサイズ超過
- `429 Too Many Requests` - レート制限
- `500 Internal Server Error` - S3エラー、DBエラー

### エラー形式（共通）
```typescript
{
  error: {
    code: string,           // エラーコード（大文字スネークケース）
    message: string,        // ユーザー向けメッセージ（日本語）
    details?: string[]      // 追加の詳細情報
  },
  request_id: string,       // リクエスト追跡ID
  retry_after?: number      // 429の場合、リトライまでの秒数
}
```

---

## C. データ設計

### 既存テーブル: `upload_jobs`

```prisma
model UploadJob {
  id          String   @id @default(cuid())
  status      JobStatus @default(PENDING)  // PENDING, PROCESSING, COMPLETED, FAILED
  fileName    String
  fileSize    Int
  s3Key       String
  s3Url       String
  description String?
  errorMessage String?
  ocrResult   String?  @db.Text
  extractionResult Json?

  userId      String
  user        User     @relation(fields: [userId], references: [id])

  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@index([userId])
  @@index([status])
  @@index([createdAt])
}

enum JobStatus {
  PENDING
  PROCESSING
  COMPLETED
  FAILED
}
```

### データのライフサイクル
1. **作成**: POST /api/upload でステータス `PENDING`
2. **更新**: OCR処理で `PROCESSING` → `COMPLETED` / `FAILED`
3. **削除**: 論理削除なし（監査のため物理削除も避ける。将来的にアーカイブ機能実装）

### 監査項目
- `userId` - 誰がアップロードしたか
- `createdAt` - いつアップロードされたか
- AuditLog テーブルに記録:
  ```json
  {
    "action": "FILE_UPLOAD",
    "entityType": "UploadJob",
    "entityId": "cm12345678",
    "details": {
      "fileName": "contract.pdf",
      "fileSize": 2048000,
      "s3Key": "uploads/2024/12/cm12345678_contract.pdf"
    }
  }
  ```

### データ保持期間
- アップロード後90日間保持
- 90日経過後は別途クリーンアップジョブで削除（Phase 5で実装予定）

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 3秒（5MBファイル）、p99 < 5秒
- **タイムアウト**: 30秒（Next.js API Route のデフォルト）
- **最大ペイロード**: 20MB
- **スループット**: 100 req/min（全ユーザー合計）

### レート制限・スロットリング
- **ユーザーごと制限**: 保留中ジョブ10個まで
- **429エラー**: `Retry-After: 300`（5分後に再試行）
- 実装方法: PrismaでユーザーのPENDINGジョブ数をカウント

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **ファイル検証**:
  - MIMEタイプチェック（application/pdf）
  - マジックナンバーチェック（%PDF- で始まるか）
  - ファイルサイズ制限（20MB）
- **S3セキュリティ**:
  - Private bucket（認証済みユーザーのみアクセス）
  - 署名付きURL（有効期限: 1時間）
  - IAMロールでアクセス制限
- **入力検証**:
  - description は XSS 対策でサニタイズ（500文字制限）

### ログ/監視
- **ログ形式**: JSON構造化ログ
  ```json
  {
    "level": "info",
    "timestamp": "2025-12-17T12:00:00.000Z",
    "request_id": "req_abc123",
    "user_id": "user123",
    "action": "file_upload",
    "file_name": "contract.pdf",
    "file_size": 2048000,
    "s3_key": "uploads/2024/12/cm12345678_contract.pdf",
    "duration_ms": 1850
  }
  ```
- **メトリクス**:
  - アップロード成功率（target: > 99.5%）
  - 平均アップロード時間
  - S3エラー率
- **アラート条件**:
  - エラー率 > 5%（5分間）
  - p95レイテンシ > 5秒
  - S3接続エラー

### 可用性・冗長化
- **RPO/RTO**: N/A（ステートレスなアップロードAPI）
- **リトライ**: クライアント側で実装（Exponential Backoff）

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
  - 関数名: `uploadFile`, `validateFile`（camelCase）
  - 定数: `MAX_FILE_SIZE`（UPPER_SNAKE_CASE）

### コミット規約
```
feat(api): Add file upload endpoint

- Implement POST /api/upload with multipart support
- Add S3 integration with AWS SDK v3
- Add file validation (PDF, size limit)
- Add audit logging
```

### PR運用
- **レビュー観点**:
  - セキュリティ（ファイル検証、認証）
  - エラーハンドリング
  - ログ出力
  - テストカバレッジ
- **マージ条件**:
  - ESLint/Prettier通過
  - ビルド成功
  - 最低1名のApprove

### 環境
| 環境 | URL | データベース | S3バケット |
|-----|-----|------------|-----------|
| local | http://localhost:3001 | SQLite (dev.db) | 開発バケット |
| dev | （未設定） | PostgreSQL | 開発バケット |
| stg | （未設定） | PostgreSQL | ステージングバケット |
| prod | （未設定） | PostgreSQL | 本番バケット |

### デプロイ手順
- **local**: `npm run dev`（自動リロード）
- **本番**: CI/CD未設定（Phase 5で実装予定）

---

## F. 連携仕様

### 外部連携: AWS S3

**SDK**: `@aws-sdk/client-s3` v3

**認証**:
```typescript
import { S3Client } from '@aws-sdk/client-s3'

const s3Client = new S3Client({
  region: process.env.AWS_REGION || 'ap-northeast-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
})
```

**アップロード処理**:
```typescript
import { PutObjectCommand } from '@aws-sdk/client-s3'

const s3Key = `uploads/${new Date().getFullYear()}/${new Date().getMonth() + 1}/${jobId}_${fileName}`

await s3Client.send(
  new PutObjectCommand({
    Bucket: process.env.S3_BUCKET_NAME!,
    Key: s3Key,
    Body: fileBuffer,
    ContentType: 'application/pdf',
  })
)

const s3Url = `https://${process.env.S3_BUCKET_NAME}.s3.${process.env.AWS_REGION}.amazonaws.com/${s3Key}`
```

**エラーハンドリング**:
- S3エラー時はUploadJobを作成せず、500エラーを返す
- リトライはクライアント側で実装

### 内部連携: Prisma

**トランザクション**: 不要（UploadJob作成のみ）

**クエリ例**:
```typescript
const pendingJobsCount = await prisma.uploadJob.count({
  where: {
    userId: session.user.id,
    status: 'PENDING',
  },
})

if (pendingJobsCount >= 10) {
  return NextResponse.json(
    { error: { code: 'TOO_MANY_PENDING_JOBS', message: '...' } },
    { status: 429 }
  )
}

const job = await prisma.uploadJob.create({
  data: {
    fileName,
    fileSize,
    s3Key,
    s3Url,
    description,
    userId: session.user.id,
    status: 'PENDING',
  },
})

await prisma.auditLog.create({
  data: {
    action: 'FILE_UPLOAD',
    entityType: 'UploadJob',
    entityId: job.id,
    userId: session.user.id,
    details: { fileName, fileSize, s3Key },
  },
})
```

### 非同期処理
- アップロード完了後、OCR処理は別APIで実施（POST /api/ocr）
- Webhook/通知は不要（ポーリングでステータス確認: GET /api/upload/[jobId]）

---

## 開発フロー

### Step 0: キックオフ
- スコープ確認: ファイルアップロード + S3保存 + UploadJob作成
- Must: PDFアップロード、S3連携、バリデーション
- Should: レート制限、監査ログ
- Could: 複数ファイル対応（v2）
- DoD: テスト通過、エラーハンドリング完備、ログ出力確認

### Step 1: 仕様の確定
- ✅ 上記OpenAPI仕様で確定
- エラー形式、認証方式は既存APIと統一

### Step 2: 土台構築
1. AWS SDK インストール:
   ```bash
   npm install @aws-sdk/client-s3
   ```
2. 環境変数設定（`.env.local`）:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=ap-northeast-1
   S3_BUCKET_NAME=your-bucket-name
   ```
3. S3クライアント作成: `lib/s3.ts`
4. マルチパートパーサー設定（Next.js 15はネイティブサポート）

### Step 3: 実装
1. **ファイル検証ユーティリティ作成** (`lib/fileValidation.ts`):
   - PDFチェック（MIMEタイプ + マジックナンバー）
   - サイズチェック（20MB）
   - ファイル名サニタイズ
2. **S3アップロード関数作成** (`lib/s3.ts`):
   - `uploadToS3(file: File, jobId: string)`
3. **API Route実装** (`app/api/upload/route.ts`):
   - 認証チェック（NextAuth）
   - レート制限チェック（PENDING jobs count）
   - ファイル検証
   - S3アップロード
   - UploadJob作成
   - AuditLog記録
   - エラーハンドリング

### Step 4: テスト
1. **ユニットテスト**（Jest）:
   - `fileValidation.ts` の各関数
   - エッジケース（空ファイル、巨大ファイル、不正MIME）
2. **API統合テスト**:
   - 正常系: PDFアップロード成功
   - 異常系: ファイルなし、形式不正、サイズ超過、レート制限
   - 認証: 未認証時401
3. **負荷テスト**（オプション）:
   - 同時10リクエスト、p95 < 3秒を確認

### Step 5: デプロイ・運用
1. local環境でテスト
2. S3バケット作成 + IAMポリシー設定
3. 監視ダッシュボード確認（CloudWatch or 自前ログ）
4. Runbook作成:
   - S3接続エラー時 → AWS認証情報確認
   - レート制限頻発 → 上限を15に引き上げ検討

---

## 🔧 環境変数

Phase 3 - API-1 で必要な環境変数:

```env
# AWS S3
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=ap-northeast-1
S3_BUCKET_NAME=contract-management-uploads
```

---

## 📦 依存パッケージ

```bash
npm install @aws-sdk/client-s3
```

---

## ✅ チケット詳細

### タイトル
`[Phase3-1] POST /api/upload - ファイルアップロード実装`

### 目的
契約書PDFをアップロードし、OCR・LLM処理のための非同期ジョブを作成する。

### 対象エンドポイント
`POST /api/upload`

### 受け入れ条件
- [ ] PDFファイルのアップロードが成功し、S3に保存される
- [ ] UploadJobレコードが作成され、status=PENDINGになる
- [ ] AuditLogにFILE_UPLOADアクションが記録される
- [ ] 以下のバリデーションが動作する:
  - [ ] ファイルなし → 400エラー
  - [ ] PDF以外 → 400エラー
  - [ ] 20MB超過 → 413エラー
  - [ ] PENDING jobs 10個以上 → 429エラー
- [ ] 未認証時に401エラーが返る
- [ ] S3エラー時に500エラーが返る
- [ ] ログが構造化形式で出力される（request_id含む）
- [ ] ESLint/Prettierエラーなし
- [ ] ビルドが成功する

### 影響範囲
- **新規ファイル**:
  - `app/api/upload/route.ts`
  - `lib/s3.ts`
  - `lib/fileValidation.ts`
- **既存テーブル**: `upload_jobs`, `audit_logs`（既存のまま）
- **環境変数**: AWS_*, S3_BUCKET_NAME 追加

### 依存
- AWS S3バケット作成完了
- AWS IAMユーザー作成 + アクセスキー発行
- `@aws-sdk/client-s3` インストール

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/upload \
  -H "Cookie: next-auth.session-token=xxx" \
  -F "file=@/path/to/contract.pdf" \
  -F "description=テスト契約書"
```

### サンプルレスポンス
```json
{
  "message": "ファイルがアップロードされました",
  "job": {
    "id": "cm12345678",
    "status": "PENDING",
    "fileName": "contract.pdf",
    "fileSize": 2048000,
    "s3Key": "uploads/2024/12/cm12345678_contract.pdf",
    "s3Url": "https://...",
    "createdAt": "2025-12-17T12:00:00.000Z"
  }
}
```

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
