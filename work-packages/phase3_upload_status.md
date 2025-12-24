# Phase 3: アップロード・処理API 作業パッケージ - アップロード状態取得

**作成日**: 2025-12-17
**対象API**: GET /api/upload/[jobId]
**優先度**: 高

---

## A. 目的・スコープ

### 何を実現するAPIか
アップロードジョブの進捗状況をポーリングで取得し、フロントエンドでリアルタイム表示する。

### 今回の範囲
- ✅ MVPでやること
  - jobIdでUploadJobを取得
  - status, ocrResult, extractionResult, errorMessageを返す
  - 権限チェック（自分のジョブのみ取得可能）
- ❌ やらないこと
  - WebSocket/SSEによるリアルタイム通知（v2で検討）
  - 他ユーザーのジョブ取得（管理者のみ可能な管理画面は別途実装）
- ⚠️ Out of scope
  - ジョブのキャンセル（DELETE /api/upload/[jobId] は将来実装）

### 成功条件
- **パフォーマンス**: p95 < 100ms（シンプルなDB取得）
- **ポーリング頻度**: クライアント側で2秒間隔推奨

---

## B. 仕様（API仕様書）

### エンドポイント
```
GET /api/upload/[jobId]
```

### 認証・認可
- **必須**: NextAuth.js セッション
- **権限**: 自分のジョブのみ取得可能（userId一致チェック）

### パスパラメータ
| パラメータ | 型 | 必須 | 説明 |
|----------|---|-----|------|
| `jobId` | string | ✅ | UploadJobのID（CUID） |

### レスポンス

**成功 (200 OK)** - PENDING状態:
```json
{
  "job": {
    "id": "cm12345678",
    "status": "PENDING",
    "fileName": "contract.pdf",
    "fileSize": 2048000,
    "s3Url": "https://...",
    "description": "2024年度契約書",
    "createdAt": "2025-12-17T12:00:00.000Z",
    "updatedAt": "2025-12-17T12:00:00.000Z"
  }
}
```

**成功 (200 OK)** - PROCESSING状態:
```json
{
  "job": {
    "id": "cm12345678",
    "status": "PROCESSING",
    "fileName": "contract.pdf",
    "fileSize": 2048000,
    "s3Url": "https://...",
    "createdAt": "2025-12-17T12:00:00.000Z",
    "updatedAt": "2025-12-17T12:01:30.000Z"
  }
}
```

**成功 (200 OK)** - COMPLETED状態:
```json
{
  "job": {
    "id": "cm12345678",
    "status": "COMPLETED",
    "fileName": "contract.pdf",
    "fileSize": 2048000,
    "s3Url": "https://...",
    "ocrResult": "賃貸借契約書\n\n契約期間: 2024年1月1日〜2026年12月31日...",
    "extractionResult": {
      "contractNumber": "C-2024-001",
      "startDate": "2024-01-01",
      "endDate": "2026-12-31",
      "monthlyRent": 800000
    },
    "createdAt": "2025-12-17T12:00:00.000Z",
    "updatedAt": "2025-12-17T12:05:00.000Z"
  }
}
```

**成功 (200 OK)** - FAILED状態:
```json
{
  "job": {
    "id": "cm12345678",
    "status": "FAILED",
    "fileName": "contract.pdf",
    "fileSize": 2048000,
    "s3Url": "https://...",
    "errorMessage": "OCR処理に失敗しました: テキストを検出できませんでした",
    "createdAt": "2025-12-17T12:00:00.000Z",
    "updatedAt": "2025-12-17T12:03:00.000Z"
  }
}
```

**エラー (404 Not Found)** - ジョブが存在しない:
```json
{
  "error": {
    "code": "JOB_NOT_FOUND",
    "message": "指定されたジョブが見つかりません"
  },
  "request_id": "req_abc123"
}
```

**エラー (403 Forbidden)** - 他人のジョブ:
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "このジョブにアクセスする権限がありません"
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
- `200 OK` - ジョブ取得成功
- `401 Unauthorized` - 認証エラー
- `403 Forbidden` - 権限エラー
- `404 Not Found` - ジョブが存在しない

---

## C. データ設計

### 既存テーブル: `upload_jobs`

既存の `upload_jobs` テーブルを使用（変更なし）。

### クエリ
```typescript
const job = await prisma.uploadJob.findUnique({
  where: { id: jobId },
  select: {
    id: true,
    status: true,
    fileName: true,
    fileSize: true,
    s3Url: true,
    description: true,
    errorMessage: true,
    ocrResult: true,
    extractionResult: true,
    userId: true, // 権限チェック用
    createdAt: true,
    updatedAt: true,
  },
})

if (!job) {
  return NextResponse.json({ error: { code: 'JOB_NOT_FOUND', message: '...' } }, { status: 404 })
}

if (job.userId !== session.user.id) {
  return NextResponse.json({ error: { code: 'FORBIDDEN', message: '...' } }, { status: 403 })
}

// userId は返さない（セキュリティ）
const { userId, ...jobData } = job
return NextResponse.json({ job: jobData })
```

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 100ms（DB取得のみ）
- **ポーリング**: クライアント側で2秒間隔、最大5分間（150回）

### レート制限
- なし（GETは冪等なため制限不要、過剰ポーリングはクライアント側で制御）

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **認可**: userId一致チェック（他人のジョブは403）

### ログ
```json
{
  "level": "info",
  "timestamp": "2025-12-17T12:00:00.000Z",
  "request_id": "req_abc123",
  "user_id": "user123",
  "action": "get_job_status",
  "job_id": "cm12345678",
  "job_status": "PROCESSING",
  "duration_ms": 45
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
feat(api): Add upload job status endpoint

- Implement GET /api/upload/[jobId]
- Add authorization check (own jobs only)
- Add structured logging
```

### PR運用
- **レビュー観点**:
  - セキュリティ（認可チェック）
  - エラーハンドリング
  - ログ出力
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

### 内部連携: Prisma

**クエリ**: 上記「データ設計」参照

### 非同期処理
- このAPIは状態取得のみ（ステータス更新は行わない）

---

## 開発フロー

### Step 0: キックオフ
- スコープ: ジョブ状態取得 + 権限チェック
- DoD: テスト通過、権限チェック動作確認

### Step 1: 仕様確定
- ✅ 上記仕様で確定

### Step 2: 土台構築
- 不要（既存Prismaクライアント使用）

### Step 3: 実装
1. **API Route実装** (`app/api/upload/[jobId]/route.ts`):
   - 認証チェック
   - jobId で UploadJob 取得
   - userId 一致チェック
   - レスポンス返却（userId除外）
   - エラーハンドリング（404, 403）

### Step 4: テスト
1. **API統合テスト**:
   - 正常系: 自分のジョブ取得成功
   - 異常系: 存在しないジョブ（404）、他人のジョブ（403）、未認証（401）
   - 各ステータス（PENDING, PROCESSING, COMPLETED, FAILED）のレスポンス確認

### Step 5: デプロイ
- local環境でテスト後、本番デプロイ

---

## ✅ チケット詳細

### タイトル
`[Phase3-2] GET /api/upload/[jobId] - アップロード状態取得実装`

### 目的
アップロードジョブの進捗状況を取得し、フロントエンドでリアルタイム表示する。

### 対象エンドポイント
`GET /api/upload/[jobId]`

### 受け入れ条件
- [ ] 自分のジョブが正常に取得できる（200）
- [ ] 存在しないジョブは404エラー
- [ ] 他人のジョブは403エラー
- [ ] 未認証時は401エラー
- [ ] レスポンスに userId が含まれない（セキュリティ）
- [ ] 各ステータス（PENDING, PROCESSING, COMPLETED, FAILED）で正しいレスポンス
- [ ] ログが出力される
- [ ] ESLint/Prettierエラーなし

### 影響範囲
- **新規ファイル**: `app/api/upload/[jobId]/route.ts`
- **既存テーブル**: なし

### 依存
- API-1（POST /api/upload）実装完了

### サンプルリクエスト
```bash
curl -X GET http://localhost:3001/api/upload/cm12345678 \
  -H "Cookie: next-auth.session-token=xxx"
```

### サンプルレスポンス
```json
{
  "job": {
    "id": "cm12345678",
    "status": "COMPLETED",
    "fileName": "contract.pdf",
    "fileSize": 2048000,
    "s3Url": "https://...",
    "ocrResult": "賃貸借契約書\n\n...",
    "extractionResult": {
      "contractNumber": "C-2024-001",
      "startDate": "2024-01-01",
      "endDate": "2026-12-31"
    },
    "createdAt": "2025-12-17T12:00:00.000Z",
    "updatedAt": "2025-12-17T12:05:00.000Z"
  }
}
```

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
