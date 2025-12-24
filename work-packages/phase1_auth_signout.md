# Phase 1: 認証API 作業パッケージ - ログアウト

**作成日**: 2025-12-17
**対象API**: POST /api/auth/signout
**優先度**: 中

---

## A. 目的・スコープ

### 何を実現するAPIか
現在のユーザーセッションを無効化し、ログアウト処理を実行する。

### 今回の範囲
- ✅ MVPでやること
  - NextAuth.js標準のsignOut機能
  - セッションCookieの削除
  - AuditLog記録（ログアウト履歴）
  - クライアント側リダイレクト（ログイン画面へ）
- ❌ やらないこと
  - 全デバイスからの一括ログアウト（v2で検討）
  - セッション管理画面（v2で検討）
- ⚠️ Out of scope
  - セッションの手動無効化（管理者機能として別途実装）

### 成功条件
- **パフォーマンス**: p95 < 200ms（シンプルなセッション削除）
- **セキュリティ**: セッションCookieの完全削除、CSRF保護
- **監査**: 全てのログアウトをAuditLogに記録

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/auth/signout
```

### 認証・認可
- **必須**: NextAuth.js セッション（Cookie: next-auth.session-token）
- **CSRF対策**: NextAuth.jsによる自動CSRF保護

### リクエスト
**Content-Type**: `application/json`

**ボディ**: なし（空のPOSTリクエスト）

**リクエスト例**:
```bash
curl -X POST http://localhost:3001/api/auth/signout \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json"
```

### レスポンス

**成功 (200 OK)**:
```json
{
  "message": "ログアウトしました",
  "redirect": "/login"
}
```

**注**: セッションCookieが削除される

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
- `200 OK` - ログアウト成功、セッション削除
- `401 Unauthorized` - 未認証（セッション存在しない）
- `500 Internal Server Error` - サーバー内部エラー

### エラー形式（共通）
```typescript
{
  error: {
    code: string,
    message: string,
    details?: string[]
  },
  request_id: string
}
```

---

## C. データ設計

### 既存テーブル: `audit_logs`

```prisma
model AuditLog {
  id          String    @id @default(cuid())
  userId      String    @map("user_id")
  contractId  String?   @map("contract_id")
  action      String
  oldValue    String?   @map("old_value")
  newValue    String?   @map("new_value")
  ipAddress   String?   @map("ip_address")
  createdAt   DateTime  @default(now()) @map("created_at")

  user        User      @relation(fields: [userId], references: [id])
  contract    Contract? @relation(fields: [contractId], references: [id])

  @@index([userId])
  @@index([contractId])
  @@index([createdAt])
  @@map("audit_logs")
}
```

### Prismaクエリ

```typescript
// 監査ログ記録
await prisma.auditLog.create({
  data: {
    action: 'LOGOUT',
    entityType: 'User',
    entityId: session.user.id,
    userId: session.user.id,
    ipAddress: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip'),
    details: {
      email: session.user.email,
      userAgent: request.headers.get('user-agent'),
    },
  },
})
```

### トランザクション
- 不要（監査ログ記録のみ）

### データのライフサイクル
- **書き込み**: AuditLogへのログアウト履歴記録
- **削除**: セッションデータ（NextAuth.jsが自動処理）

### 監査項目
- `action`: "LOGOUT"
- `entityType`: "User"
- `entityId`: ユーザーID
- `userId`: ログアウトしたユーザーID
- `ipAddress`: クライアントIPアドレス
- `details`: { email, userAgent }

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 200ms（監査ログ記録 + セッション削除）
- **タイムアウト**: 5秒

### レート制限
- なし（ログアウトは安全な操作のため制限不要）

### セキュリティ
- **CSRF対策**: NextAuth.jsによる自動CSRF保護
- **セッション削除**: Cookieの完全削除（Domain, Path, Secure属性考慮）
- **監査**: 全てのログアウトを記録

### ログ/監視
- **ログ形式**: JSON構造化ログ
  ```json
  {
    "level": "info",
    "timestamp": "2025-12-17T12:00:00.000Z",
    "request_id": "req_abc123",
    "action": "logout",
    "user_id": "user123",
    "ip_address": "203.0.113.42",
    "duration_ms": 120
  }
  ```
- **メトリクス**:
  - ログアウト成功率（target: > 99.9%）
  - 平均応答時間

### 可用性・冗長化
- **RPO/RTO**: N/A（ステートレスな操作）

---

## E. 開発ルール・運用ルール

### リポジトリ
- **URL**: `/home/ryom/contract-manage-demo-next/app`
- **ブランチ戦略**: trunk-based

### コーディング規約
- TypeScript Strict Mode
- ESLint + Prettier（既存設定に従う）

### コミット規約
```
feat(auth): Add signout endpoint

- Implement POST /api/auth/signout with NextAuth.js
- Add audit logging for logout events
- Add proper session cookie deletion
```

### PR運用
- **レビュー観点**:
  - セッション削除の完全性
  - 監査ログ記録
  - エラーハンドリング
- **マージ条件**:
  - ESLint/Prettier通過
  - ビルド成功
  - 最低1名のApprove

### 環境
Phase1-1（signin）と同じ

### デプロイ手順
Phase1-1（signin）と同じ

---

## F. 連携仕様

### 内部連携: NextAuth.js

**実装**:

```typescript
// app/api/auth/signout/route.ts
import { NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

export async function POST(request: Request) {
  try {
    const session = await auth()

    if (!session?.user) {
      return NextResponse.json(
        { error: { code: 'UNAUTHORIZED', message: '認証が必要です' } },
        { status: 401 }
      )
    }

    // 監査ログ記録
    await prisma.auditLog.create({
      data: {
        action: 'LOGOUT',
        entityType: 'User',
        entityId: session.user.id,
        userId: session.user.id,
        ipAddress: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip'),
        details: {
          email: session.user.email,
          userAgent: request.headers.get('user-agent'),
        },
      },
    })

    // NextAuth.js標準のsignOut処理
    // ※ NextAuth.jsの組み込み機能を使用
    // クライアント側で signOut() を呼び出すことを想定

    return NextResponse.json({
      message: 'ログアウトしました',
      redirect: '/login'
    })
  } catch (error) {
    console.error('Logout error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_SERVER_ERROR', message: 'サーバーエラーが発生しました' } },
      { status: 500 }
    )
  }
}
```

**クライアント側実装**:

```typescript
// フロントエンドでの使用例
import { signOut } from 'next-auth/react'

async function handleLogout() {
  // サーバー側の監査ログ記録
  await fetch('/api/auth/signout', { method: 'POST' })

  // NextAuth.jsのsignOut（セッション削除 + リダイレクト）
  await signOut({ callbackUrl: '/login' })
}
```

### 内部連携: Prisma

**クエリ**: 上記「データ設計」参照

---

## 開発フロー

### Step 0: キックオフ
- スコープ確認: ログアウト処理 + セッション削除 + 監査ログ
- Must: セッション削除、監査ログ記録
- Should: エラーハンドリング
- DoD: テスト通過、監査ログ記録確認

### Step 1: 仕様の確定
- ✅ 上記仕様で確定
- NextAuth.js標準機能を活用

### Step 2: 土台構築
- Phase1-1（signin）の実装完了が前提

### Step 3: 実装
1. **API Route実装** (`app/api/auth/signout/route.ts`):
   - セッション取得 + 存在チェック
   - 監査ログ記録
   - レスポンス返却
2. **クライアント側実装**:
   - signOutボタン/リンクの実装
   - NextAuth.js `signOut()` の呼び出し

### Step 4: テスト
1. **API統合テスト**:
   - 正常系: ログアウト成功、セッション削除
   - 異常系: 未認証時（401）
   - 監査ログ記録確認
2. **E2Eテスト**:
   - ログイン → ログアウト → 再アクセス（認証必要）
   - セッションCookie削除確認

### Step 5: デプロイ・運用
1. local環境でテスト
2. 監視設定（ログアウト成功率）

---

## チケット詳細

### タイトル
`[Phase1-2] POST /api/auth/signout - ログアウト実装`

### 目的
現在のユーザーセッションを無効化し、ログアウト処理を実行する。

### 対象エンドポイント
`POST /api/auth/signout`

### 受け入れ条件
- [ ] ログイン済みユーザーがログアウトできる（200）
- [ ] セッションCookieが削除される
- [ ] 未認証時にログアウトしようとすると401エラー
- [ ] ログアウト時にAuditLogに記録される（action: LOGOUT）
- [ ] ログが構造化形式で出力される
- [ ] ESLint/Prettierエラーなし
- [ ] ビルドが成功する

### 影響範囲
- **新規ファイル**:
  - `app/api/auth/signout/route.ts`
- **既存テーブル**: `audit_logs`（書き込み）

### 依存
- Phase1-1（signin）実装完了

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/auth/signout \
  -H "Cookie: next-auth.session-token=xxx"
```

### サンプルレスポンス
```json
{
  "message": "ログアウトしました",
  "redirect": "/login"
}
```

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
