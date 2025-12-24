# Phase 2: 契約管理API 作業パッケージ - 契約削除

**作成日**: 2025-12-17
**対象API**: DELETE /api/contracts/[id]
**優先度**: 低

---

## A. 目的・スコープ

### 何を実現するAPIか
既存契約を削除する（論理削除推奨）。

### 今回の範囲
- ✅ MVPでやること
  - 物理削除（実データを削除）
  - CASCADE削除（ContractDetail, ContractParty も自動削除）
  - 監査ログ記録（削除前のデータを保存）
  - 認証・権限チェック（ADMIN のみ）
- ❌ やらないこと
  - 論理削除（v2で実装検討、deletedAt フィールド追加）
  - 削除の取り消し（v2で検討）
  - 関連データの保護（契約に紐づくファイルは削除しない）
- ⚠️ Out of scope
  - 承認ワークフロー（v2で検討）

### 成功条件
- **パフォーマンス**: p95 < 500ms（CASCADE削除）
- **データ整合性**: トランザクション処理により全ての関連データが確実に削除される
- **監査**: 削除前のデータをAuditLogに完全保存
- **安全性**: ADMIN ロールのみ実行可能

---

## B. 仕様（API仕様書）

### エンドポイント
```
DELETE /api/contracts/[id]
```

### 認証・認可
- **必須**: NextAuth.js セッション
- **ロール**: ADMIN のみ（他のロールは403）

### パスパラメータ
| パラメータ | 型 | 必須 | 説明 |
|----------|---|-----|------|
| `id` | string | ✅ | 契約ID（CUID） |

**リクエスト例**:
```bash
DELETE /api/contracts/cm12345678
```

### レスポンス

**成功 (200 OK)**:
```json
{
  "message": "契約が正常に削除されました",
  "deletedContract": {
    "id": "cm12345678",
    "contractNumber": "C-2025-001"
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
    "message": "この操作を実行する権限がありません。管理者のみ契約を削除できます"
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
- `200 OK` - 削除成功
- `401 Unauthorized` - 認証エラー
- `403 Forbidden` - 権限エラー（非ADMIN）
- `404 Not Found` - 契約が存在しない
- `500 Internal Server Error` - DBエラー

---

## C. データ設計

### Prismaクエリ（トランザクション）

```typescript
// 権限チェック
if (session.user.role !== 'ADMIN') {
  return NextResponse.json(
    {
      error: {
        code: 'FORBIDDEN',
        message: 'この操作を実行する権限がありません。管理者のみ契約を削除できます'
      }
    },
    { status: 403 }
  )
}

// 契約存在チェック（削除前にデータ取得、監査ログ用）
const existing = await prisma.contract.findUnique({
  where: { id: contractId },
  include: {
    details: true,
    parties: true,
  },
})

if (!existing) {
  return NextResponse.json(
    { error: { code: 'CONTRACT_NOT_FOUND', message: '指定された契約が見つかりません' } },
    { status: 404 }
  )
}

// トランザクション実行
await prisma.$transaction(async (tx) => {
  // AuditLog記録（削除前のデータを保存）
  await tx.auditLog.create({
    data: {
      action: 'CONTRACT_DELETED',
      entityType: 'Contract',
      entityId: existing.id,
      userId: session.user.id,
      oldValue: JSON.stringify({
        contractNumber: existing.contractNumber,
        type: existing.type,
        status: existing.status,
        startDate: existing.startDate,
        endDate: existing.endDate,
        details: existing.details,
        parties: existing.parties,
      }),
      details: {
        contractNumber: existing.contractNumber,
        deletedBy: session.user.id,
        deletedAt: new Date().toISOString(),
      },
    },
  })

  // Contract削除（CASCADE により details, parties も自動削除）
  await tx.contract.delete({
    where: { id: contractId },
  })
})

return NextResponse.json({
  message: '契約が正常に削除されました',
  deletedContract: {
    id: existing.id,
    contractNumber: existing.contractNumber,
  },
})
```

### Prismaスキーマ（CASCADE設定）

```prisma
model ContractDetail {
  id              String    @id @default(cuid())
  contractId      String    @unique @map("contract_id")
  // ...

  contract        Contract  @relation(fields: [contractId], references: [id], onDelete: Cascade)

  @@map("contract_details")
}

model ContractParty {
  id          String      @id @default(cuid())
  contractId  String      @map("contract_id")
  // ...

  contract    Contract    @relation(fields: [contractId], references: [id], onDelete: Cascade)

  @@map("contract_parties")
}
```

### トランザクション
- **必須**: AuditLog記録 → Contract削除（CASCADE により details, parties も削除）

### データのライフサイクル
- **削除**: Contract（物理削除）
- **自動削除**: ContractDetail, ContractParty（CASCADE）
- **保存**: AuditLogに削除前データを完全保存

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 500ms（CASCADE削除）
- **タイムアウト**: 10秒

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **認可**: ADMIN ロールのみ削除可能（厳格な権限チェック）
- **監査**: 削除前のデータを完全保存（復旧可能性を確保）

### ログ/監視
```json
{
  "level": "warn",
  "timestamp": "2025-12-17T12:00:00.000Z",
  "request_id": "req_abc123",
  "user_id": "admin123",
  "action": "delete_contract",
  "contract_id": "cm12345678",
  "contract_number": "C-2025-001",
  "duration_ms": 320
}
```

**注**: 削除操作は警告レベル（warn）でログ記録

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
- スコープ: 契約削除（物理削除） + CASCADE + ADMIN権限のみ
- Must: 削除処理、権限チェック（ADMIN）、監査ログ
- DoD: テスト通過、CASCADE動作確認、監査ログ記録確認

### Step 1: 仕様確定
- ✅ 上記仕様で確定

### Step 2: 土台構築
- Phase2-4（更新）実装完了が前提

### Step 3: 実装
1. **API Route実装** (`app/api/contracts/[id]/route.ts`):
   - 認証チェック
   - 権限チェック（ADMIN のみ）
   - 契約存在チェック + データ取得
   - トランザクション実行（監査ログ → 削除）
   - エラーハンドリング

### Step 4: テスト
1. **API統合テスト**:
   - 正常系: 契約削除成功（ADMIN）、CASCADE確認（details, parties も削除）
   - 異常系: 存在しないID（404）、非ADMIN（403）、未認証（401）
   - 監査ログ確認: 削除前データが保存されている

### Step 5: デプロイ
- local環境でテスト
- **重要**: 本番環境では慎重に実行（削除は復旧困難）

---

## チケット詳細

### タイトル
`[Phase2-5] DELETE /api/contracts/[id] - 契約削除実装`

### 目的
既存契約を削除する（ADMIN のみ）。

### 対象エンドポイント
`DELETE /api/contracts/[id]`

### 受け入れ条件
- [ ] 契約が正常に削除される（200、ADMIN）
- [ ] CASCADE削除が動作する（details, parties も削除）
- [ ] 非ADMIN時に403エラー（USER, MANAGER, ACCOUNTANT）
- [ ] 存在しないIDで404エラー
- [ ] 未認証時に401エラー
- [ ] AuditLogに記録される（削除前データ含む）
- [ ] トランザクション失敗時にロールバック
- [ ] ログが出力される（warnレベル）
- [ ] ESLint/Prettierエラーなし

### 影響範囲
- **更新ファイル**: `app/api/contracts/[id]/route.ts`（GET, PUT, DELETEを実装）
- **既存テーブル**: `contracts`, `contract_details`, `contract_parties`（削除）、`audit_logs`（書き込み）

### 依存
- Phase2-4（更新）実装完了
- Prismaスキーマの CASCADE 設定確認

### サンプルリクエスト
```bash
curl -X DELETE http://localhost:3001/api/contracts/cm12345678 \
  -H "Cookie: next-auth.session-token=xxx"
```

### サンプルレスポンス
上記「仕様」参照

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
