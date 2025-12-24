# Phase 4-2: POST /api/analysis - AI契約分析API 作業パッケージ

**作成日**: 2025-12-17
**対象フェーズ**: Phase 4-2 (AI契約分析)
**前提条件**: Phase 1, 2, 3 完了済み

---

## A. 目的・スコープ

### 何を実現するAPIか
自然言語による契約データの統計・集計分析を提供し、ユーザーが「A社がオーナーの物件の、一店舗あたりの賃料平均を計算して」のような質問でデータ分析を実行できる。OpenAI GPT-4によるText-to-SQL生成により、自然言語をSQLクエリに変換し、安全に実行して結果を返す。

### 今回の範囲
- ✅ MVPでやること
  - 自然言語からのSQL生成（Text-to-SQL）
  - SQLセキュリティチェック（読み取り専用、危険な操作の禁止）
  - SQL実行とデータ取得
  - 統計結果の可視化データ生成（カウント、平均、合計、最小、最大）
  - LLMによる自然な回答生成
  - 分析履歴の記録（AnalysisHistory）
  - グラフ用データの整形
- ❌ やらないこと（将来対応）
  - 複雑な多段階JOIN（v2で対応）
  - リアルタイムダッシュボード（v2で対応）
  - 時系列分析・トレンド予測（v2で対応）
  - カスタムレポートのテンプレート保存（v2で対応）
- ⚠️ Out of scope
  - データの更新・削除操作（読み取り専用）
  - 外部データソースとの連携（フェーズ1は契約データのみ）

### 成功条件
- **分析精度**: 生成されたSQLが正しく実行される（評価用テストケース10問で90%以上）
- **レイテンシ**: p95 < 5秒（SQL生成 + 実行 + 回答生成）
- **セキュリティ**: 危険なSQL（DELETE, DROP, UPDATE等）は実行前に検出・拒否
- **ユーザー満足度**: 自然で分かりやすい回答が生成される（主観評価、80%以上の満足度）

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/analysis
```

### 認証・認可
- **必須**: NextAuth.js セッション（Cookie: next-auth.session-token）
- **ロール**: USER, MANAGER, ACCOUNTANT, ADMIN（全ロールOK）

### リクエスト
**Content-Type**: `application/json`

**ボディ**:
| フィールド名 | 型 | 必須 | 説明 | バリデーション |
|------------|---|-----|------|--------------|
| `question` | string | ✅ | 分析質問（自然言語） | 最小10文字、最大1000文字 |

**リクエスト例**:
```json
{
  "question": "A社がオーナーの物件の、一店舗あたりの賃料平均を計算して"
}
```

**curlコマンド例**:
```bash
curl -X POST http://localhost:3001/api/analysis \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "A社がオーナーの物件の、一店舗あたりの賃料平均を計算して"
  }'
```

### レスポンス

**成功 (200 OK)**:
```json
{
  "answer": "A社がオーナーの物件は23件あり、平均賃料は¥584,348です。\n\n**統計情報:**\n- 総件数: 23件\n- 平均賃料: ¥584,348\n- 賃料合計: ¥13,440,000\n- 最低賃料: ¥250,000（新宿店舗 3F）\n- 最高賃料: ¥980,000（渋谷オフィス 10F）\n\nA社は比較的高額な物件を多く保有しており、立地の良いエリアに集中しています。",
  "statistics": {
    "count": 23,
    "averageRent": 584348,
    "totalRent": 13440000,
    "minRent": 250000,
    "maxRent": 980000
  },
  "contracts": [
    {
      "id": "contract_001",
      "contractNumber": "C-2024-010",
      "propertyName": "渋谷店舗 1F",
      "propertyAddress": "東京都渋谷区渋谷1-1-1",
      "monthlyRent": 650000,
      "lessor": "A社不動産株式会社"
    },
    {
      "id": "contract_002",
      "contractNumber": "C-2024-023",
      "propertyName": "新宿オフィス 5F",
      "propertyAddress": "東京都新宿区新宿2-2-2",
      "monthlyRent": 820000,
      "lessor": "A社不動産株式会社"
    }
  ],
  "query": "SELECT COUNT(*) as count, AVG(cd.monthly_rent) as average_rent, SUM(cd.monthly_rent) as total_rent, MIN(cd.monthly_rent) as min_rent, MAX(cd.monthly_rent) as max_rent FROM contracts c JOIN contract_details cd ON cd.contract_id = c.id JOIN contract_parties cp ON cp.contract_id = c.id WHERE cp.party_type = 'LESSOR' AND cp.name LIKE '%A社%' AND c.status = 'ACTIVE'",
  "chartData": {
    "type": "bar",
    "labels": ["渋谷店舗 1F", "新宿オフィス 5F", "品川倉庫 1F", "六本木ビル 3F", "池袋店舗 2F"],
    "values": [650000, 820000, 450000, 980000, 550000]
  },
  "tokensUsed": 800,
  "processingTime": 2800,
  "analysisId": "analysis_xxx"
}
```

**エラー (400 Bad Request)** - 質問が短すぎる:
```json
{
  "error": {
    "code": "QUESTION_TOO_SHORT",
    "message": "分析質問は最低10文字必要です",
    "details": [
      "現在の文字数: 5",
      "必要な文字数: 10"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (400 Bad Request)** - 質問が長すぎる:
```json
{
  "error": {
    "code": "QUESTION_TOO_LONG",
    "message": "分析質問は最大1000文字です",
    "details": [
      "現在の文字数: 1050",
      "最大文字数: 1000"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (400 Bad Request)** - 危険なSQL検出:
```json
{
  "error": {
    "code": "UNSAFE_SQL",
    "message": "安全でないSQL操作が検出されました",
    "details": [
      "検出されたキーワード: DELETE",
      "許可されている操作: SELECT のみ"
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

**エラー (429 Too Many Requests)** - レート制限:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "分析回数の上限に達しました",
    "details": [
      "上限: 20回/分",
      "リトライまでの時間: 60秒"
    ]
  },
  "request_id": "req_abc123",
  "retry_after": 60
}
```

**エラー (500 Internal Server Error)** - SQL実行エラー:
```json
{
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "分析処理に失敗しました",
    "details": [
      "SQLの実行に失敗しました。質問を変更して再度お試しください。"
    ]
  },
  "request_id": "req_abc123"
}
```

### ステータスコード規約
- `200 OK` - 分析成功
- `400 Bad Request` - 質問不正、危険なSQL検出、バリデーションエラー
- `401 Unauthorized` - 認証エラー
- `429 Too Many Requests` - レート制限
- `500 Internal Server Error` - OpenAI APIエラー、DBエラー、SQL実行エラー

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

### 既存テーブル: `contracts`, `contract_details`, `contract_parties`
AI契約分析では既存の契約関連テーブルを分析対象とする。変更なし。

### 新規テーブル: `analysis_histories`
分析履歴を保存するテーブル。

```prisma
model AnalysisHistory {
  id          String    @id @default(cuid())
  userId      String    @map("user_id")
  question    String    @db.Text // 分析質問
  answer      String    @db.Text // AI生成回答
  query       String    @db.Text // 生成されたSQL
  resultCount Int       @map("result_count") // 結果件数
  statistics  Json?     // 統計情報（JSON）
  tokensUsed  Int       @map("tokens_used") // 使用トークン数
  processingTime Int    @map("processing_time") // 処理時間（ミリ秒）
  createdAt   DateTime  @default(now()) @map("created_at")

  user        User      @relation(fields: [userId], references: [id])

  @@index([userId])
  @@index([createdAt])
  @@map("analysis_histories")
}
```

### データのライフサイクル
1. **分析実行**: POST /api/analysis で自動的にAnalysisHistoryに保存
2. **履歴取得**: 将来的にGET /api/analysis/historyで取得可能（v2）
3. **履歴削除**: 6ヶ月経過後に定期削除バッチで削除

### 監査項目
- AnalysisHistory に分析履歴を自動記録
- AuditLog には記録しない（分析は閲覧のみのため）

### データ保持期間
- **AnalysisHistory**: 6ヶ月間保持（定期削除バッチで古いデータを削除）

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 5秒（SQL生成: 2秒、SQL実行: 1秒、回答生成: 2秒）
- **タイムアウト**: 10秒
- **スループット**: 20 req/min（全ユーザー合計）
- **同時実行**: 最大5リクエスト同時処理

### レート制限・スロットリング
- **ユーザーごと制限**: 20回/分
- **429エラー**: `Retry-After: 60`（1分後に再試行）
- 実装方法: Redisまたはメモリベースのレート制限（simple-rate-limiter使用）

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **入力検証**:
  - 質問長: 10〜1000文字
  - XSS対策: 質問のサニタイズ
- **SQLインジェクション対策**:
  - 生成されたSQLの厳格なホワイトリストチェック
  - 許可キーワード: SELECT, FROM, WHERE, JOIN, GROUP BY, ORDER BY, LIMIT, COUNT, SUM, AVG, MIN, MAX
  - 禁止キーワード: DELETE, DROP, UPDATE, INSERT, ALTER, CREATE, TRUNCATE, EXEC, EXECUTE
  - セミコロン（;）の禁止（複数クエリ実行防止）
- **プロンプトインジェクション対策**:
  - システムプロンプトとユーザー入力を明確に分離
  - ユーザー入力のエスケープ処理
- **データベースアクセス制限**:
  - 読み取り専用ユーザーでの実行（READ ONLY TRANSACTION）
  - タイムアウト設定（5秒）

### ログ/監視
- **ログ形式**: JSON構造化ログ
  ```json
  {
    "level": "info",
    "timestamp": "2025-12-17T12:00:00.000Z",
    "request_id": "req_abc123",
    "user_id": "user123",
    "action": "analysis",
    "question": "A社がオーナーの物件の、一店舗あたりの賃料平均を計算して",
    "generated_sql": "SELECT COUNT(*) as count, AVG(cd.monthly_rent) as average_rent...",
    "result_count": 23,
    "tokens_used": 800,
    "processing_time": 2800
  }
  ```
- **メトリクス**:
  - 分析成功率（target: > 90%）
  - 平均処理時間
  - SQL実行エラー率
  - OpenAI APIエラー率
- **アラート条件**:
  - エラー率 > 10%（5分間）
  - p95レイテンシ > 8秒
  - SQL実行エラー頻発
  - OpenAI API接続エラー

### 可用性・冗長化
- **RPO/RTO**: N/A（ステートレスな分析API）
- **リトライ**: OpenAI APIエラー時は3回リトライ（指数バックオフ）

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
  - 関数名: `generateSQL`, `validateSQL`, `executeSQL`（camelCase）
  - 定数: `ALLOWED_SQL_KEYWORDS`, `FORBIDDEN_SQL_KEYWORDS`（UPPER_SNAKE_CASE）

### コミット規約
```
feat(api): Add AI analysis endpoint

- Implement POST /api/analysis with Text-to-SQL
- Add SQL security checks (whitelist/blacklist)
- Add LLM answer generation with GPT-4
- Add analysis history recording
```

### PR運用
- **レビュー観点**:
  - セキュリティ（SQLインジェクション対策、ホワイトリストチェック）
  - 性能（SQL実行のタイムアウト設定）
  - エラーハンドリング
  - ログ出力
- **マージ条件**:
  - ESLint/Prettier通過
  - ビルド成功
  - 最低1名のApprove

### 環境
| 環境 | URL | データベース | OpenAI API |
|-----|-----|------------|-----------|
| local | http://localhost:3001 | PostgreSQL (dev) | 開発用APIキー |
| dev | （未設定） | PostgreSQL | 開発用APIキー |
| stg | （未設定） | PostgreSQL | ステージング用APIキー |
| prod | （未設定） | PostgreSQL | 本番用APIキー |

### デプロイ手順
- **local**: `npm run dev`（自動リロード）
- **本番**: CI/CD未設定（Phase 5で実装予定）

---

## F. 連携仕様

### 外部連携: OpenAI GPT-4（Text-to-SQL）

**SDK**: `openai` v4

**認証**:
```typescript
import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
})
```

**プロンプト設計（Text-to-SQL）**:
```typescript
const systemPrompt = `
あなたはPostgreSQLのエキスパートです。ユーザーからの自然言語の質問を、正確で安全なSQLクエリに変換してください。

【データベーススキーマ】
- contracts (契約テーブル)
  - id: 契約ID
  - contract_number: 契約番号
  - type: 契約種別 (RENTAL/RENEWAL/MEMORANDUM)
  - status: ステータス (ACTIVE/EXPIRED/TERMINATED)
  - start_date: 開始日
  - end_date: 終了日
  - renewal_type: 更新条件
  - notice_period_months: 解約予告期間（月数）

- contract_details (契約詳細テーブル)
  - id: ID
  - contract_id: 契約ID (外部キー)
  - property_address: 物件住所
  - property_name: 物件名
  - property_area: 面積
  - property_usage: 用途
  - monthly_rent: 月額賃料
  - deposit: 敷金
  - key_money: 礼金
  - management_fee: 管理費

- contract_parties (契約当事者テーブル)
  - id: ID
  - contract_id: 契約ID (外部キー)
  - party_type: 当事者種別 (LESSOR/LESSEE)
  - name: 名前
  - address: 住所
  - phone_number: 電話番号

【SQLルール】
1. SELECT文のみ使用可能（DELETE, UPDATE, INSERT, DROP等は禁止）
2. 必要に応じてJOINを使用
3. 集計関数（COUNT, AVG, SUM, MIN, MAX）を適切に使用
4. WHERE句で適切にフィルタリング
5. GROUP BYやORDER BYを適切に使用
6. LIMITで結果件数を制限（デフォルト: 100件）
7. カラム名はスネークケース（例: monthly_rent）
8. テーブルエイリアスを使用（c, cd, cp）
9. セミコロン（;）は使用しない

【回答形式】
SQLクエリのみを返してください。説明文は不要です。
`

const userPrompt = `
次の質問をPostgreSQLのSELECT文に変換してください。

【質問】
${question}

【SQL】
`

const response = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: userPrompt },
  ],
  temperature: 0, // 決定論的な出力
  max_tokens: 500,
})

const generatedSQL = response.choices[0].message.content!.trim()
```

**回答生成プロンプト**:
```typescript
const answerSystemPrompt = `
あなたは不動産契約管理システムのAIアシスタントです。
ユーザーからの分析質問に対して、SQLの実行結果を元に正確で分かりやすい回答を生成してください。

回答のルール:
- 統計情報（件数、平均、合計等）を明確に示す
- 金額は千円単位のカンマ区切りで表示（例: ¥584,348）
- 日付はYYYY年MM月DD日形式で表示
- 箇条書きで読みやすく整理する
- 重要なポイントを強調する
- 分析結果から得られる洞察を含める

回答の形式:
1. 要約（分析結果の概要）
2. 詳細統計情報
3. 補足情報・洞察
`

const answerUserPrompt = `
【ユーザーの質問】
${question}

【SQL実行結果】
${JSON.stringify(results, null, 2)}

【統計情報】
${JSON.stringify(statistics, null, 2)}

上記の情報を元に、ユーザーの質問に回答してください。
`

const answerResponse = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: [
    { role: 'system', content: answerSystemPrompt },
    { role: 'user', content: answerUserPrompt },
  ],
  temperature: 0.3,
  max_tokens: 1000,
})

const answer = answerResponse.choices[0].message.content!
```

### SQLセキュリティチェック

**ホワイトリスト・ブラックリストチェック**:
```typescript
// lib/sqlSecurity.ts
const ALLOWED_KEYWORDS = [
  'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER',
  'ON', 'AND', 'OR', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL', 'NOT',
  'GROUP', 'BY', 'ORDER', 'ASC', 'DESC', 'LIMIT', 'OFFSET',
  'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT',
  'AS', 'CAST', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
]

const FORBIDDEN_KEYWORDS = [
  'DELETE', 'DROP', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE',
  'EXEC', 'EXECUTE', 'DECLARE', 'CURSOR', 'FETCH',
  'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK',
  'PROCEDURE', 'FUNCTION', 'TRIGGER', 'VIEW', 'INDEX'
]

export function validateSQL(sql: string): { valid: boolean; error?: string } {
  const upperSQL = sql.toUpperCase()

  // セミコロンチェック（複数クエリ実行防止）
  if (sql.includes(';')) {
    return { valid: false, error: 'セミコロン（;）は使用できません' }
  }

  // 禁止キーワードチェック
  for (const keyword of FORBIDDEN_KEYWORDS) {
    if (upperSQL.includes(keyword)) {
      return { valid: false, error: `禁止されたキーワードが含まれています: ${keyword}` }
    }

  // SELECTで始まることを確認
  if (!upperSQL.trim().startsWith('SELECT')) {
    return { valid: false, error: 'SQLはSELECTで始まる必要があります' }
  }

  // コメント記号チェック（SQLインジェクション防止）
  if (sql.includes('--') || sql.includes('/*') || sql.includes('*/')) {
    return { valid: false, error: 'SQLコメントは使用できません' }
  }

  return { valid: true }
}
```

### 内部連携: Prisma（SQL実行）

**読み取り専用トランザクション**:
```typescript
import { prisma } from '@/lib/prisma'

// SQL実行（読み取り専用、タイムアウト5秒）
const results = await prisma.$queryRawUnsafe<any[]>(
  `SET TRANSACTION READ ONLY; ${generatedSQL}`
)

// タイムアウト設定（Prismaクライアント）
const prismaWithTimeout = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
  // クエリタイムアウト: 5秒
  log: ['query', 'error'],
  errorFormat: 'pretty',
})
```

**統計情報の計算**:
```typescript
function calculateStatistics(results: any[]): Statistics {
  if (results.length === 0) {
    return { count: 0 }
  }

  // 数値カラムの検出
  const firstRow = results[0]
  const numericColumns = Object.keys(firstRow).filter(key => {
    const value = firstRow[key]
    return typeof value === 'number' && !isNaN(value)
  })

  const statistics: Statistics = {
    count: results.length,
  }

  // 各数値カラムの統計を計算
  for (const col of numericColumns) {
    const values = results.map(r => r[col]).filter(v => v != null)
    if (values.length > 0) {
      statistics[`${col}_avg`] = values.reduce((a, b) => a + b, 0) / values.length
      statistics[`${col}_sum`] = values.reduce((a, b) => a + b, 0)
      statistics[`${col}_min`] = Math.min(...values)
      statistics[`${col}_max`] = Math.max(...values)
    }
  }

  return statistics
}
```

**分析履歴の保存**:
```typescript
await prisma.analysisHistory.create({
  data: {
    userId: session.user.id,
    question,
    answer,
    query: generatedSQL,
    resultCount: results.length,
    statistics,
    tokensUsed: response.usage?.total_tokens || 0,
    processingTime: Date.now() - startTime,
  },
})
```

---

## 開発フロー

### Step 0: キックオフ
- スコープ確認: Text-to-SQL + セキュリティチェック + SQL実行 + 回答生成
- Must: 自然言語分析、SQL生成、セキュリティチェック、統計計算
- Should: 分析履歴記録、グラフデータ生成
- Could: カスタムレポートテンプレート（v2）
- DoD: SQL生成精度90%以上、レイテンシ5秒以内、セキュリティチェック完備

### Step 1: 仕様の確定
- ✅ 上記OpenAPI仕様で確定
- エラー形式、認証方式は既存APIと統一

### Step 2: 土台構築
1. **Prismaスキーマ更新**:
   ```bash
   # AnalysisHistory モデルをschema.prismaに追加
   npx prisma migrate dev --name add_analysis_history
   npx prisma generate
   ```

2. **OpenAI SDK インストール**（既にインストール済み）:
   ```bash
   npm install openai
   ```

3. **環境変数設定**（`.env.local`）:
   ```env
   OPENAI_API_KEY=sk-...
   DATABASE_URL="postgresql://user:password@localhost:5432/contract_manage"
   ```

### Step 3: 実装
1. **Text-to-SQL生成関数** (`lib/textToSQL.ts`):
   - `generateSQL(question: string): Promise<string>` - 自然言語をSQLに変換

2. **SQLセキュリティチェック関数** (`lib/sqlSecurity.ts`):
   - `validateSQL(sql: string): { valid: boolean; error?: string }` - SQLの安全性チェック

3. **SQL実行関数** (`lib/sqlExecution.ts`):
   - `executeSQL(sql: string): Promise<any[]>` - 読み取り専用でSQL実行

4. **統計計算関数** (`lib/statistics.ts`):
   - `calculateStatistics(results: any[]): Statistics` - 統計情報の計算

5. **回答生成関数** (`lib/answerGeneration.ts`):
   - `generateAnalysisAnswer(question: string, results: any[], statistics: Statistics): Promise<string>`

6. **API Route実装** (`app/api/analysis/route.ts`):
   - 認証チェック（NextAuth）
   - 質問バリデーション（10〜1000文字）
   - レート制限チェック
   - Text-to-SQL生成（OpenAI GPT-4）
   - SQLセキュリティチェック（ホワイトリスト/ブラックリスト）
   - SQL実行（読み取り専用トランザクション）
   - 統計計算
   - 回答生成（OpenAI GPT-4）
   - 分析履歴記録（AnalysisHistory）
   - エラーハンドリング

### Step 4: テスト
1. **ユニットテスト**（Jest）:
   - `textToSQL.ts` の各関数
   - `sqlSecurity.ts` の各関数（特にブラックリストチェック）
   - `sqlExecution.ts` の各関数
   - `statistics.ts` の各関数

2. **API統合テスト**:
   - 正常系: 自然言語分析成功、SQL生成、SQL実行、回答生成
   - 異常系: 質問不正（短すぎる/長すぎる）、危険なSQL検出、認証エラー、SQLエラー
   - セキュリティテスト: DELETE, DROP, UPDATE等の禁止キーワード検出

3. **SQL生成精度評価**:
   - テストケース10問を用意（例: 「A社がオーナーの物件の平均賃料」「2024年に契約した物件の敷金合計」等）
   - 各テストケースで生成されたSQLが正しく実行されるか評価
   - 目標精度: 90%以上（10問中9問以上）

4. **負荷テスト**（オプション）:
   - 同時5リクエスト、p95 < 5秒を確認

### Step 5: デプロイ・運用
1. local環境でテスト
2. PostgreSQLで読み取り専用ユーザーを作成（オプション）
3. 監視ダッシュボード確認（レイテンシ、エラー率、SQL実行成功率）
4. Runbook作成:
   - OpenAI APIエラー時 → APIキー確認、リトライ
   - SQL実行エラー時 → 生成されたSQLをログで確認、プロンプトチューニング
   - セキュリティアラート時 → 危険なSQLの試行をログで確認、ブラックリスト更新

---

## チケット詳細

### タイトル
`[Phase4-2] POST /api/analysis - AI契約分析実装`

### 目的
自然言語による契約データの統計・集計分析を提供し、ユーザーが直感的にデータ分析を実行できるようにする。

### 対象エンドポイント
`POST /api/analysis`（上記OpenAPI仕様参照）

### 受け入れ条件
- [ ] 自然言語質問での契約データ分析が成功する
- [ ] OpenAI GPT-4でText-to-SQL生成ができる
- [ ] 生成されたSQLがセキュリティチェックを通過する
- [ ] 読み取り専用トランザクションでSQL実行ができる
- [ ] 統計情報（カウント、平均、合計、最小、最大）が計算される
- [ ] LLM（GPT-4）で自然な回答が生成される
- [ ] 分析履歴がAnalysisHistoryに保存される
- [ ] 以下のバリデーションが動作する:
  - [ ] 質問が短すぎる（10文字未満） → 400エラー
  - [ ] 質問が長すぎる（1000文字超過） → 400エラー
  - [ ] 危険なSQL検出（DELETE, DROP, UPDATE等） → 400エラー
  - [ ] レート制限超過 → 429エラー
- [ ] 未認証時に401エラーが返る
- [ ] OpenAI APIエラー時に500エラーが返る
- [ ] SQLインジェクション対策が機能する
- [ ] ログが構造化形式で出力される（request_id含む）
- [ ] SQL生成精度評価で90%以上を達成
- [ ] ESLint/Prettierエラーなし
- [ ] ビルドが成功する

### 影響範囲
- **新規ファイル**:
  - `app/api/analysis/route.ts`
  - `lib/textToSQL.ts`
  - `lib/sqlSecurity.ts`
  - `lib/sqlExecution.ts`
  - `lib/statistics.ts`
  - `lib/answerGeneration.ts`（分析用）
- **新規テーブル**: `analysis_histories`
- **環境変数**: OPENAI_API_KEY（既存）

### 依存
- OpenAI APIキー発行完了
- `openai` パッケージインストール完了
- Prisma設定完了

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/analysis \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "A社がオーナーの物件の、一店舗あたりの賃料平均を計算して"
  }'
```

### サンプルレスポンス
上記「仕様」参照

---

## 🔧 技術補足

### Text-to-SQLの精度向上のためのプロンプトチューニング

**Few-shot Learningの追加**:
```typescript
const fewShotExamples = `
【例1】
質問: 2024年に契約した物件の件数を教えて
SQL: SELECT COUNT(*) as count FROM contracts WHERE EXTRACT(YEAR FROM start_date) = 2024

【例2】
質問: 渋谷エリアの物件の平均賃料は？
SQL: SELECT AVG(cd.monthly_rent) as average_rent FROM contracts c JOIN contract_details cd ON cd.contract_id = c.id WHERE cd.property_address LIKE '%渋谷%' AND c.status = 'ACTIVE'

【例3】
質問: A社がオーナーの物件を賃料順に表示して
SQL: SELECT c.contract_number, cd.property_name, cd.monthly_rent, cp.name as lessor FROM contracts c JOIN contract_details cd ON cd.contract_id = c.id JOIN contract_parties cp ON cp.contract_id = c.id WHERE cp.party_type = 'LESSOR' AND cp.name LIKE '%A社%' ORDER BY cd.monthly_rent DESC LIMIT 100
`

// システムプロンプトに追加
const systemPromptWithExamples = systemPrompt + '\n' + fewShotExamples
```

### SQLインジェクション対策の多層防御

1. **ホワイトリスト/ブラックリストチェック**（第1層）
2. **Prismaのパラメータ化クエリ**（第2層、可能な場合）
3. **読み取り専用トランザクション**（第3層）
4. **データベースユーザー権限制限**（第4層、オプション）

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
