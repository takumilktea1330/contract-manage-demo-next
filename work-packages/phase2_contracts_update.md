# Phase 2: 契約管理API 作業パッケージ - 契約更新

**作成日**: 2025-12-17
**対象API**: PUT /api/contracts/[id]
**優先度**: 中

---

## A. 目的・スコープ

### 何を実現するAPIか
既存契約の情報を更新する（部分更新対応）。

### 今回の範囲
- ✅ MVPでやること
  - 契約基本情報の部分更新
  - 物件詳細情報の部分更新（ContractDetail）
  - 当事者情報の更新（ContractParty）
  - バリデーション（Zod）
  - 更新履歴記録（AuditLog）
  - トランザクション処理
  - 認証・権限チェック
- ❌ やらないこと
  - 契約番号の変更（不変とする）
  - 完全置換（PATCHではなくPUTだが、部分更新を許可）
  - 楽観的ロック（v2で検討）
- ⚠️ Out of scope
  - 承認ワークフロー（v2で検討）
  - 変更差分の詳細記録（v2で検討）

### 成功条件
- **パフォーマンス**: p95 < 1秒（複数テーブルUPDATE + トランザクション）
- **データ整合性**: トランザクション処理により全ての更新が確実に反映される
- **監査**: 更新前後の値をAuditLogに記録

---

## B. 仕様（API仕様書）

### エンドポイント
```
PUT /api/contracts/[id]
```

### 認証・認可
- **必須**: NextAuth.js セッション
- **ロール**: USER, MANAGER, ADMIN（経理担当者ACCOUNTANTは閲覧のみ）

### パスパラメータ
| パラメータ | 型 | 必須 | 説明 |
|----------|---|-----|------|
| `id` | string | ✅ | 契約ID（CUID） |

### リクエスト
**Content-Type**: `application/json`

**ボディ**（部分更新対応、指定したフィールドのみ更新）:
```json
{
  "status": "EXPIRED",
  "verificationStatus": "APPROVED",
  "details": {
    "monthlyRent": 550000,
    "managementFee": 55000
  },
  "parties": [
    {
      "id": "party123",
      "phoneNumber": "03-1234-9999",
      "email": "new-info@marunouchi-fudosan.co.jp"
    }
  ]
}
```

**更新可能フィールド**:
- 契約基本情報: `status`, `verificationStatus`, `renewalType`, `noticePeriodMonths`, `verifiedBy`, `verifiedAt`
- 物件詳細: `details.*`（全フィールド）
- 当事者情報: `parties[].phoneNumber`, `parties[].email`, `parties[].address`

**更新不可フィールド**:
- `contractNumber` - 契約番号（不変）
- `type` - 契約種別（不変）
- `startDate`, `endDate` - 契約期間（不変、変更する場合は新規契約作成）
- `createdBy`, `createdAt` - 作成者情報（不変）

### レスポンス

**成功 (200 OK)**:
```json
{
  "message": "契約が正常に更新されました",
  "contract": {
    "id": "cm12345678",
    "contractNumber": "C-2025-001",
    "status": "EXPIRED",
    "verificationStatus": "APPROVED",
    "updatedAt": "2025-12-17T12:00:00.000Z"
  }
}
```

**エラー (404 Not Found)**:
```json
{
  "error": {
    "code": "CONTRACT_NOT_FOUND",
    "message": "指定された契約が見つかりません"
  },
  "request_id": "req_abc123"
}
```

**エラー (400 Bad Request)** - バリデーションエラー:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力内容に誤りがあります",
    "details": [
      "status: ACTIVE, EXPIRED, TERMINATED のいずれかを指定してください",
      "details.monthlyRent: 賃料は0以上の数値である必要があります"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (400 Bad Request)** - 不変フィールド変更:
```json
{
  "error": {
    "code": "IMMUTABLE_FIELD_UPDATE",
    "message": "変更できないフィールドが含まれています",
    "details": [
      "contractNumber は変更できません",
      "startDate は変更できません"
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

**エラー (403 Forbidden)**:
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
- `200 OK` - 更新成功
- `400 Bad Request` - バリデーションエラー、不変フィールド変更
- `401 Unauthorized` - 認証エラー
- `403 Forbidden` - 権限エラー
- `404 Not Found` - 契約が存在しない
- `500 Internal Server Error` - DBエラー

---

## C. データ設計

### Prismaクエリ（トランザクション）

```typescript
// バリデーション
const validated = updateContractSchema.parse(body)

// 不変フィールドチェック
const immutableFields = ['contractNumber', 'type', 'startDate', 'endDate', 'createdBy', 'createdAt']
const attemptedImmutableUpdates = immutableFields.filter(field => field in body)

if (attemptedImmutableUpdates.length > 0) {
  return NextResponse.json(
    {
      error: {
        code: 'IMMUTABLE_FIELD_UPDATE',
        message: '変更できないフィールドが含まれています',
        details: attemptedImmutableUpdates.map(f => `${f} は変更できません`)
      }
    },
    { status: 400 }
  )
}

// 契約存在チェック
const existing = await prisma.contract.findUnique({
  where: { id: contractId },
  include: { details: true, parties: true },
})

if (!existing) {
  return NextResponse.json(
    { error: { code: 'CONTRACT_NOT_FOUND', message: '指定された契約が見つかりません' } },
    { status: 404 }
  )
}

// トランザクション実行
const updatedContract = await prisma.$transaction(async (tx) => {
  // Contract更新
  const updated = await tx.contract.update({
    where: { id: contractId },
    data: {
      ...(validated.status && { status: validated.status }),
      ...(validated.verificationStatus && { verificationStatus: validated.verificationStatus }),
      ...(validated.renewalType && { renewalType: validated.renewalType }),
      ...(validated.noticePeriodMonths && { noticePeriodMonths: validated.noticePeriodMonths }),
      ...(validated.verifiedBy && { verifiedBy: validated.verifiedBy }),
      ...(validated.verifiedAt && { verifiedAt: new Date(validated.verifiedAt) }),
    },
  })

  // ContractDetail更新
  if (validated.details) {
    await tx.contractDetail.update({
      where: { contractId },
      data: {
        ...(validated.details.propertyAddress && { propertyAddress: validated.details.propertyAddress }),
        ...(validated.details.propertyName && { propertyName: validated.details.propertyName }),
        ...(validated.details.monthlyRent !== undefined && { monthlyRent: validated.details.monthlyRent }),
        ...(validated.details.deposit !== undefined && { deposit: validated.details.deposit }),
        ...(validated.details.managementFee !== undefined && { managementFee: validated.details.managementFee }),
        // ... 他のフィールド
      },
    })
  }

  // ContractParty更新（指定されたpartyのみ）
  if (validated.parties && validated.parties.length > 0) {
    for (const party of validated.parties) {
      await tx.contractParty.update({
        where: { id: party.id },
        data: {
          ...(party.phoneNumber && { phoneNumber: party.phoneNumber }),
          ...(party.email && { email: party.email }),
          ...(party.address && { address: party.address }),
        },
      })
    }
  }

  // AuditLog記録
  await tx.auditLog.create({
    data: {
      action: 'CONTRACT_UPDATED',
      entityType: 'Contract',
      entityId: updated.id,
      userId: session.user.id,
      oldValue: JSON.stringify({
        status: existing.status,
        verificationStatus: existing.verificationStatus,
        details: existing.details,
      }),
      newValue: JSON.stringify({
        status: validated.status,
        verificationStatus: validated.verificationStatus,
        details: validated.details,
      }),
    },
  })

  return updated
})

return NextResponse.json({
  message: '契約が正常に更新されました',
  contract: {
    id: updatedContract.id,
    contractNumber: updatedContract.contractNumber,
    status: updatedContract.status,
    verificationStatus: updatedContract.verificationStatus,
    updatedAt: updatedContract.updatedAt,
  },
})
```

### トランザクション
- **必須**: Contract + ContractDetail + ContractParty + AuditLog を同一トランザクション内で更新

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 1秒（複数テーブルUPDATE）
- **タイムアウト**: 10秒

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **認可**: USER, MANAGER, ADMIN のみ更新可能
- **不変フィールド保護**: contractNumber等の変更を拒否

### ログ/監視
```json
{
  "level": "info",
  "timestamp": "2025-12-17T12:00:00.000Z",
  "request_id": "req_abc123",
  "user_id": "user123",
  "action": "update_contract",
  "contract_id": "cm12345678",
  "fields_updated": ["status", "details.monthlyRent"],
  "duration_ms": 750
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
- スコープ: 契約更新（部分更新） + 不変フィールド保護 + 監査ログ
- Must: 基本情報更新、トランザクション、不変フィールドチェック
- DoD: テスト通過、監査ログ記録確認

### Step 1: 仕様確定
- ✅ 上記仕様で確定

### Step 2: 土台構築
- Phase2-3（作成）実装完了が前提

### Step 3: 実装
1. **Zodスキーマ** (`schemas/contractSchema.ts`):
   - updateContractSchema定義（部分更新対応）
2. **API Route実装** (`app/api/contracts/[id]/route.ts`):
   - 認証・権限チェック
   - バリデーション
   - 不変フィールドチェック
   - 契約存在チェック
   - トランザクション実行
   - 監査ログ記録（oldValue, newValue）
   - エラーハンドリング

### Step 4: テスト
1. **API統合テスト**:
   - 正常系: 契約更新成功（status, details, parties）
   - 異常系: 存在しないID（404）、不変フィールド変更（400）、権限不足（403）
   - トランザクションテスト: ロールバック確認

### Step 5: デプロイ
- local環境でテスト

---

## チケット詳細

### タイトル
`[Phase2-4] PUT /api/contracts/[id] - 契約更新実装`

### 目的
既存契約の情報を更新する。

### 対象エンドポイント
`PUT /api/contracts/[id]`

### 受け入れ条件
- [ ] 契約が正常に更新される（200）
- [ ] 部分更新が動作する（指定フィールドのみ更新）
- [ ] 不変フィールド変更時に400エラー
- [ ] 存在しないIDで404エラー
- [ ] 権限不足時に403エラー
- [ ] AuditLogに記録される（oldValue, newValue含む）
- [ ] トランザクション失敗時にロールバック
- [ ] ログが出力される
- [ ] ESLint/Prettierエラーなし

### 影響範囲
- **更新ファイル**: `app/api/contracts/[id]/route.ts`（GETとPUTを両方実装）
- **更新ファイル**: `schemas/contractSchema.ts`（updateContractSchema追加）
- **既存テーブル**: `contracts`, `contract_details`, `contract_parties`, `audit_logs`（更新・書き込み）

### 依存
- Phase2-3（作成）実装完了

### サンプルリクエスト
```bash
curl -X PUT http://localhost:3001/api/contracts/cm12345678 \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "EXPIRED",
    "details": { "monthlyRent": 550000 }
  }'
```

### サンプルレスポンス
上記「仕様」参照

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
