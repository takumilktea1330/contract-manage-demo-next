# Phase 2: 契約管理API 作業パッケージ - 契約検索

**作成日**: 2025-12-17
**対象API**: POST /api/contracts/search
**優先度**: 中

---

## A. 目的・スコープ

### 何を実現するAPIか
複雑な検索条件による契約検索（通常検索、非RAG）を提供する。

### 今回の範囲
- ✅ MVPでやること
  - 複合条件検索（期間範囲、賃料範囲、所在地、契約種別、ステータス）
  - キーワード検索（全文検索、部分一致）
  - ページネーション対応
  - ソート機能
  - 認証チェック
- ❌ やらないこと
  - RAG検索（別API: POST /api/ragで実装）
  - 全文検索エンジン統合（PostgreSQL Full-Text Search、将来検討）
  - 検索履歴保存（v2で検討）
  - 保存された検索条件（v2で検討）
- ⚠️ Out of scope
  - 地理空間検索（住所からの距離検索等、v3で検討）

### 成功条件
- **パフォーマンス**: p95 < 1秒（複雑な条件でも高速検索）
- **検索精度**: 複合条件で正確にフィルタリング
- **柔軟性**: 任意の条件の組み合わせに対応

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/contracts/search
```

### 認証・認可
- **必須**: NextAuth.js セッション
- **ロール**: USER, MANAGER, ACCOUNTANT, ADMIN（全ロールOK）

### リクエスト
**Content-Type**: `application/json`

**ボディ**:
```json
{
  "keyword": "渋谷",
  "filters": {
    "type": "RENTAL",
    "status": "ACTIVE",
    "verificationStatus": "VERIFIED",
    "startDateFrom": "2024-01-01",
    "startDateTo": "2025-12-31",
    "endDateFrom": "2026-01-01",
    "endDateTo": "2028-12-31",
    "minRent": 100000,
    "maxRent": 1000000,
    "minArea": 50.0,
    "maxArea": 200.0,
    "propertyUsage": "事務所",
    "partyName": "丸の内不動産"
  },
  "page": 1,
  "limit": 20,
  "sortBy": "monthlyRent",
  "sortOrder": "desc"
}
```

**フィールド説明**:
| フィールド | 型 | 必須 | 説明 | バリデーション |
|----------|---|-----|------|--------------|
| `keyword` | string | ❌ | キーワード検索 | 最大255文字 |
| `filters.type` | string | ❌ | 契約種別 | RENTAL/RENEWAL/MEMORANDUM |
| `filters.status` | string | ❌ | 契約ステータス | ACTIVE/EXPIRED/TERMINATED |
| `filters.verificationStatus` | string | ❌ | 検証状態 | UNVERIFIED/VERIFIED/APPROVED |
| `filters.startDateFrom` | string | ❌ | 開始日（From） | ISO 8601形式 |
| `filters.startDateTo` | string | ❌ | 開始日（To） | ISO 8601形式 |
| `filters.endDateFrom` | string | ❌ | 終了日（From） | ISO 8601形式 |
| `filters.endDateTo` | string | ❌ | 終了日（To） | ISO 8601形式 |
| `filters.minRent` | number | ❌ | 最低賃料 | 0以上 |
| `filters.maxRent` | number | ❌ | 最高賃料 | 0以上 |
| `filters.minArea` | number | ❌ | 最小面積 | 0以上 |
| `filters.maxArea` | number | ❌ | 最大面積 | 0以上 |
| `filters.propertyUsage` | string | ❌ | 物件用途 | 最大100文字 |
| `filters.partyName` | string | ❌ | 当事者名 | 最大255文字 |
| `page` | number | ❌ | ページ番号 | 1以上、デフォルト1 |
| `limit` | number | ❌ | 取得件数 | 1-100、デフォルト20 |
| `sortBy` | string | ❌ | ソート項目 | contractNumber/startDate/endDate/monthlyRent/createdAt |
| `sortOrder` | string | ❌ | ソート順 | asc/desc、デフォルトdesc |

**リクエスト例**:
```bash
# 基本的な検索
curl -X POST http://localhost:3001/api/contracts/search \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "渋谷",
    "filters": {
      "type": "RENTAL",
      "status": "ACTIVE",
      "minRent": 100000,
      "maxRent": 1000000
    },
    "page": 1,
    "limit": 20
  }'

# 複雑な検索
curl -X POST http://localhost:3001/api/contracts/search \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "startDateFrom": "2024-01-01",
      "endDateTo": "2027-12-31",
      "minRent": 500000,
      "propertyUsage": "事務所",
      "partyName": "丸の内"
    },
    "sortBy": "monthlyRent",
    "sortOrder": "desc"
  }'
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
      "propertyName": "渋谷オフィスビル 5F",
      "propertyAddress": "東京都渋谷区渋谷1-1-1",
      "propertyUsage": "事務所",
      "propertyArea": 120.5,
      "monthlyRent": 800000,
      "createdAt": "2025-01-01T00:00:00.000Z"
    }
  ],
  "pagination": {
    "total": 15,
    "page": 1,
    "limit": 20,
    "totalPages": 1,
    "hasNext": false,
    "hasPrev": false
  },
  "searchSummary": {
    "keyword": "渋谷",
    "appliedFilters": {
      "type": "RENTAL",
      "status": "ACTIVE",
      "minRent": 100000,
      "maxRent": 1000000
    },
    "resultCount": 15
  }
}
```

**エラー (400 Bad Request)** - バリデーションエラー:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "検索条件が不正です",
    "details": [
      "minRent: 0以上の数値を指定してください",
      "startDateFrom: ISO 8601形式の日付を指定してください"
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

### ステータスコード規約
- `200 OK` - 検索成功（結果0件でも200）
- `400 Bad Request` - バリデーションエラー
- `401 Unauthorized` - 認証エラー
- `500 Internal Server Error` - DBエラー

---

## C. データ設計

### Prismaクエリ

```typescript
// バリデーション
const validated = searchContractsSchema.parse(body)

// フィルタ条件構築
const where: Prisma.ContractWhereInput = {
  // 契約種別・ステータス
  ...(validated.filters?.type && { type: validated.filters.type }),
  ...(validated.filters?.status && { status: validated.filters.status }),
  ...(validated.filters?.verificationStatus && { verificationStatus: validated.filters.verificationStatus }),

  // 開始日範囲
  ...(validated.filters?.startDateFrom && {
    startDate: { gte: new Date(validated.filters.startDateFrom) }
  }),
  ...(validated.filters?.startDateTo && {
    startDate: { lte: new Date(validated.filters.startDateTo) }
  }),

  // 終了日範囲
  ...(validated.filters?.endDateFrom && {
    endDate: { gte: new Date(validated.filters.endDateFrom) }
  }),
  ...(validated.filters?.endDateTo && {
    endDate: { lte: new Date(validated.filters.endDateTo) }
  }),

  // 物件情報フィルタ
  details: {
    ...(validated.filters?.minRent && { monthlyRent: { gte: validated.filters.minRent } }),
    ...(validated.filters?.maxRent && { monthlyRent: { lte: validated.filters.maxRent } }),
    ...(validated.filters?.minArea && { propertyArea: { gte: validated.filters.minArea } }),
    ...(validated.filters?.maxArea && { propertyArea: { lte: validated.filters.maxArea } }),
    ...(validated.filters?.propertyUsage && { propertyUsage: { contains: validated.filters.propertyUsage, mode: 'insensitive' } }),
  },

  // 当事者名フィルタ
  ...(validated.filters?.partyName && {
    parties: {
      some: {
        name: { contains: validated.filters.partyName, mode: 'insensitive' }
      }
    }
  }),

  // キーワード検索（契約番号、物件名、住所）
  ...(validated.keyword && {
    OR: [
      { contractNumber: { contains: validated.keyword, mode: 'insensitive' } },
      { details: { propertyName: { contains: validated.keyword, mode: 'insensitive' } } },
      { details: { propertyAddress: { contains: validated.keyword, mode: 'insensitive' } } },
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
        propertyUsage: true,
        propertyArea: true,
        monthlyRent: true,
      },
    },
  },
  orderBy: {
    [validated.sortBy || 'createdAt']: validated.sortOrder || 'desc',
  },
  skip: ((validated.page || 1) - 1) * (validated.limit || 20),
  take: validated.limit || 20,
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
  propertyUsage: contract.details?.propertyUsage || null,
  propertyArea: contract.details?.propertyArea || null,
  monthlyRent: contract.details?.monthlyRent ? Number(contract.details.monthlyRent) : null,
  createdAt: contract.createdAt,
}))

const totalPages = Math.ceil(total / (validated.limit || 20))
const page = validated.page || 1

return NextResponse.json({
  data,
  pagination: {
    total,
    page,
    limit: validated.limit || 20,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1,
  },
  searchSummary: {
    keyword: validated.keyword || null,
    appliedFilters: validated.filters || {},
    resultCount: total,
  },
})
```

### トランザクション
- 不要（読み取りのみ）

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 1秒（複雑な条件でも高速）
- **タイムアウト**: 10秒
- **インデックス**: startDate, endDate, status, verificationStatus にインデックス設定済み

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
  "action": "search_contracts",
  "keyword": "渋谷",
  "filters": {
    "type": "RENTAL",
    "minRent": 100000
  },
  "result_count": 15,
  "duration_ms": 650
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
- スコープ: 契約検索（複合条件） + ページネーション
- Must: 基本検索、フィルタリング、ページネーション
- Should: 複合条件、範囲検索、ソート
- DoD: テスト通過、パフォーマンス要件充足

### Step 1: 仕様確定
- ✅ 上記仕様で確定

### Step 2: 土台構築
- Phase2-1（一覧取得）実装完了が前提

### Step 3: 実装
1. **Zodスキーマ** (`schemas/contractSchema.ts`):
   - searchContractsSchema定義（複雑なネスト構造）
2. **API Route実装** (`app/api/contracts/search/route.ts`):
   - 認証チェック
   - バリデーション
   - 複雑なフィルタ条件構築
   - Prismaクエリ実行
   - レスポンス整形
   - エラーハンドリング

### Step 4: テスト
1. **API統合テスト**:
   - 正常系: 各種フィルタ、複合条件、ページネーション、ソート
   - 異常系: バリデーションエラー、未認証（401）
   - エッジケース: 結果0件、全フィルタ指定、範囲検索（minとmax）

### Step 5: デプロイ
- local環境でテスト
- インデックス確認

---

## チケット詳細

### タイトル
`[Phase2-6] POST /api/contracts/search - 契約検索実装`

### 目的
複雑な検索条件による契約検索を提供する。

### 対象エンドポイント
`POST /api/contracts/search`

### 受け入れ条件
- [ ] キーワード検索が動作する
- [ ] 各種フィルタが動作する（type, status, verificationStatus, 日付範囲, 賃料範囲, 面積範囲, 用途, 当事者名）
- [ ] 複合条件検索が動作する
- [ ] ページネーション情報が正しい
- [ ] ソート機能が動作する
- [ ] バリデーションエラー時に詳細なエラーメッセージ（400）
- [ ] 未認証時に401エラー
- [ ] 結果0件の場合も正しくレスポンス
- [ ] searchSummaryが含まれる
- [ ] ログが出力される
- [ ] ESLint/Prettierエラーなし

### 影響範囲
- **新規ファイル**: `app/api/contracts/search/route.ts`
- **更新ファイル**: `schemas/contractSchema.ts`（searchContractsSchema追加）
- **既存テーブル**: `contracts`, `contract_details`, `contract_parties`（読み取りのみ）

### 依存
- Phase2-1（一覧取得）実装完了

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/contracts/search \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "渋谷",
    "filters": {
      "type": "RENTAL",
      "minRent": 100000,
      "maxRent": 1000000
    },
    "page": 1,
    "limit": 20
  }'
```

### サンプルレスポンス
上記「仕様」参照

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
