# Phase 2: 契約管理API 作業パッケージ - 契約詳細取得

**作成日**: 2025-12-17
**対象API**: GET /api/contracts/[id]
**優先度**: 最高

---

## A. 目的・スコープ

### 何を実現するAPIか
契約IDを指定して、契約の詳細情報（基本情報、物件情報、当事者情報、金銭条件）を取得する。

### 今回の範囲
- ✅ MVPでやること
  - 契約基本情報の取得
  - 物件詳細情報の取得（ContractDetail）
  - 当事者情報の取得（ContractParty - 貸主/借主）
  - 信頼度スコアの表示
  - 検証状態の表示
  - 認証チェック
- ❌ やらないこと
  - 更新履歴の表示（v2で対応）
  - 関連文書一覧（v2で対応）
  - コメント機能（v2で対応）
- ⚠️ Out of scope
  - 他ユーザーのデータ閲覧制限（Phase 1では全ユーザーが全契約を閲覧可能）

### 成功条件
- **パフォーマンス**: p95 < 200ms（単一レコード取得 + JOIN）
- **データ完全性**: すべてのリレーションを含む完全なデータ取得
- **監査**: 詳細閲覧は記録しない（パフォーマンス考慮）

---

## B. 仕様（API仕様書）

### エンドポイント
```
GET /api/contracts/[id]
```

### 認証・認可
- **必須**: NextAuth.js セッション
- **ロール**: USER, MANAGER, ACCOUNTANT, ADMIN（全ロールOK）

### パスパラメータ
| パラメータ | 型 | 必須 | 説明 |
|----------|---|-----|------|
| `id` | string | ✅ | 契約ID（CUID） |

**リクエスト例**:
```bash
GET /api/contracts/cm12345678
```

### レスポンス

**成功 (200 OK)**:
```json
{
  "id": "cm12345678",
  "contractNumber": "C-2025-001",
  "type": "RENTAL",
  "status": "ACTIVE",
  "verificationStatus": "VERIFIED",
  "startDate": "2025-01-01T00:00:00.000Z",
  "endDate": "2027-12-31T00:00:00.000Z",
  "renewalType": "自動更新",
  "noticePeriodMonths": 3,
  "pdfUrl": "https://s3.amazonaws.com/...",
  "pdfFileName": "contract_20250101.pdf",
  "pdfFileSize": 2048000,
  "details": {
    "id": "detail123",
    "propertyAddress": "東京都千代田区丸の内1-1-1",
    "propertyName": "東京オフィスビル 5F",
    "propertyArea": 120.5,
    "propertyUsage": "事務所",
    "roomNumber": "501",
    "monthlyRent": 500000,
    "deposit": 1500000,
    "keyMoney": 1000000,
    "managementFee": 50000,
    "confidenceScore": 0.95,
    "extractedAt": "2025-01-01T10:30:00.000Z"
  },
  "parties": [
    {
      "id": "party123",
      "partyType": "LESSOR",
      "name": "株式会社丸の内不動産",
      "nameKana": "カブシキガイシャマルノウチフドウサン",
      "address": "東京都千代田区丸の内2-2-2",
      "phoneNumber": "03-1234-5678",
      "email": "info@marunouchi-fudosan.co.jp",
      "confidenceScore": 0.92
    },
    {
      "id": "party456",
      "partyType": "LESSEE",
      "name": "株式会社サンプル商事",
      "nameKana": "カブシキガイシャサンプルショウジ",
      "address": "東京都港区赤坂1-1-1",
      "phoneNumber": "03-9876-5432",
      "email": "contact@sample-shoji.co.jp",
      "confidenceScore": 0.98
    }
  ],
  "createdBy": "user123",
  "createdAt": "2025-01-01T00:00:00.000Z",
  "updatedAt": "2025-01-15T10:30:00.000Z",
  "verifiedAt": "2025-01-02T14:00:00.000Z",
  "verifiedBy": "user456"
}
```

**エラー (404 Not Found)** - 契約が存在しない:
```json
{
  "error": {
    "code": "CONTRACT_NOT_FOUND",
    "message": "指定された契約が見つかりません"
  },
  "request_id": "req_abc123"
}
```

**エラー (400 Bad Request)** - 不正なID形式:
```json
{
  "error": {
    "code": "INVALID_CONTRACT_ID",
    "message": "契約IDの形式が不正です"
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

### ステータスコード規約
- `200 OK` - 取得成功
- `400 Bad Request` - 不正なID形式
- `401 Unauthorized` - 認証エラー
- `404 Not Found` - 契約が存在しない
- `500 Internal Server Error` - DBエラー

---

## C. データ設計

### Prismaクエリ

```typescript
const contract = await prisma.contract.findUnique({
  where: { id: contractId },
  include: {
    details: true,
    parties: {
      orderBy: {
        partyType: 'asc', // LESSOR → LESSEE の順
      },
    },
  },
})

if (!contract) {
  return NextResponse.json(
    { error: { code: 'CONTRACT_NOT_FOUND', message: '指定された契約が見つかりません' } },
    { status: 404 }
  )
}

// レスポンス整形（Decimal型を数値に変換）
return NextResponse.json({
  ...contract,
  details: contract.details ? {
    ...contract.details,
    monthlyRent: contract.details.monthlyRent ? Number(contract.details.monthlyRent) : null,
    deposit: contract.details.deposit ? Number(contract.details.deposit) : null,
    keyMoney: contract.details.keyMoney ? Number(contract.details.keyMoney) : null,
    managementFee: contract.details.managementFee ? Number(contract.details.managementFee) : null,
  } : null,
})
```

### トランザクション
- 不要（読み取りのみ）

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 200ms（単一レコード取得 + 2つのJOIN）
- **タイムアウト**: 5秒

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **SQLインジェクション対策**: Prismaのパラメータ化クエリ

### ログ/監視
```json
{
  "level": "info",
  "timestamp": "2025-12-17T12:00:00.000Z",
  "request_id": "req_abc123",
  "user_id": "user123",
  "action": "get_contract_detail",
  "contract_id": "cm12345678",
  "duration_ms": 120
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
- スコープ: 契約詳細取得（基本情報 + 詳細 + 当事者）
- Must: データ取得、存在チェック、認証
- DoD: テスト通過、パフォーマンス要件充足

### Step 1: 仕様確定
- ✅ 上記仕様で確定

### Step 2: 土台構築
- Phase2-1（一覧取得）実装完了が前提

### Step 3: 実装
1. **API Route実装** (`app/api/contracts/[id]/route.ts`):
   - 認証チェック
   - ID形式バリデーション（CUID形式）
   - Prismaクエリ実行（include: details, parties）
   - 存在チェック（404処理）
   - レスポンス整形（Decimal → Number変換）
   - エラーハンドリング

### Step 4: テスト
1. **API統合テスト**:
   - 正常系: 契約詳細取得成功（details, parties含む）
   - 異常系: 存在しないID（404）、不正なID形式（400）、未認証（401）
   - エッジケース: detailsがnull、partiesが0件

### Step 5: デプロイ
- local環境でテスト

---

## チケット詳細

### タイトル
`[Phase2-2] GET /api/contracts/[id] - 契約詳細取得実装`

### 目的
契約IDを指定して、契約の詳細情報を取得する。

### 対象エンドポイント
`GET /api/contracts/[id]`

### 受け入れ条件
- [ ] 契約詳細が取得できる（200）
- [ ] details情報が含まれる（propertyAddress, monthlyRentなど）
- [ ] parties情報が含まれる（LESSOR, LESSEE）
- [ ] 存在しないIDで404エラー
- [ ] 不正なID形式で400エラー
- [ ] 未認証時に401エラー
- [ ] Decimal型が数値に変換されている
- [ ] ログが出力される
- [ ] ESLint/Prettierエラーなし

### 影響範囲
- **新規ファイル**: `app/api/contracts/[id]/route.ts`
- **既存テーブル**: `contracts`, `contract_details`, `contract_parties`（読み取りのみ）

### 依存
- Phase2-1（一覧取得）実装完了

### サンプルリクエスト
```bash
curl -X GET http://localhost:3001/api/contracts/cm12345678 \
  -H "Cookie: next-auth.session-token=xxx"
```

### サンプルレスポンス
上記「仕様」参照

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
