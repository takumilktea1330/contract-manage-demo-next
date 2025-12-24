# Phase 3: アップロード・処理API 作業パッケージ - LLM情報抽出

**作成日**: 2025-12-17
**対象API**: POST /api/extraction
**優先度**: 高

---

## A. 目的・スコープ

### 何を実現するAPIか
OCR済みのテキストからLLM（OpenAI/Claude）を使って契約情報を構造化データとして抽出する。

### 今回の範囲
- ✅ MVPでやること
  - OpenAI GPT-4o または Claude 3.5 Sonnet を使用
  - 契約番号、期間、賃料、当事者情報等を抽出
  - Contract + ContractDetail + ContractParty の自動作成
  - 抽出結果を UploadJob.extractionResult に保存
  - 信頼度スコア（confidenceScore）の計算
- ❌ やらないこと
  - 100%正確な抽出（信頼度lowの場合は人間が検証）
  - 複雑な契約条項の法的解釈（v2で検討）
- ⚠️ Out of scope
  - RAG検索（別API: POST /api/search）

### 成功条件
- **パフォーマンス**: p95 < 10秒（LLM API呼び出し時間依存）
- **精度**: 主要項目（契約番号、期間、賃料）で90%以上
- **信頼度**: confidenceScore > 0.8 の場合は検証不要レベル

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/extraction
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
- ジョブのstatus=COMPLETED であること（ocrResultが存在すること）
- ジョブの所有者が自分であること

### レスポンス

**成功 (201 Created)** - 契約作成完了:
```json
{
  "message": "契約情報が抽出されました",
  "contract": {
    "id": "cm99999999",
    "contractNumber": "C-2024-001",
    "type": "RENTAL",
    "status": "ACTIVE",
    "verificationStatus": "UNVERIFIED",
    "startDate": "2024-01-01T00:00:00.000Z",
    "endDate": "2026-12-31T00:00:00.000Z",
    "details": {
      "propertyAddress": "東京都渋谷区渋谷1-1-1",
      "monthlyRent": 800000,
      "deposit": 2400000,
      "confidenceScore": 0.85
    },
    "parties": [
      {
        "partyType": "LESSOR",
        "name": "株式会社ABC不動産"
      },
      {
        "partyType": "LESSEE",
        "name": "株式会社XYZ商事"
      }
    ]
  },
  "job": {
    "id": "cm12345678",
    "extractionResult": {
      "contractNumber": "C-2024-001",
      "type": "RENTAL",
      "startDate": "2024-01-01",
      "endDate": "2026-12-31",
      "monthlyRent": 800000,
      "deposit": 2400000,
      "lessor": { "name": "株式会社ABC不動産" },
      "lessee": { "name": "株式会社XYZ商事" }
    }
  }
}
```

**エラー (400 Bad Request)** - OCR未完了:
```json
{
  "error": {
    "code": "OCR_NOT_COMPLETED",
    "message": "OCR処理が完了していません",
    "details": [
      "先にOCR処理を実行してください（POST /api/ocr）"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (404 Not Found)**:
```json
{
  "error": {
    "code": "JOB_NOT_FOUND",
    "message": "指定されたジョブが見つかりません"
  },
  "request_id": "req_abc123"
}
```

**エラー (500 Internal Server Error)** - LLMエラー:
```json
{
  "error": {
    "code": "EXTRACTION_FAILED",
    "message": "情報抽出に失敗しました",
    "details": [
      "OpenAI APIとの通信エラーが発生しました"
    ]
  },
  "request_id": "req_abc123"
}
```

### ステータスコード規約
- `201 Created` - 契約作成完了
- `400 Bad Request` - OCR未完了、jobId不正
- `401 Unauthorized` - 認証エラー
- `403 Forbidden` - 権限エラー
- `404 Not Found` - ジョブが存在しない
- `500 Internal Server Error` - LLMエラー、DBエラー

---

## C. データ設計

### 新規作成: Contract, ContractDetail, ContractParty

```typescript
const contract = await prisma.contract.create({
  data: {
    contractNumber: extractedData.contractNumber,
    type: extractedData.type,
    status: 'ACTIVE',
    verificationStatus: 'UNVERIFIED',
    startDate: new Date(extractedData.startDate),
    endDate: new Date(extractedData.endDate),
    renewalType: extractedData.renewalType,
    noticePeriodMonths: extractedData.noticePeriodMonths,
    pdfUrl: job.s3Url,
    pdfFileName: job.fileName,
    pdfFileSize: job.fileSize,
    uploadJobId: job.id,
    creatorId: session.user.id,
    details: {
      create: {
        propertyAddress: extractedData.propertyAddress,
        propertyName: extractedData.propertyName,
        monthlyRent: extractedData.monthlyRent,
        deposit: extractedData.deposit,
        confidenceScore: extractedData.confidenceScore,
        // ... 他のフィールド
      },
    },
    parties: {
      create: [
        {
          partyType: 'LESSOR',
          name: extractedData.lessor.name,
          address: extractedData.lessor.address,
          // ...
        },
        {
          partyType: 'LESSEE',
          name: extractedData.lessee.name,
          address: extractedData.lessee.address,
          // ...
        },
      ],
    },
  },
  include: {
    details: true,
    parties: true,
  },
})

// UploadJob に extractionResult 保存
await prisma.uploadJob.update({
  where: { id: jobId },
  data: {
    extractionResult: extractedData,
  },
})

// AuditLog記録
await prisma.auditLog.create({
  data: {
    action: 'CONTRACT_CREATED',
    entityType: 'Contract',
    entityId: contract.id,
    userId: session.user.id,
    details: { source: 'LLM_EXTRACTION', jobId: job.id },
  },
})
```

### トランザクション
- Contract作成、UploadJob更新、AuditLog記録を同一トランザクション内で実行

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 10秒（LLM API呼び出し）
- **タイムアウト**: 30秒

### レート制限
- **OpenAI**: 組織ごとのレート制限に従う（TPM, RPM）
- **429エラー**: `Retry-After: 60`

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **認可**: 自分のジョブのみ処理可能
- **APIキー**: 環境変数で管理、絶対にログに出力しない

### ログ
```json
{
  "level": "info",
  "timestamp": "2025-12-17T12:05:00.000Z",
  "request_id": "req_abc123",
  "user_id": "user123",
  "action": "extraction_completed",
  "job_id": "cm12345678",
  "contract_id": "cm99999999",
  "confidence_score": 0.85,
  "duration_ms": 8500
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
feat(api): Add LLM extraction endpoint

- Implement POST /api/extraction with OpenAI integration
- Add Contract/Detail/Party creation logic
- Add confidence score calculation
- Add transaction for data consistency
- Add error handling for LLM failures
```

### PR運用
- **レビュー観点**:
  - セキュリティ（APIキー管理、認証、認可）
  - エラーハンドリング
  - トランザクション処理
  - プロンプト品質
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

### 外部連携: OpenAI API

**SDK**: `openai` v4

**認証**:
```typescript
import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
})
```

**プロンプト設計**:
```typescript
const systemPrompt = `
あなたは不動産契約書から情報を抽出するAIアシスタントです。
以下のJSONフォーマットで契約情報を出力してください。

必須フィールド:
- contractNumber (契約番号)
- type (RENTAL/RENEWAL/MEMORANDUM)
- startDate (開始日, YYYY-MM-DD)
- endDate (終了日, YYYY-MM-DD)
- monthlyRent (月額賃料, 数値)
- lessor (貸主情報 { name, address, phoneNumber?, email? })
- lessee (借主情報 { name, address, phoneNumber?, email? })

任意フィールド:
- propertyAddress, propertyName, deposit, keyMoney, ...
- confidenceScore (0.0〜1.0, 抽出精度の自己評価)

抽出できない項目はnullにしてください。
`

const response = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: `以下の契約書から情報を抽出してください:\n\n${job.ocrResult}` },
  ],
  response_format: { type: 'json_object' },
  temperature: 0.1,
})

const extractedData = JSON.parse(response.choices[0].message.content!)
```

**エラーハンドリング**:
- OpenAI APIエラー時は500エラーを返す
- レート制限エラー時は429エラーを返す

### 代替案: Claude API

**SDK**: `@anthropic-ai/sdk`

```typescript
import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY!,
})

const response = await anthropic.messages.create({
  model: 'claude-3-5-sonnet-20241022',
  max_tokens: 4096,
  system: systemPrompt,
  messages: [
    { role: 'user', content: `以下の契約書から情報を抽出してください:\n\n${job.ocrResult}` },
  ],
})

const extractedData = JSON.parse(response.content[0].text)
```

---

## 開発フロー

### Step 0: キックオフ
- スコープ: LLM連携 + 情報抽出 + Contract作成
- DoD: 抽出精度90%以上、信頼度スコア計算

### Step 1: 仕様確定
- ✅ 上記仕様で確定
- プロンプトエンジニアリング（精度チューニング）

### Step 2: 土台構築
1. OpenAI SDK インストール:
   ```bash
   npm install openai
   ```
2. 環境変数設定:
   ```env
   OPENAI_API_KEY=sk-...
   ```

### Step 3: 実装
1. **LLM連携関数** (`lib/llm.ts`):
   - `extractContractInfo(ocrText: string)`
   - プロンプトテンプレート
2. **API Route実装** (`app/api/extraction/route.ts`):
   - 認証・認可チェック
   - ジョブ取得 + ocrResult存在チェック
   - LLM処理
   - Contract/Detail/Party作成（トランザクション）
   - UploadJob.extractionResult更新
   - AuditLog記録

### Step 4: テスト
1. **プロンプトテスト**:
   - 実際の契約書テキストで抽出精度確認
   - エッジケース（情報不足、フォーマット不正）
2. **API統合テスト**:
   - 正常系: Contract作成成功
   - 異常系: OCR未完了（400）、LLMエラー（500）
3. **精度評価**:
   - 10件の契約書で主要項目の抽出精度測定（target: 90%以上）

### Step 5: デプロイ
- local環境でテスト
- OpenAI APIキーの本番用発行
- 監視設定（LLMエラー率、精度メトリクス）

---

## 🔧 環境変数

Phase 3 - API-4 で必要な環境変数:

```env
# OpenAI API
OPENAI_API_KEY=sk-...

# Claude API (オプション)
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 📦 依存パッケージ

```bash
npm install openai
# または
npm install @anthropic-ai/sdk
```

---

## ✅ チケット詳細

### タイトル
`[Phase3-4] POST /api/extraction - LLM情報抽出実装`

### 目的
OCR済みテキストからLLMで契約情報を抽出し、Contractレコードを自動作成する。

### 対象エンドポイント
`POST /api/extraction`

### 受け入れ条件
- [ ] OCR完了済みジョブから情報抽出できる
- [ ] Contract + ContractDetail + ContractParty が作成される
- [ ] extractionResult が UploadJob に保存される
- [ ] confidenceScore が計算される
- [ ] OCR未完了ジョブは400エラー
- [ ] AuditLogに記録される
- [ ] 実際の契約書で主要項目の抽出精度90%以上
- [ ] ESLint/Prettierエラーなし

### 影響範囲
- **新規ファイル**:
  - `app/api/extraction/route.ts`
  - `lib/llm.ts`
- **既存テーブル**: `contracts`, `contract_details`, `contract_parties`, `upload_jobs`

### 依存
- API-3（POST /api/ocr）実装完了
- OpenAI APIキー発行完了

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/extraction \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{"jobId": "cm12345678"}'
```

### サンプルレスポンス
```json
{
  "message": "契約情報が抽出されました",
  "contract": {
    "id": "cm99999999",
    "contractNumber": "C-2024-001",
    "type": "RENTAL",
    "status": "ACTIVE",
    "verificationStatus": "UNVERIFIED",
    "startDate": "2024-01-01T00:00:00.000Z",
    "endDate": "2026-12-31T00:00:00.000Z",
    "details": {
      "propertyAddress": "東京都渋谷区渋谷1-1-1",
      "monthlyRent": 800000,
      "deposit": 2400000,
      "confidenceScore": 0.85
    },
    "parties": [
      {
        "partyType": "LESSOR",
        "name": "株式会社ABC不動産"
      },
      {
        "partyType": "LESSEE",
        "name": "株式会社XYZ商事"
      }
    ]
  }
}
```

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
