# Phase 1: 認証API 作業パッケージ - ログイン

**作成日**: 2025-12-17
**対象API**: POST /api/auth/signin
**優先度**: 最高

---

## A. 目的・スコープ

### 何を実現するAPIか
メールアドレスとパスワードによるユーザー認証を実行し、セッションを確立する。

### 今回の範囲
- ✅ MVPでやること
  - NextAuth.js (Auth.js v5) によるCredentials認証
  - bcryptによるパスワードハッシュ検証
  - JWTベースのセッション管理
  - ログイン成功時のユーザー情報返却
  - AuditLog記録（ログイン履歴）
  - CSRF対策（NextAuth.js標準機能）
- ❌ やらないこと（将来対応）
  - OAuth認証（Google/Microsoft）- v2で対応
  - 多要素認証（MFA）- v2で対応
  - パスワードレス認証 - v3で検討
  - アカウントロックアウト機能 - v2で対応
- ⚠️ Out of scope
  - ユーザー登録機能（別途管理者が事前登録）
  - パスワードリセット（別APIで実装予定）

### 成功条件
- **パフォーマンス**: p95 < 500ms（bcrypt検証を含む）
- **セキュリティ**: bcrypt cost factor 12、CSRF保護、XSS対策
- **監査**: 全てのログイン試行（成功/失敗）をAuditLogに記録
- **エラーハンドリング**: 認証情報漏洩を防ぐ汎用エラーメッセージ

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/auth/signin
```

### 認証・認可
- **認証**: 不要（ログインAPIのため）
- **CSRF対策**: NextAuth.jsによる自動CSRF保護

### リクエスト
**Content-Type**: `application/json`

**ボディ**:
| フィールド名 | 型 | 必須 | 説明 | バリデーション |
|------------|---|-----|------|--------------|
| `email` | string | ✅ | メールアドレス | RFC 5322準拠、最大255文字 |
| `password` | string | ✅ | パスワード | 最小8文字、最大128文字 |

**リクエスト例**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### レスポンス

**成功 (200 OK)**:
```json
{
  "user": {
    "id": "cm12345678",
    "email": "user@example.com",
    "name": "山田太郎",
    "role": "USER"
  },
  "message": "ログインに成功しました"
}
```

**注**: セッションはCookieに保存される（`next-auth.session-token`）

**エラー (401 Unauthorized)** - 認証失敗:
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "メールアドレスまたはパスワードが正しくありません"
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
      "email: 有効なメールアドレスを入力してください",
      "password: パスワードは8文字以上である必要があります"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (429 Too Many Requests)** - レート制限:
```json
{
  "error": {
    "code": "TOO_MANY_REQUESTS",
    "message": "ログイン試行回数が上限に達しました。しばらく経ってから再度お試しください"
  },
  "request_id": "req_abc123",
  "retry_after": 300
}
```

**エラー (500 Internal Server Error)** - サーバーエラー:
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "サーバーエラーが発生しました。しばらく経ってから再度お試しください"
  },
  "request_id": "req_abc123"
}
```

### ステータスコード規約
- `200 OK` - ログイン成功、セッション確立
- `400 Bad Request` - バリデーションエラー
- `401 Unauthorized` - 認証失敗（メール/パスワード不一致）
- `429 Too Many Requests` - レート制限超過
- `500 Internal Server Error` - サーバー内部エラー

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

### 既存テーブル: `users`

```prisma
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  passwordHash  String    @map("password_hash")
  name          String
  role          UserRole  @default(USER)
  createdAt     DateTime  @default(now()) @map("created_at")
  updatedAt     DateTime  @updatedAt @map("updated_at")

  contracts     Contract[]
  uploadJobs    UploadJob[]
  auditLogs     AuditLog[]

  @@map("users")
}

enum UserRole {
  USER          // 事務担当者
  MANAGER       // マネージャー・管理者
  ACCOUNTANT    // 経理担当者
  ADMIN         // システム管理者
}
```

### Prismaクエリ

```typescript
// ユーザー取得（メールアドレスで検索）
const user = await prisma.user.findUnique({
  where: { email: credentials.email },
  select: {
    id: true,
    email: true,
    passwordHash: true,
    name: true,
    role: true,
  },
})

// 監査ログ記録
await prisma.auditLog.create({
  data: {
    action: 'LOGIN_SUCCESS', // または 'LOGIN_FAILED'
    entityType: 'User',
    entityId: user.id,
    userId: user.id,
    ipAddress: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip'),
    details: {
      email: user.email,
      userAgent: request.headers.get('user-agent'),
    },
  },
})
```

### トランザクション
- 不要（ログイン処理は単一のDB読み取り + 監査ログ記録）

### データのライフサイクル
- **読み取り**: ユーザー情報取得（メールアドレスでユニーク検索）
- **書き込み**: AuditLogへのログイン履歴記録

### 監査項目
- `action`: "LOGIN_SUCCESS" または "LOGIN_FAILED"
- `entityType`: "User"
- `entityId`: ユーザーID
- `userId`: ログイン試行したユーザーID（失敗時はnull）
- `ipAddress`: クライアントIPアドレス
- `details`: { email, userAgent, failureReason? }

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 500ms（bcrypt検証 250ms + DB読み取り 50ms + 監査ログ 100ms）
- **タイムアウト**: 5秒
- **スループット**: 100 req/min（全ユーザー合計）

### レート制限・スロットリング
- **IP単位**: 5回/分（失敗時のみカウント）
- **429エラー**: `Retry-After: 300`（5分）
- 実装方法: メモリキャッシュ（開発時）、将来的にRedisで実装

### セキュリティ
- **パスワードハッシュ**: bcrypt cost factor 12
- **CSRF対策**: NextAuth.jsによる自動CSRF保護
- **XSS対策**: Reactによる自動エスケープ + Content Security Policy
- **ブルートフォース対策**: レート制限（5回/分）
- **情報漏洩対策**: 認証失敗時は汎用エラーメッセージ（メールアドレスの存在を推測できないように）
- **セッション管理**: JWT（httpOnly Cookie、Secure属性、SameSite=Lax）
- **パスワード要件**: 最小8文字（将来的に複雑性要件を追加検討）

### ログ/監視
- **ログ形式**: JSON構造化ログ
  ```json
  {
    "level": "info",
    "timestamp": "2025-12-17T12:00:00.000Z",
    "request_id": "req_abc123",
    "action": "login_attempt",
    "email": "user@example.com",
    "ip_address": "203.0.113.42",
    "user_agent": "Mozilla/5.0...",
    "status": "success",
    "duration_ms": 320
  }
  ```
- **メトリクス**:
  - ログイン成功率（target: > 99%、正当なユーザーの場合）
  - ログイン失敗率（異常検知: > 10% で調査）
  - 平均応答時間
- **アラート条件**:
  - ログイン失敗率 > 20%（5分間）→ ブルートフォース攻撃の可能性
  - p95レイテンシ > 1秒
  - 特定IPからの連続失敗（10回以上）

### 可用性・冗長化
- **RPO/RTO**: N/A（ステートレスな認証API）
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
  - 関数名: `authenticateUser`, `validateCredentials`（camelCase）
  - 定数: `MAX_LOGIN_ATTEMPTS`（UPPER_SNAKE_CASE）

### コミット規約
```
feat(auth): Add signin endpoint with NextAuth.js

- Implement POST /api/auth/signin with Credentials provider
- Add bcrypt password verification
- Add audit logging for login attempts
- Add rate limiting for brute-force protection
```

### PR運用
- **レビュー観点**:
  - セキュリティ（パスワード検証、CSRF、レート制限）
  - エラーハンドリング
  - ログ出力
  - テストカバレッジ
- **マージ条件**:
  - ESLint/Prettier通過
  - ビルド成功
  - 最低1名のApprove

### 環境
| 環境 | URL | データベース | 備考 |
|-----|-----|------------|------|
| local | http://localhost:3001 | SQLite (dev.db) | 開発環境 |
| dev | （未設定） | PostgreSQL | 検証環境 |
| stg | （未設定） | PostgreSQL | ステージング |
| prod | （未設定） | PostgreSQL | 本番環境 |

### デプロイ手順
- **local**: `npm run dev`（自動リロード）
- **本番**: CI/CD未設定（Phase 5で実装予定）

---

## F. 連携仕様

### 内部連携: NextAuth.js

**設定ファイル**: `app/api/auth/[...nextauth]/route.ts`

```typescript
import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import { PrismaAdapter } from "@auth/prisma-adapter"
import { prisma } from "@/lib/prisma"
import bcrypt from "bcryptjs"
import { z } from "zod"

const credentialsSchema = z.object({
  email: z.string().email("有効なメールアドレスを入力してください").max(255),
  password: z.string().min(8, "パスワードは8文字以上である必要があります").max(128),
})

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        try {
          // バリデーション
          const validated = credentialsSchema.parse(credentials)

          // ユーザー取得
          const user = await prisma.user.findUnique({
            where: { email: validated.email },
            select: {
              id: true,
              email: true,
              passwordHash: true,
              name: true,
              role: true,
            },
          })

          if (!user) {
            // 監査ログ: ログイン失敗（ユーザー存在しない）
            await prisma.auditLog.create({
              data: {
                action: 'LOGIN_FAILED',
                entityType: 'User',
                entityId: null,
                userId: null,
                details: {
                  email: validated.email,
                  reason: 'USER_NOT_FOUND'
                },
              },
            })
            return null
          }

          // パスワード検証
          const isValid = await bcrypt.compare(validated.password, user.passwordHash)

          if (!isValid) {
            // 監査ログ: ログイン失敗（パスワード不一致）
            await prisma.auditLog.create({
              data: {
                action: 'LOGIN_FAILED',
                entityType: 'User',
                entityId: user.id,
                userId: user.id,
                details: {
                  email: user.email,
                  reason: 'INVALID_PASSWORD'
                },
              },
            })
            return null
          }

          // 監査ログ: ログイン成功
          await prisma.auditLog.create({
            data: {
              action: 'LOGIN_SUCCESS',
              entityType: 'User',
              entityId: user.id,
              userId: user.id,
              details: { email: user.email },
            },
          })

          return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role
          }
        } catch (error) {
          console.error('Authentication error:', error)
          return null
        }
      }
    })
  ],
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  pages: {
    signIn: "/login"
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.role = user.role
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        session.user.role = token.role as string
      }
      return session
    }
  }
})

export { handlers as GET, handlers as POST }
```

### 内部連携: Prisma

**クエリ**: 上記「データ設計」参照

---

## 開発フロー

### Step 0: キックオフ
- スコープ確認: NextAuth.js統合 + Credentials認証 + 監査ログ
- Must: 認証成功/失敗、セッション管理、監査ログ
- Should: レート制限、詳細なエラーメッセージ
- Could: OAuth連携（v2）
- DoD: テスト通過、セキュリティ要件充足、監査ログ記録確認

### Step 1: 仕様の確定
- ✅ 上記OpenAPI仕様で確定
- エラー形式、認証方式は既存APIと統一

### Step 2: 土台構築
1. NextAuth.js インストール:
   ```bash
   npm install next-auth@latest @auth/prisma-adapter bcryptjs
   npm install -D @types/bcryptjs
   ```
2. 環境変数設定（`.env.local`）:
   ```env
   NEXTAUTH_URL=http://localhost:3001
   NEXTAUTH_SECRET=your-super-secret-key-change-this-in-production
   ```
3. NextAuth.js設定ファイル作成: `app/api/auth/[...nextauth]/route.ts`
4. 認証ヘルパー作成: `lib/auth.ts`

### Step 3: 実装
1. **NextAuth.js設定** (`app/api/auth/[...nextauth]/route.ts`):
   - Credentials Provider設定
   - bcrypt検証ロジック
   - 監査ログ記録
   - セッション設定（JWT）
2. **バリデーション** (`schemas/authSchema.ts`):
   - Zodスキーマ定義（email, password）
3. **認証ヘルパー** (`lib/auth.ts`):
   - `requireAuth()` - セッション必須チェック
   - `requireRole(role)` - ロール別権限チェック
4. **エラーハンドリング**:
   - 汎用エラーメッセージ（認証情報漏洩防止）
   - レート制限（将来実装）

### Step 4: テスト
1. **ユニットテスト**（Jest）:
   - バリデーションスキーマのテスト
   - bcrypt検証ロジックのテスト
2. **API統合テスト**:
   - 正常系: ログイン成功、セッション確立
   - 異常系: メール存在しない、パスワード不一致、バリデーションエラー
   - 監査ログ記録確認（成功/失敗）
3. **セキュリティテスト**:
   - CSRF保護確認
   - ブルートフォース対策（レート制限）
   - セッションCookie属性確認（httpOnly, Secure, SameSite）

### Step 5: デプロイ・運用
1. local環境でテスト
2. NEXTAUTH_SECRETの本番用生成（`openssl rand -base64 32`）
3. 監視設定（ログイン失敗率、レイテンシ）
4. Runbook作成:
   - ブルートフォース攻撃時 → 特定IPのブロック
   - ログイン失敗率急増時 → DB/bcrypt処理の確認

---

## チケット詳細

### タイトル
`[Phase1-1] POST /api/auth/signin - ログイン実装`

### 目的
メールアドレスとパスワードによるユーザー認証を実行し、セッションを確立する。

### 対象エンドポイント
`POST /api/auth/signin`（上記OpenAPI仕様参照）

### 受け入れ条件
- [ ] 有効な認証情報でログインが成功する（200）
- [ ] セッションCookieが発行される（`next-auth.session-token`）
- [ ] 無効なメールアドレスでログイン失敗する（401）
- [ ] 無効なパスワードでログイン失敗する（401）
- [ ] バリデーションエラー時に詳細なエラーメッセージが返る（400）
- [ ] ログイン成功時にAuditLogに記録される（action: LOGIN_SUCCESS）
- [ ] ログイン失敗時にAuditLogに記録される（action: LOGIN_FAILED）
- [ ] 認証失敗時に汎用エラーメッセージが返る（メールアドレスの存在を推測できない）
- [ ] ログが構造化形式で出力される（request_id含む）
- [ ] ESLint/Prettierエラーなし
- [ ] ビルドが成功する

### 影響範囲
- **新規ファイル**:
  - `app/api/auth/[...nextauth]/route.ts`
  - `lib/auth.ts`
  - `schemas/authSchema.ts`
- **既存テーブル**: `users`（読み取りのみ）、`audit_logs`（書き込み）
- **環境変数**: NEXTAUTH_URL, NEXTAUTH_SECRET 追加

### 依存
- Prismaスキーマ実装完了（`users`テーブル）
- シードデータ作成（テストユーザー）
- bcryptjsインストール

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### サンプルレスポンス
```json
{
  "user": {
    "id": "cm12345678",
    "email": "user@example.com",
    "name": "山田太郎",
    "role": "USER"
  },
  "message": "ログインに成功しました"
}
```

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
