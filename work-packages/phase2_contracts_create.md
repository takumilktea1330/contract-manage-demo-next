# Phase 2: 契約管理API 作業パッケージ - 契約作成

**作成日**: 2025-12-17
**対象API**: POST /api/contracts
**優先度**: 中

---

## A. 目的・スコープ

### 何を実現するAPIか
手動入力により新規契約を作成する（PDFアップロード経由ではない、マニュアル作成）。

### 今回の範囲
- ✅ MVPでやること
  - 契約基本情報の作成
  - 物件詳細情報の作成（ContractDetail）
  - 当事者情報の作成（ContractParty）
  - バリデーション（Zod）
  - 契約番号の重複チェック
  - トランザクション処理（Contract + Detail + Parties を同時作成）
  - 監査ログ記録
  - 認証・権限チェック
- ❌ やらないこと
  - PDFファイルのアップロード（別API: POST /api/uploadで実装）
  - AI抽出処理（別API: POST /api/extractionで実装）
- ⚠️ Out of scope
  - 承認ワークフロー（v2で検討）
  - ドラフト保存機能（v2で検討）

### 成功条件
- **パフォーマンス**: p95 < 1秒（トランザクション内で3テーブルINSERT）
- **データ整合性**: トランザクション処理により全てのデータが確実に作成される
- **バリデーション**: 必須項目・形式・範囲の厳密なチェック
- **監査**: 契約作成をAuditLogに記録

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/contracts
```

### 認証・認可
- **必須**: NextAuth.js セッション
- **ロール**: USER, MANAGER, ADMIN（経理担当者ACCOUNTANTは閲覧のみ）

### リクエスト
**Content-Type**: `application/json`

**ボディ**:
```json
{
  "contractNumber": "C-2025-100",
  "type": "RENTAL",
  "status": "ACTIVE",
  "verificationStatus": "VERIFIED",
  "startDate": "2025-04-01",
  "endDate": "2027-03-31",
  "renewalType": "自動更新",
  "noticePeriodMonths": 3,
  "pdfUrl": "https://s3.amazonaws.com/...",
  "pdfFileName": "contract.pdf",
  "pdfFileSize": 2048000,
  "details": {
    "propertyAddress": "東京都渋谷区渋谷1-1-1",
    "propertyName": "渋谷ビル 3F",
    "propertyArea": 85.0,
    "propertyUsage": "店舗",
    "roomNumber": "301",
    "monthlyRent": 300000,
    "deposit": 900000,
    "keyMoney": 300000,
    "managementFee": 30000
  },
  "parties": [
    {
      "partyType": "LESSOR",
      "name": "不動産会社A",
      "nameKana": "フドウサンガイシャエー",
      "address": "東京都渋谷区...",
      "phoneNumber": "03-1111-2222",
      "email": "info@a-fudosan.co.jp"
    },
    {
      "partyType": "LESSEE",
      "name": "株式会社B商事",
      "nameKana": "カブシキガイシャビーショウジ",
      "address": "東京都港区...",
      "phoneNumber": "03-3333-4444",
      "email": "contact@b-shoji.co.jp"
    }
  ]
}
```

**必須フィールド**:
- `contractNumber` - 契約番号（ユニーク）
- `type` - 契約種別（RENTAL/RENEWAL/MEMORANDUM）
- `status` - 契約ステータス（ACTIVE/EXPIRED/TERMINATED）
- `startDate` - 開始日（ISO 8601形式）
- `endDate` - 終了日（ISO 8601形式）
- `details.propertyAddress` - 物件住所
- `details.monthlyRent` - 月額賃料
- `parties` - 当事者情報（最低1件、最大10件）

**任意フィールド**:
- `verificationStatus` - 検証状態（デフォルト: UNVERIFIED）
- `renewalType`, `noticePeriodMonths` - 更新条件
- `pdfUrl`, `pdfFileName`, `pdfFileSize` - PDFファイル情報
- `details.*` - その他物件情報
- `parties[].nameKana`, `parties[].email` など

### レスポンス

**成功 (201 Created)**:
```json
{
  "message": "契約が正常に作成されました",
  "contract": {
    "id": "cm12345678",
    "contractNumber": "C-2025-100",
    "type": "RENTAL",
    "status": "ACTIVE",
    "verificationStatus": "VERIFIED",
    "startDate": "2025-04-01T00:00:00.000Z",
    "endDate": "2027-03-31T00:00:00.000Z",
    "createdAt": "2025-12-17T12:00:00.000Z"
  }
}
```

**エラー (400 Bad Request)** - バリデーションエラー:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力内容に誤りがあります",
    "details": [
      "contractNumber: 契約番号は必須です",
      "startDate: 開始日は終了日より前である必要があります",
      "details.monthlyRent: 賃料は0以上の数値である必要があります"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (409 Conflict)** - 契約番号重複:
```json
{
  "error": {
    "code": "DUPLICATE_CONTRACT_NUMBER",
    "message": "この契約番号は既に使用されています",
    "details": [
      "契約番号: C-2025-100"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (401 Unauthorized)**:
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
    "message": "この操作を実行する権限がありません"
  },
  "request_id": "req_abc123"
}
```

### ステータスコード規約
- `201 Created` - 作成成功
- `400 Bad Request` - バリデーションエラー
- `401 Unauthorized` - 認証エラー
- `403 Forbidden` - 権限エラー
- `409 Conflict` - 契約番号重複
- `500 Internal Server Error` - DBエラー

---

## C. データ設計

### Prismaクエリ（トランザクション）

```typescript
// バリデーション
const validated = createContractSchema.parse(body)

// 契約番号重複チェック
const existing = await prisma.contract.findUnique({
  where: { contractNumber: validated.contractNumber },
})

if (existing) {
  return NextResponse.json(
    {
      error: {
        code: 'DUPLICATE_CONTRACT_NUMBER',
        message: 'この契約番号は既に使用されています',
        details: [`契約番号: ${validated.contractNumber}`]
      }
    },
    { status: 409 }
  )
}

// トランザクション実行
const contract = await prisma.$transaction(async (tx) => {
  // Contract作成
  const newContract = await tx.contract.create({
    data: {
      contractNumber: validated.contractNumber,
      type: validated.type,
      status: validated.status,
      verificationStatus: validated.verificationStatus || 'UNVERIFIED',
      startDate: new Date(validated.startDate),
      endDate: new Date(validated.endDate),
      renewalType: validated.renewalType,
      noticePeriodMonths: validated.noticePeriodMonths,
      pdfUrl: validated.pdfUrl,
      pdfFileName: validated.pdfFileName,
      pdfFileSize: validated.pdfFileSize,
      createdBy: session.user.id,
      details: {
        create: {
          propertyAddress: validated.details.propertyAddress,
          propertyName: validated.details.propertyName,
          propertyArea: validated.details.propertyArea,
          propertyUsage: validated.details.propertyUsage,
          roomNumber: validated.details.roomNumber,
          monthlyRent: validated.details.monthlyRent,
          deposit: validated.details.deposit,
          keyMoney: validated.details.keyMoney,
          managementFee: validated.details.managementFee,
        },
      },
      parties: {
        create: validated.parties.map(party => ({
          partyType: party.partyType,
          name: party.name,
          nameKana: party.nameKana,
          address: party.address,
          phoneNumber: party.phoneNumber,
          email: party.email,
        })),
      },
    },
    include: {
      details: true,
      parties: true,
    },
  })

  // AuditLog記録
  await tx.auditLog.create({
    data: {
      action: 'CONTRACT_CREATED',
      entityType: 'Contract',
      entityId: newContract.id,
      userId: session.user.id,
      details: {
        contractNumber: newContract.contractNumber,
        source: 'MANUAL_INPUT',
      },
    },
  })

  return newContract
})

return NextResponse.json(
  {
    message: '契約が正常に作成されました',
    contract: {
      id: contract.id,
      contractNumber: contract.contractNumber,
      type: contract.type,
      status: contract.status,
      verificationStatus: contract.verificationStatus,
      startDate: contract.startDate,
      endDate: contract.endDate,
      createdAt: contract.createdAt,
    },
  },
  { status: 201 }
)
```

### トランザクション
- **必須**: Contract + ContractDetail + ContractParty + AuditLog を同一トランザクション内で作成
- **ロールバック**: いずれかの作成に失敗した場合、全てロールバック

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 1秒（3テーブルINSERT + トランザクション）
- **タイムアウト**: 10秒

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **認可**: USER, MANAGER, ADMIN のみ作成可能
- **バリデーション**: Zodによる厳密な入力検証
- **SQLインジェクション対策**: Prismaのパラメータ化クエリ

### ログ/監視
```json
{
  "level": "info",
  "timestamp": "2025-12-17T12:00:00.000Z",
  "request_id": "req_abc123",
  "user_id": "user123",
  "action": "create_contract",
  "contract_number": "C-2025-100",
  "contract_id": "cm12345678",
  "duration_ms": 850
}
```

---

## E. 開発ルール・運用ルール

同Phase 1と同様

---

## F. 連携仕様

### 内部連携: Prisma
上記「データ設計」参照

---

## 開発フロー

### Step 0: キックオフ
- スコープ: 契約作成（手動入力） + トランザクション + バリデーション
- Must: 基本情報作成、トランザクション、重複チェック
- Should: 監査ログ、権限チェック
- DoD: テスト通過、トランザクション動作確認

### Step 1: 仕様確定
- ✅ 上記仕様で確定

### Step 2: 土台構築
- Phase2-2（詳細取得）実装完了が前提

### Step 3: 実装
1. **Zodスキーマ** (`schemas/contractSchema.ts`):
   - createContractSchema定義
   - ネストされたオブジェクト（details, parties）のバリデーション
2. **API Route実装** (`app/api/contracts/route.ts`):
   - 認証・権限チェック
   - バリデーション
   - 契約番号重複チェック
   - トランザクション実行
   - 監査ログ記録
   - エラーハンドリング

### Step 4: テスト
1. **API統合テスト**:
   - 正常系: 契約作成成功（details, parties含む）
   - 異常系: バリデーションエラー、契約番号重複（409）、権限不足（403）、未認証（401）
   - トランザクションテスト: 途中失敗時のロールバック確認

### Step 5: デプロイ
- local環境でテスト

---

## チケット詳細

### タイトル
`[Phase2-3] POST /api/contracts - 契約作成実装`

### 目的
手動入力により新規契約を作成する。

### 対象エンドポイント
`POST /api/contracts`

### 受け入れ条件
- [ ] 契約が正常に作成される（201）
- [ ] Contract + ContractDetail + ContractPartyが全て作成される
- [ ] 契約番号重複時に409エラー
- [ ] バリデーションエラー時に詳細なエラーメッセージ（400）
- [ ] 権限不足時に403エラー（ACCOUNTANT）
- [ ] 未認証時に401エラー
- [ ] トランザクション失敗時にロールバック
- [ ] AuditLogに記録される
- [ ] ログが出力される
- [ ] ESLint/Prettierエラーなし

### 影響範囲
- **更新ファイル**: `app/api/contracts/route.ts`（GETとPOSTを両方実装）
- **新規ファイル**: `schemas/contractSchema.ts`（createContractSchema）
- **既存テーブル**: `contracts`, `contract_details`, `contract_parties`, `audit_logs`（書き込み）

### 依存
- Phase2-2（詳細取得）実装完了

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/contracts \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "contractNumber": "C-2025-100",
    "type": "RENTAL",
    ...
  }'
```

### サンプルレスポンス
上記「仕様」参照

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
