# Phase 4-3: POST /api/rentroll - レントロール生成API 作業パッケージ

**作成日**: 2025-12-17
**対象フェーズ**: Phase 4-3 (レントロール生成)
**前提条件**: Phase 1, 2, 3 完了済み

---

## A. 目的・スコープ

### 何を実現するAPIか
契約データから詳細なレントロール（賃貸借契約一覧表）を生成し、Excel（XLSX）、CSV、PDF形式で出力する機能を提供する。ユーザーが指定した条件（期間、ステータス、種別、出力項目等）に基づいてカスタマイズ可能なレポートを生成し、S3にアップロードしてPresigned URLを返す。

### 今回の範囲
- ✅ MVPでやること
  - 詳細な出力条件設定（期間、ステータス、種別、出力項目、ソート順）
  - 3つの出力形式対応（Excel: XLSX、CSV、PDF）
  - Excel生成（exceljs使用）
  - CSV生成（csv-writer使用）
  - PDF生成（pdfkit使用）
  - S3へのアップロード
  - Presigned URL発行（有効期限24時間）
  - サマリー情報の計算（総件数、賃料合計、平均賃料、総面積）
- ❌ やらないこと（将来対応）
  - テンプレートのカスタマイズ機能（v2で対応）
  - グラフ・チャートの埋め込み（v2で対応）
  - メール自動送信機能（v2で対応）
  - 定期レポート自動生成（v2で対応）
- ⚠️ Out of scope
  - Excelマクロ機能（セキュリティリスクのため対応しない）
  - 複雑なピボットテーブル（v2で検討）

### 成功条件
- **生成成功率**: p95 > 95%（ファイル生成・S3アップロード成功率）
- **レイテンシ**: p95 < 10秒（1000件のデータ）
- **ファイルサイズ**: 最大10MB（10,000件程度まで対応）
- **出力品質**: Excel/CSV/PDFが正しいフォーマットで出力される

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/rentroll
```

### 認証・認可
- **必須**: NextAuth.js セッション（Cookie: next-auth.session-token）
- **ロール**: MANAGER, ACCOUNTANT, ADMIN（レポート出力権限が必要）
- **制限**: USERロールは閲覧のみ可（403エラー）

### リクエスト
**Content-Type**: `application/json`

**ボディ**:
| フィールド名 | 型 | 必須 | 説明 | バリデーション |
|------------|---|-----|------|--------------|
| `filters` | object | ✅ | 出力条件 | - |
| `filters.startDate` | string | ❌ | 開始日（契約開始日でフィルタ） | ISO 8601形式 |
| `filters.endDate` | string | ❌ | 終了日（契約開始日でフィルタ） | ISO 8601形式 |
| `filters.statuses` | string[] | ❌ | 契約ステータス | ACTIVE, EXPIRED, TERMINATED |
| `filters.types` | string[] | ❌ | 契約種別 | RENTAL, RENEWAL, MEMORANDUM |
| `fields` | string[] | ✅ | 出力項目 | 後述の出力可能項目から選択 |
| `sortBy` | string | ❌ | ソートキー（デフォルト: contractNumber） | 出力項目のいずれか |
| `sortOrder` | string | ❌ | ソート順（デフォルト: asc） | asc, desc |
| `format` | string | ✅ | 出力形式 | xlsx, csv, pdf |

**出力可能項目（fields）**:
- `contractNumber` - 契約番号
- `type` - 契約種別
- `status` - ステータス
- `verificationStatus` - 検証状態
- `startDate` - 開始日
- `endDate` - 終了日
- `renewalType` - 更新条件
- `noticePeriodMonths` - 解約予告期間
- `propertyAddress` - 物件住所
- `propertyName` - 物件名
- `propertyArea` - 面積
- `propertyUsage` - 用途
- `monthlyRent` - 月額賃料
- `deposit` - 敷金
- `keyMoney` - 礼金
- `managementFee` - 管理費
- `lessorName` - 貸主名
- `lessorAddress` - 貸主住所
- `lesseeName` - 借主名
- `lesseeAddress` - 借主住所
- `createdAt` - 作成日時
- `updatedAt` - 更新日時

**リクエスト例**:
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
    "endDate",
    "lessorName",
    "lesseeName"
  ],
  "sortBy": "contractNumber",
  "sortOrder": "asc",
  "format": "xlsx"
}
```

**curlコマンド例**:
```bash
curl -X POST http://localhost:3001/api/rentroll \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### レスポンス

**成功 (200 OK)**:
```json
{
  "downloadUrl": "https://your-bucket.s3.ap-northeast-1.amazonaws.com/rentrolls/2025/12/rentroll_20251217120000_user123.xlsx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
  "fileName": "rentroll_20251217120000.xlsx",
  "fileSize": 102400,
  "recordCount": 987,
  "summary": {
    "totalCount": 987,
    "totalRent": 584000000,
    "averageRent": 591699,
    "totalArea": 125450.5,
    "averageArea": 127.1
  },
  "expiresAt": "2025-12-18T12:00:00.000Z",
  "createdAt": "2025-12-17T12:00:00.000Z"
}
```

**エラー (400 Bad Request)** - 出力項目なし:
```json
{
  "error": {
    "code": "FIELDS_REQUIRED",
    "message": "出力項目を最低1つ指定してください",
    "details": [
      "指定された項目数: 0",
      "必要な項目数: 1以上"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (400 Bad Request)** - 不正な出力形式:
```json
{
  "error": {
    "code": "INVALID_FORMAT",
    "message": "不正な出力形式が指定されました",
    "details": [
      "指定された形式: doc",
      "サポートされている形式: xlsx, csv, pdf"
    ]
  },
  "request_id": "req_abc123"
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

**エラー (403 Forbidden)** - 権限不足:
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "レポート出力権限がありません",
    "details": [
      "必要なロール: MANAGER, ACCOUNTANT, ADMIN",
      "現在のロール: USER"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (404 Not Found)** - データなし:
```json
{
  "error": {
    "code": "NO_DATA_FOUND",
    "message": "指定された条件に一致するデータが見つかりません",
    "details": [
      "フィルタ条件を変更して再度お試しください"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (429 Too Many Requests)** - レート制限:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "レポート生成回数の上限に達しました",
    "details": [
      "上限: 10回/時間",
      "リトライまでの時間: 3600秒"
    ]
  },
  "request_id": "req_abc123",
  "retry_after": 3600
}
```

**エラー (500 Internal Server Error)** - ファイル生成失敗:
```json
{
  "error": {
    "code": "GENERATION_FAILED",
    "message": "レポート生成に失敗しました",
    "details": [
      "内部エラーが発生しました。しばらく経ってから再度お試しください。"
    ]
  },
  "request_id": "req_abc123"
}
```

### ステータスコード規約
- `200 OK` - レポート生成成功、Presigned URL発行完了
- `400 Bad Request` - フィルタ不正、出力項目なし、形式不正、バリデーションエラー
- `401 Unauthorized` - 認証エラー
- `403 Forbidden` - 権限エラー
- `404 Not Found` - データなし
- `429 Too Many Requests` - レート制限
- `500 Internal Server Error` - ファイル生成エラー、S3エラー

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

### 既存テーブル: `contracts`, `contract_details`, `contract_parties`
レントロール生成では既存の契約関連テーブルを出力対象とする。変更なし。

### データ取得クエリ
```typescript
const contracts = await prisma.contract.findMany({
  where: {
    ...(filters.startDate && { startDate: { gte: new Date(filters.startDate) } }),
    ...(filters.endDate && { startDate: { lte: new Date(filters.endDate) } }),
    ...(filters.statuses && { status: { in: filters.statuses } }),
    ...(filters.types && { type: { in: filters.types } }),
  },
  include: {
    details: true,
    parties: true,
  },
  orderBy: {
    [sortBy]: sortOrder,
  },
})
```

### データのライフサイクル
1. **レポート生成**: POST /api/rentroll で自動生成
2. **S3保存**: 生成されたファイルをS3にアップロード
3. **Presigned URL発行**: 有効期限24時間のダウンロードURL発行
4. **ファイル削除**: 7日経過後にS3から自動削除（ライフサイクルポリシー）

### 監査項目
- AuditLog に記録:
  ```json
  {
    "action": "RENTROLL_GENERATED",
    "entityType": "Rentroll",
    "details": {
      "format": "xlsx",
      "recordCount": 987,
      "filters": { ... }
    }
  }
  ```

### データ保持期間
- **S3ファイル**: 7日間保持（ライフサイクルポリシーで自動削除）

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 10秒（1000件のデータ）
- **タイムアウト**: 30秒（大量データの場合）
- **最大レコード数**: 10,000件まで対応
- **最大ファイルサイズ**: 10MB

### レート制限・スロットリング
- **ユーザーごと制限**: 10回/時間
- **429エラー**: `Retry-After: 3600`（1時間後に再試行）
- 実装方法: Redisまたはメモリベースのレート制限（simple-rate-limiter使用）

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **認可**: MANAGER, ACCOUNTANT, ADMIN ロールのみ
- **S3セキュリティ**:
  - Private bucket（認証済みユーザーのみアクセス）
  - Presigned URL（有効期限: 24時間）
  - IAMロールでアクセス制限
- **データマスキング**:
  - 個人情報（氏名・住所）は権限に応じてマスキング
  - ロールごとの表示制御:
    - ACCOUNTANT: 個人情報マスク（田中***）
    - MANAGER, ADMIN: 個人情報フル表示

### ログ/監視
- **ログ形式**: JSON構造化ログ
  ```json
  {
    "level": "info",
    "timestamp": "2025-12-17T12:00:00.000Z",
    "request_id": "req_abc123",
    "user_id": "user123",
    "action": "rentroll_generated",
    "format": "xlsx",
    "record_count": 987,
    "file_size": 102400,
    "processing_time": 8500,
    "s3_key": "rentrolls/2025/12/rentroll_20251217120000_user123.xlsx"
  }
  ```
- **メトリクス**:
  - レポート生成成功率（target: > 95%）
  - 平均生成時間
  - 平均ファイルサイズ
  - S3エラー率
- **アラート条件**:
  - エラー率 > 5%（5分間）
  - p95レイテンシ > 15秒
  - S3接続エラー

### 可用性・冗長化
- **RPO/RTO**: N/A（ステートレスなレポート生成API）
- **リトライ**: S3エラー時は3回リトライ（指数バックオフ）

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
  - 関数名: `generateExcel`, `generateCSV`, `generatePDF`（camelCase）
  - 定数: `MAX_RECORDS`, `PRESIGNED_URL_EXPIRY`（UPPER_SNAKE_CASE）

### コミット規約
```
feat(api): Add rentroll generation endpoint

- Implement POST /api/rentroll with Excel/CSV/PDF output
- Add exceljs integration for Excel generation
- Add csv-writer integration for CSV generation
- Add pdfkit integration for PDF generation
- Add S3 Presigned URL generation
```

### PR運用
- **レビュー観点**:
  - セキュリティ（権限チェック、データマスキング）
  - 性能（大量データの処理）
  - エラーハンドリング
  - ログ出力
- **マージ条件**:
  - ESLint/Prettier通過
  - ビルド成功
  - 最低1名のApprove

### 環境
| 環境 | URL | データベース | S3バケット |
|-----|-----|------------|-----------|
| local | http://localhost:3001 | PostgreSQL (dev) | 開発バケット |
| dev | （未設定） | PostgreSQL | 開発バケット |
| stg | （未設定） | PostgreSQL | ステージングバケット |
| prod | （未設定） | PostgreSQL | 本番バケット |

### デプロイ手順
- **local**: `npm run dev`（自動リロード）
- **本番**: CI/CD未設定（Phase 5で実装予定）

---

## F. 連携仕様

### 外部連携1: AWS S3（ファイル保存）

**SDK**: `@aws-sdk/client-s3` v3

**認証**:
```typescript
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'

const s3Client = new S3Client({
  region: process.env.AWS_REGION || 'ap-northeast-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
})
```

**ファイルアップロード処理**:
```typescript
const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
const fileName = `rentroll_${timestamp}_${userId}.${format}`
const s3Key = `rentrolls/${new Date().getFullYear()}/${new Date().getMonth() + 1}/${fileName}`

// S3にアップロード
await s3Client.send(
  new PutObjectCommand({
    Bucket: process.env.S3_BUCKET_NAME!,
    Key: s3Key,
    Body: fileBuffer,
    ContentType: getContentType(format),
    Metadata: {
      userId,
      recordCount: String(recordCount),
      createdAt: new Date().toISOString(),
    },
  })
)

// Presigned URL発行（有効期限24時間）
const command = new GetObjectCommand({
  Bucket: process.env.S3_BUCKET_NAME!,
  Key: s3Key,
})

const downloadUrl = await getSignedUrl(s3Client, command, { expiresIn: 86400 })
```

**S3ライフサイクルポリシー**:
```json
{
  "Rules": [
    {
      "Id": "DeleteOldRentrolls",
      "Status": "Enabled",
      "Prefix": "rentrolls/",
      "Expiration": {
        "Days": 7
      }
    }
  ]
}
```

### 外部連携2: exceljs（Excel生成）

**SDK**: `exceljs` v4

**Excel生成処理**:
```typescript
import ExcelJS from 'exceljs'

async function generateExcel(contracts: any[], fields: string[]): Promise<Buffer> {
  const workbook = new ExcelJS.Workbook()
  const worksheet = workbook.addWorksheet('レントロール')

  // ヘッダー行の設定
  const headers = fields.map(field => FIELD_LABELS[field])
  worksheet.addRow(headers)

  // ヘッダー行のスタイル設定
  const headerRow = worksheet.getRow(1)
  headerRow.font = { bold: true, size: 12 }
  headerRow.fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FF4472C4' },
  }
  headerRow.alignment = { vertical: 'middle', horizontal: 'center' }

  // データ行の追加
  contracts.forEach(contract => {
    const row = fields.map(field => formatFieldValue(contract, field))
    worksheet.addRow(row)
  })

  // カラム幅の自動調整
  worksheet.columns.forEach(column => {
    let maxLength = 0
    column.eachCell({ includeEmpty: true }, cell => {
      const length = cell.value ? String(cell.value).length : 10
      if (length > maxLength) {
        maxLength = length
      }
    })
    column.width = Math.min(maxLength + 2, 50)
  })

  // フィルター・固定行の設定
  worksheet.autoFilter = {
    from: { row: 1, column: 1 },
    to: { row: 1, column: fields.length },
  }
  worksheet.views = [{ state: 'frozen', xSplit: 0, ySplit: 1 }]

  // Bufferに変換
  const buffer = await workbook.xlsx.writeBuffer()
  return Buffer.from(buffer)
}
```

### 外部連携3: csv-writer（CSV生成）

**SDK**: `csv-writer` v1

**CSV生成処理**:
```typescript
import { createObjectCsvStringifier } from 'csv-writer'

async function generateCSV(contracts: any[], fields: string[]): Promise<Buffer> {
  const csvStringifier = createObjectCsvStringifier({
    header: fields.map(field => ({
      id: field,
      title: FIELD_LABELS[field],
    })),
  })

  // ヘッダー行
  const header = csvStringifier.getHeaderString()

  // データ行
  const records = contracts.map(contract => {
    const record: any = {}
    fields.forEach(field => {
      record[field] = formatFieldValue(contract, field)
    })
    return record
  })

  const body = csvStringifier.stringifyRecords(records)

  // BOM付きUTF-8（Excelで正しく開くため）
  const csv = '\uFEFF' + header + body
  return Buffer.from(csv, 'utf8')
}
```

### 外部連携4: pdfkit（PDF生成）

**SDK**: `pdfkit` v0.14

**PDF生成処理**:
```typescript
import PDFDocument from 'pdfkit'

async function generatePDF(contracts: any[], fields: string[]): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({
      size: 'A4',
      layout: 'landscape',
      margin: 50,
    })

    const chunks: Buffer[] = []
    doc.on('data', chunk => chunks.push(chunk))
    doc.on('end', () => resolve(Buffer.concat(chunks)))
    doc.on('error', reject)

    // 日本語フォントの登録（Noto Sans JP等）
    // doc.registerFont('NotoSansJP', 'path/to/NotoSansJP-Regular.ttf')
    // doc.font('NotoSansJP')

    // タイトル
    doc.fontSize(20).text('レントロール', { align: 'center' })
    doc.moveDown()

    // サマリー情報
    doc.fontSize(10).text(`生成日時: ${new Date().toLocaleString('ja-JP')}`)
    doc.text(`総件数: ${contracts.length}件`)
    doc.moveDown()

    // テーブル描画（簡易版）
    const tableTop = doc.y
    const columnWidth = (doc.page.width - 100) / fields.length
    let currentY = tableTop

    // ヘッダー行
    fields.forEach((field, i) => {
      doc.fontSize(8).text(
        FIELD_LABELS[field],
        50 + i * columnWidth,
        currentY,
        { width: columnWidth, align: 'center' }
      )
    })
    currentY += 20

    // データ行
    contracts.forEach((contract, rowIndex) => {
      if (currentY > doc.page.height - 100) {
        doc.addPage()
        currentY = 50
      }

      fields.forEach((field, i) => {
        doc.fontSize(7).text(
          String(formatFieldValue(contract, field) || ''),
          50 + i * columnWidth,
          currentY,
          { width: columnWidth, align: 'left' }
        )
      })
      currentY += 15
    })

    doc.end()
  })
}
```

### 内部連携: Prisma

**データ取得クエリ**:
```typescript
const contracts = await prisma.contract.findMany({
  where: {
    ...(filters.startDate && { startDate: { gte: new Date(filters.startDate) } }),
    ...(filters.endDate && { startDate: { lte: new Date(filters.endDate) } }),
    ...(filters.statuses && { status: { in: filters.statuses } }),
    ...(filters.types && { type: { in: filters.types } }),
  },
  include: {
    details: true,
    parties: true,
  },
  orderBy: {
    [sortBy]: sortOrder,
  },
  take: 10000, // 最大10,000件
})

// サマリー計算
const summary = {
  totalCount: contracts.length,
  totalRent: contracts.reduce((sum, c) => sum + (c.details?.monthlyRent || 0), 0),
  averageRent: contracts.length > 0 ?
    contracts.reduce((sum, c) => sum + (c.details?.monthlyRent || 0), 0) / contracts.length : 0,
  totalArea: contracts.reduce((sum, c) => sum + (c.details?.propertyArea || 0), 0),
  averageArea: contracts.length > 0 ?
    contracts.reduce((sum, c) => sum + (c.details?.propertyArea || 0), 0) / contracts.length : 0,
}
```

**AuditLog記録**:
```typescript
await prisma.auditLog.create({
  data: {
    action: 'RENTROLL_GENERATED',
    entityType: 'Rentroll',
    userId: session.user.id,
    details: {
      format,
      recordCount: contracts.length,
      filters,
      fileName,
    },
  },
})
```

---

## 開発フロー

### Step 0: キックオフ
- スコープ確認: レントロール生成（Excel/CSV/PDF） + S3アップロード + Presigned URL発行
- Must: 3形式対応、フィルタリング、ソート、サマリー計算
- Should: データマスキング、権限チェック
- Could: テンプレートカスタマイズ（v2）
- DoD: 生成成功率95%以上、レイテンシ10秒以内、エラーハンドリング完備

### Step 1: 仕様の確定
- ✅ 上記OpenAPI仕様で確定
- エラー形式、認証方式は既存APIと統一

### Step 2: 土台構築
1. **必要なパッケージインストール**:
   ```bash
   npm install exceljs csv-writer pdfkit @types/pdfkit
   npm install @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
   ```

2. **環境変数設定**（`.env.local`）:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=ap-northeast-1
   S3_BUCKET_NAME=contract-management-rentrolls
   ```

3. **S3バケット作成**:
   ```bash
   aws s3api create-bucket \
     --bucket contract-management-rentrolls \
     --region ap-northeast-1 \
     --create-bucket-configuration LocationConstraint=ap-northeast-1
   ```

4. **S3ライフサイクルポリシー設定**:
   ```bash
   aws s3api put-bucket-lifecycle-configuration \
     --bucket contract-management-rentrolls \
     --lifecycle-configuration file://lifecycle.json
   ```

### Step 3: 実装
1. **Excel生成関数** (`lib/excelGenerator.ts`):
   - `generateExcel(contracts: Contract[], fields: string[]): Promise<Buffer>`

2. **CSV生成関数** (`lib/csvGenerator.ts`):
   - `generateCSV(contracts: Contract[], fields: string[]): Promise<Buffer>`

3. **PDF生成関数** (`lib/pdfGenerator.ts`):
   - `generatePDF(contracts: Contract[], fields: string[]): Promise<Buffer>`

4. **S3アップロード関数** (`lib/s3Upload.ts`):
   - `uploadToS3(fileBuffer: Buffer, fileName: string, contentType: string): Promise<string>` - S3Key返却
   - `generatePresignedUrl(s3Key: string, expiresIn: number): Promise<string>`

5. **データフォーマット関数** (`lib/dataFormatter.ts`):
   - `formatFieldValue(contract: Contract, field: string): string | number` - 項目値のフォーマット
   - `maskPersonalInfo(value: string, role: string): string` - データマスキング

6. **API Route実装** (`app/api/rentroll/route.ts`):
   - 認証チェック（NextAuth）
   - 権限チェック（MANAGER, ACCOUNTANT, ADMIN）
   - フィルタ・フィールドバリデーション
   - レート制限チェック
   - データ取得（Prisma）
   - サマリー計算
   - ファイル生成（Excel/CSV/PDF）
   - S3アップロード
   - Presigned URL発行
   - AuditLog記録
   - エラーハンドリング

### Step 4: テスト
1. **ユニットテスト**（Jest）:
   - `excelGenerator.ts` の各関数
   - `csvGenerator.ts` の各関数
   - `pdfGenerator.ts` の各関数
   - `dataFormatter.ts` の各関数（特にマスキング）

2. **API統合テスト**:
   - 正常系: Excel/CSV/PDF生成成功、Presigned URL発行
   - 異常系: フィルタ不正、権限不足（403）、データなし（404）、形式不正（400）
   - 認証: 未認証時401

3. **ファイル出力テスト**:
   - 生成されたExcelをMicrosoft Excelで開いて確認
   - 生成されたCSVをExcelで開いて確認（文字化けなし）
   - 生成されたPDFをAdobe Readerで開いて確認

4. **負荷テスト**（オプション）:
   - 1000件のデータでp95 < 10秒を確認
   - 10,000件のデータで生成成功を確認

### Step 5: デプロイ・運用
1. local環境でテスト
2. S3バケット作成 + IAMポリシー設定
3. ライフサイクルポリシー設定（7日で自動削除）
4. 監視ダッシュボード確認（レイテンシ、エラー率、ファイルサイズ）
5. Runbook作成:
   - S3接続エラー時 → AWS認証情報確認
   - ファイル生成エラー時 → メモリ不足確認、ログで詳細確認
   - Presigned URL期限切れ時 → 再生成を案内

---

## チケット詳細

### タイトル
`[Phase4-3] POST /api/rentroll - レントロール生成実装`

### 目的
契約データから詳細なレントロールを生成し、Excel/CSV/PDF形式で出力する機能を提供する。

### 対象エンドポイント
`POST /api/rentroll`（上記OpenAPI仕様参照）

### 受け入れ条件
- [ ] Excel（XLSX）形式でレポート生成ができる
- [ ] CSV形式でレポート生成ができる
- [ ] PDF形式でレポート生成ができる
- [ ] フィルタリング（期間、ステータス、種別）が動作する
- [ ] 出力項目の選択が動作する
- [ ] ソート（昇順・降順）が動作する
- [ ] サマリー情報（総件数、賃料合計、平均賃料等）が計算される
- [ ] S3にファイルがアップロードされる
- [ ] Presigned URL（有効期限24時間）が発行される
- [ ] 以下のバリデーションが動作する:
  - [ ] 出力項目なし → 400エラー
  - [ ] 不正な形式 → 400エラー
  - [ ] 権限不足（USERロール） → 403エラー
  - [ ] データなし → 404エラー
  - [ ] レート制限超過 → 429エラー
- [ ] 未認証時に401エラーが返る
- [ ] S3エラー時に500エラーが返る
- [ ] データマスキングが動作する（ACCOUNTANTロール）
- [ ] AuditLogに記録される
- [ ] ログが構造化形式で出力される（request_id含む）
- [ ] 生成されたExcel/CSV/PDFが正しく開ける
- [ ] ESLint/Prettierエラーなし
- [ ] ビルドが成功する

### 影響範囲
- **新規ファイル**:
  - `app/api/rentroll/route.ts`
  - `lib/excelGenerator.ts`
  - `lib/csvGenerator.ts`
  - `lib/pdfGenerator.ts`
  - `lib/s3Upload.ts`（既存の場合は拡張）
  - `lib/dataFormatter.ts`
- **環境変数**: AWS_*, S3_BUCKET_NAME（既存の場合は確認）

### 依存
- AWS S3バケット作成完了
- AWS IAMユーザー作成 + アクセスキー発行
- `exceljs`, `csv-writer`, `pdfkit`, `@aws-sdk/client-s3` インストール完了

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/rentroll \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### サンプルレスポンス
上記「仕様」参照

---

## 🔧 技術補足

### 日本語フォント対応（PDF生成）

PDFで日本語を表示するには、日本語フォントを登録する必要があります。

```typescript
import PDFDocument from 'pdfkit'
import fs from 'fs'

// Noto Sans JPフォントのダウンロード
// https://fonts.google.com/noto/specimen/Noto+Sans+JP

const doc = new PDFDocument()

// 日本語フォントの登録
doc.registerFont('NotoSansJP', fs.readFileSync('path/to/NotoSansJP-Regular.ttf'))
doc.font('NotoSansJP')

// 日本語テキストの描画
doc.fontSize(12).text('レントロール', 50, 50)
```

### CSV BOM付きUTF-8（Excel互換）

WindowsのExcelでCSVを正しく開くには、BOM（Byte Order Mark）付きUTF-8が必要です。

```typescript
// BOM付きUTF-8
const csv = '\uFEFF' + headerString + dataString
const buffer = Buffer.from(csv, 'utf8')
```

### データマスキング実装例

```typescript
function maskPersonalInfo(value: string, userRole: string): string {
  // MANAGER, ADMINはマスキングなし
  if (userRole === 'MANAGER' || userRole === 'ADMIN') {
    return value
  }

  // ACCOUNTANT, USERはマスキング
  if (!value || value.length === 0) {
    return ''
  }

  // 名前のマスキング（最初の1文字のみ表示）
  if (value.length > 1) {
    return value.charAt(0) + '***'
  }

  return '***'
}
```

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
