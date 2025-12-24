# Phase 2: 契約管理API 作業パッケージ - 契約一覧取得

**作成日**: 2025-12-17
**対象API**: GET /api/contracts
**優先度**: 最高

---

## A. 目的・スコープ

### 何を実現するAPIか
契約データをページネーション付きで取得し、フィルタリング・検索機能を提供する。

### 今回の範囲
- ✅ MVPでやること
  - ページネーション対応（limit, offset）
  - フィルタリング（契約種別、ステータス、検証状態）
  - キーワード検索（契約番号、物件名）
  - ソート機能（契約番号、開始日、終了日、賃料）
  - レスポンスにページネーション情報を含める
  - 認証チェック（ログイン必須）
- ❌ やらないこと（将来対応）
  - 複雑な全文検索（別API: POST /api/contracts/searchで実装）
  - RAG検索（別API: POST /api/ragで実装）
  - CSV/Excelエクスポート（別API: POST /api/rentrollで実装）
- ⚠️ Out of scope
  - 他ユーザーのデータ閲覧制限（Phase 1では全ユーザーが全契約を閲覧可能）
  - 削除済み契約の表示（論理削除は将来実装）

### 成功条件
- **パフォーマンス**: p95 < 500ms（1000件のDBから20件取得）
- **ページネーション**: デフォルト20件、最大100件
- **検索精度**: キーワード検索で部分一致（LIKE検索）
- **監査**: 閲覧操作は記録しない（検索・一覧は記録対象外）

---

## B. 仕様（API仕様書）

### エンドポイント
```
GET /api/contracts
```

### 認証・認可
- **必須**: NextAuth.js セッション（Cookie: next-auth.session-token）
- **ロール**: USER, MANAGER, ACCOUNTANT, ADMIN（全ロールOK）

### クエリパラメータ

| パラメータ | 型 | 必須 | デフォルト | 説明 | バリデーション |
|----------|---|-----|---------|------|--------------|
| `page` | number | ❌ | 1 | ページ番号 | 1以上 |
| `limit` | number | ❌ | 20 | 取得件数 | 1-100 |
| `type` | string | ❌ | - | 契約種別 | RENTAL/RENEWAL/MEMORANDUM |
| `status` | string | ❌ | - | 契約ステータス | ACTIVE/EXPIRED/TERMINATED |
| `verificationStatus` | string | ❌ | - | 検証状態 | UNVERIFIED/VERIFIED/APPROVED |
| `keyword` | string | ❌ | - | キーワード検索 | 最大255文字 |
| `sortBy` | string | ❌ | createdAt | ソート項目 | contractNumber/startDate/endDate/monthlyRent/createdAt |
| `sortOrder` | string | ❌ | desc | ソート順 | asc/desc |

**リクエスト例**:
```bash
# 基本的な一覧取得
GET /api/contracts

# ページネーション
GET /api/contracts?page=2&limit=50

# フィルタリング
GET /api/contracts?type=RENTAL&status=ACTIVE

# キーワード検索
GET /api/contracts?keyword=渋谷

# ソート
GET /api/contracts?sortBy=monthlyRent&sortOrder=desc

# 複合条件
GET /api/contracts?type=RENTAL&status=ACTIVE&keyword=渋谷&page=1&limit=20&sortBy=startDate&sortOrder=asc
```

### レスポンス

**成功 (200 OK)**:
```json
{
  "data": [
    {
      "id": "cm12345678",
      "contractNumber": "C-2025-001",
      "type": "RENTAL",
      "status": "ACTIVE",
      "verificationStatus": "VERIFIED",
      "startDate": "2025-01-01T00:00:00.000Z",
      "endDate": "2027-12-31T00:00:00.000Z",
      "propertyName": "東京オフィスビル 5F",
      "propertyAddress": "東京都千代田区丸の内1-1-1",
      "monthlyRent": 500000,
      "createdAt": "2025-01-01T00:00:00.000Z",
      "updatedAt": "2025-01-15T10:30:00.000Z"
    },
    {
      "id": "cm87654321",
      "contractNumber": "C-2025-002",
      "type": "RENTAL",
      "status": "ACTIVE",
      "verificationStatus": "UNVERIFIED",
      "startDate": "2025-02-01T00:00:00.000Z",
      "endDate": "2027-01-31T00:00:00.000Z",
      "propertyName": "渋谷店舗 1F",
      "propertyAddress": "東京都渋谷区渋谷1-1-1",
      "monthlyRent": 800000,
      "createdAt": "2025-02-01T00:00:00.000Z",
      "updatedAt": "2025-02-01T00:00:00.000Z"
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "totalPages": 5,
    "hasNext": true,
    "hasPrev": false
  }
}
```

**エラー (400 Bad Request)** - バリデーションエラー:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "パラメータが不正です",
    "details": [
      "limit: 1から100の範囲で指定してください",
      "type: RENTAL, RENEWAL, MEMORANDUM のいずれかを指定してください"
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

**エラー (500 Internal Server Error)**:
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "サーバーエラーが発生しました"
  },
  "request_id": "req_abc123"
}
```

### ステータスコード規約
- `200 OK` - 取得成功（データが0件でも200）
- `400 Bad Request` - バリデーションエラー
- `401 Unauthorized` - 認証エラー
- `500 Internal Server Error` - DBエラー、その他サーバーエラー

---

## C. データ設計

### 既存テーブル: `contracts`, `contract_details`

```prisma
model Contract {
  id                  String              @id @default(cuid())
  contractNumber      String              @unique @map("contract_number")
  type                ContractType
  status              ContractStatus      @default(ACTIVE)
  verificationStatus  VerificationStatus  @default(UNVERIFIED) @map("verification_status")
  startDate           DateTime            @map("start_date")
  endDate             DateTime            @map("end_date")
  pdfUrl              String              @map("pdf_url")
  pdfFileName         String              @map("pdf_file_name")
  createdBy           String              @map("created_by")
  createdAt           DateTime            @default(now()) @map("created_at")
  updatedAt           DateTime            @updatedAt @map("updated_at")

  creator             User                @relation(fields: [createdBy], references: [id])
  details             ContractDetail?
  parties             ContractParty[]

  @@index([contractNumber])
  @@index([status])
  @@index([verificationStatus])
  @@index([startDate])
  @@index([endDate])
  @@map("contracts")
}

model ContractDetail {
  id              String    @id @default(cuid())
  contractId      String    @unique @map("contract_id")
  propertyAddress String?   @map("property_address")
  propertyName    String?   @map("property_name")
  monthlyRent     Decimal?  @map("monthly_rent") @db.Decimal(12, 2)

  contract        Contract  @relation(fields: [contractId], references: [id], onDelete: Cascade)

  @@map("contract_details")
}
```

### Prismaクエリ

```typescript
// フィルタ条件構築
const where: Prisma.ContractWhereInput = {
  ...(type && { type }),
  ...(status && { status }),
  ...(verificationStatus && { verificationStatus }),
  ...(keyword && {
    OR: [
      { contractNumber: { contains: keyword, mode: 'insensitive' } },
      { details: { propertyName: { contains: keyword, mode: 'insensitive' } } },
      { details: { propertyAddress: { contains: keyword, mode: 'insensitive' } } },
    ]
  }),
}

// 件数取得
const total = await prisma.contract.count({ where })

// データ取得
const contracts = await prisma.contract.findMany({
  where,
  include: {
    details: {
      select: {
        propertyName: true,
        propertyAddress: true,
        monthlyRent: true,
      },
    },
  },
  orderBy: {
    [sortBy]: sortOrder,
  },
  skip: (page - 1) * limit,
  take: limit,
})

// レスポンス整形
const data = contracts.map(contract => ({
  id: contract.id,
  contractNumber: contract.contractNumber,
  type: contract.type,
  status: contract.status,
  verificationStatus: contract.verificationStatus,
  startDate: contract.startDate,
  endDate: contract.endDate,
  propertyName: contract.details?.propertyName || null,
  propertyAddress: contract.details?.propertyAddress || null,
  monthlyRent: contract.details?.monthlyRent ? Number(contract.details.monthlyRent) : null,
  createdAt: contract.createdAt,
  updatedAt: contract.updatedAt,
}))

const totalPages = Math.ceil(total / limit)

return {
  data,
  pagination: {
    total,
    page,
    limit,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1,
  },
}
```

### トランザクション
- 不要（読み取りのみ）

### データのライフサイクル
- **読み取り**: Contractテーブル + ContractDetailテーブル（LEFT JOIN）

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 500ms（1000件のDBから20件取得）
- **タイムアウト**: 10秒
- **スループット**: 1000 req/min

### レート制限
- なし（GET APIは冪等なため制限不要）

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **SQLインジェクション対策**: Prismaのパラメータ化クエリ
- **XSS対策**: Reactによる自動エスケープ

### ログ/監視
- **ログ形式**: JSON構造化ログ
  ```json
  {
    "level": "info",
    "timestamp": "2025-12-17T12:00:00.000Z",
    "request_id": "req_abc123",
    "user_id": "user123",
    "action": "list_contracts",
    "filters": {
      "type": "RENTAL",
      "status": "ACTIVE",
      "keyword": "渋谷"
    },
    "page": 1,
    "limit": 20,
    "result_count": 15,
    "duration_ms": 320
  }
  ```
- **メトリクス**:
  - 平均レスポンスタイム
  - 検索パターン分析（よく使われるフィルタ）
- **アラート条件**:
  - p95レイテンシ > 1秒
  - エラー率 > 5%

---

## E. 開発ルール・運用ルール

同Phase 1と同様

---

## F. 連携仕様

### 内部連携: Prisma

**クエリ**: 上記「データ設計」参照

---

## 開発フロー

### Step 0: キックオフ
- スコープ: 契約一覧取得 + ページネーション + フィルタリング + 検索
- Must: 基本的な一覧取得、ページネーション、認証チェック
- Should: フィルタリング、キーワード検索、ソート
- DoD: テスト通過、パフォーマンス要件充足

### Step 1: 仕様確定
- ✅ 上記仕様で確定

### Step 2: 土台構築
- Phase 1（認証）実装完了が前提
- Prismaスキーマ実装完了

### Step 3: 実装
1. **バリデーションスキーマ** (`schemas/contractSchema.ts`):
   - クエリパラメータのZodスキーマ
2. **API Route実装** (`app/api/contracts/route.ts`):
   - 認証チェック
   - バリデーション
   - フィルタ条件構築
   - Prismaクエリ実行
   - レスポンス整形
   - エラーハンドリング

### Step 4: テスト
1. **API統合テスト**:
   - 正常系: 一覧取得成功、ページネーション、フィルタリング、検索、ソート
   - 異常系: バリデーションエラー、未認証（401）
   - エッジケース: データ0件、最終ページ、limitが最大値
2. **パフォーマンステスト**:
   - 1000件のデータで p95 < 500ms を確認

### Step 5: デプロイ
- local環境でテスト
- インデックス確認（contractNumber, status, verificationStatus, startDate, endDate）

---

## チケット詳細

### タイトル
`[Phase2-1] GET /api/contracts - 契約一覧取得実装`

### 目的
契約データをページネーション付きで取得し、フィルタリング・検索機能を提供する。

### 対象エンドポイント
`GET /api/contracts`

### 受け入れ条件
- [ ] 契約一覧が取得できる（200）
- [ ] ページネーション情報が正しい（total, page, limit, totalPages, hasNext, hasPrev）
- [ ] 契約種別でフィルタリングできる（type）
- [ ] ステータスでフィルタリングできる（status）
- [ ] 検証状態でフィルタリングできる（verificationStatus）
- [ ] キーワード検索が動作する（契約番号、物件名、住所）
- [ ] ソート機能が動作する（sortBy, sortOrder）
- [ ] バリデーションエラー時に詳細なエラーメッセージ（400）
- [ ] 未認証時に401エラー
- [ ] データ0件の場合も正しくレスポンス（data: [], total: 0）
- [ ] ログが出力される
- [ ] ESLint/Prettierエラーなし

### 影響範囲
- **新規ファイル**:
  - `app/api/contracts/route.ts`
  - `schemas/contractSchema.ts`
- **既存テーブル**: `contracts`, `contract_details`（読み取りのみ）

### 依存
- Phase 1（認証）実装完了
- Prismaスキーマ実装完了
- シードデータ作成（テスト用契約データ）

### サンプルリクエスト
```bash
curl -X GET "http://localhost:3001/api/contracts?type=RENTAL&status=ACTIVE&keyword=渋谷&page=1&limit=20" \
  -H "Cookie: next-auth.session-token=xxx"
```

### サンプルレスポンス
上記「仕様」参照

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
