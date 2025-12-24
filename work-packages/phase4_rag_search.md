# Phase 4-1: POST /api/rag - RAG検索API 作業パッケージ

**作成日**: 2025-12-17
**対象フェーズ**: Phase 4-1 (RAG検索)
**前提条件**: Phase 1, 2, 3 完了済み、Contract Embeddingデータ作成完了

---

## A. 目的・スコープ

### 何を実現するAPIか
自然言語による契約検索機能を提供し、ユーザーが「来年3月末に満了する賃貸契約を教えて」のような自然な質問で契約情報を検索できる。OpenAI Embeddings APIとPostgreSQL pgvectorを使用したRAG（Retrieval-Augmented Generation）検索により、関連性の高い契約情報を検索し、LLMで自然な回答を生成する。

### 今回の範囲
- ✅ MVPでやること
  - 自然言語クエリのEmbedding生成（OpenAI Embeddings API）
  - PostgreSQL pgvectorによるベクトル類似度検索
  - 上位10件の関連契約取得
  - LLMによる自然な回答生成（OpenAI GPT-4）
  - 検索履歴の記録（SearchHistory）
  - 関連度スコアの表示
- ❌ やらないこと（将来対応）
  - 複雑なフィルタリングの組み合わせ（v2で対応）
  - 検索結果のパーソナライゼーション（v2で対応）
  - 検索クエリの自動補完・サジェスト（v2で対応）
  - 検索結果のキャッシング（v2で対応）
- ⚠️ Out of scope
  - 画像・音声による検索（将来検討）
  - 多言語対応（フェーズ1は日本語のみ）

### 成功条件
- **検索精度**: 関連性の高い契約が上位3件に表示される（評価用テストケース10問で80%以上）
- **レイテンシ**: p95 < 5秒（Embedding生成 + ベクトル検索 + LLM回答生成）
- **関連度スコア**: 上位契約の類似度スコア > 0.7（70%以上）
- **ユーザー満足度**: 自然な回答が生成される（主観評価、80%以上の満足度）

---

## B. 仕様（API仕様書）

### エンドポイント
```
POST /api/rag
```

### 認証・認可
- **必須**: NextAuth.js セッション（Cookie: next-auth.session-token）
- **ロール**: USER, MANAGER, ACCOUNTANT, ADMIN（全ロールOK）

### リクエスト
**Content-Type**: `application/json`

**ボディ**:
| フィールド名 | 型 | 必須 | 説明 | バリデーション |
|------------|---|-----|------|--------------|
| `query` | string | ✅ | 検索クエリ（自然言語） | 最小5文字、最大500文字 |
| `limit` | number | ❌ | 取得件数（デフォルト: 10） | 最大20件 |

**リクエスト例**:
```json
{
  "query": "来年3月末に満了する賃貸契約を教えて",
  "limit": 10
}
```

**curlコマンド例**:
```bash
curl -X POST http://localhost:3001/api/rag \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "来年3月末に満了する賃貸契約を教えて",
    "limit": 10
  }'
```

### レスポンス

**成功 (200 OK)**:
```json
{
  "answer": "2026年3月末（2026-03-31）に満了する賃貸契約は5件見つかりました。以下がその一覧です：\n\n1. **C-2024-089: 渋谷店舗 1F**\n   - 賃料: ¥800,000\n   - 満了日: 2026-03-31\n   - 更新条件: 自動更新\n\n2. **C-2024-102: 品川オフィス 7F**\n   - 賃料: ¥620,000\n   - 満了日: 2026-03-31\n   - 更新条件: 合意更新\n\n3. **C-2024-078: 新宿店舗 2F**\n   - 賃料: ¥950,000\n   - 満了日: 2026-03-31\n   - 更新条件: 自動更新\n\nこれらの契約は更新期限が迫っています。更新または解約の意思決定が必要です。",
  "contracts": [
    {
      "id": "contract_001",
      "contractNumber": "C-2024-089",
      "propertyName": "渋谷店舗 1F",
      "propertyAddress": "東京都渋谷区渋谷1-1-1",
      "startDate": "2024-04-01T00:00:00.000Z",
      "endDate": "2026-03-31T00:00:00.000Z",
      "monthlyRent": 800000,
      "status": "ACTIVE",
      "verificationStatus": "VERIFIED",
      "relevanceScore": 0.98,
      "excerpt": "賃貸借契約書。賃料月額800,000円。契約期間は2024年4月1日から2026年3月31日まで..."
    },
    {
      "id": "contract_002",
      "contractNumber": "C-2024-102",
      "propertyName": "品川オフィス 7F",
      "propertyAddress": "東京都品川区大崎1-2-3",
      "startDate": "2024-04-01T00:00:00.000Z",
      "endDate": "2026-03-31T00:00:00.000Z",
      "monthlyRent": 620000,
      "status": "ACTIVE",
      "verificationStatus": "VERIFIED",
      "relevanceScore": 0.96,
      "excerpt": "賃貸借契約書。賃料月額620,000円。契約期間は2024年4月1日から2026年3月31日まで..."
    }
  ],
  "searchId": "search_xxx",
  "totalResults": 5,
  "tokensUsed": 1250,
  "processingTime": 3200
}
```

**エラー (400 Bad Request)** - クエリが短すぎる:
```json
{
  "error": {
    "code": "QUERY_TOO_SHORT",
    "message": "検索クエリは最低5文字必要です",
    "details": [
      "現在の文字数: 2",
      "必要な文字数: 5"
    ]
  },
  "request_id": "req_abc123"
}
```

**エラー (400 Bad Request)** - クエリが長すぎる:
```json
{
  "error": {
    "code": "QUERY_TOO_LONG",
    "message": "検索クエリは最大500文字です",
    "details": [
      "現在の文字数: 520",
      "最大文字数: 500"
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

**エラー (404 Not Found)** - 関連契約が見つからない:
```json
{
  "answer": "申し訳ございません。ご質問に関連する契約が見つかりませんでした。検索条件を変更してお試しください。",
  "contracts": [],
  "searchId": "search_xxx",
  "totalResults": 0,
  "tokensUsed": 800,
  "processingTime": 2500
}
```

**エラー (429 Too Many Requests)** - レート制限:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "検索回数の上限に達しました",
    "details": [
      "上限: 30回/分",
      "リトライまでの時間: 60秒"
    ]
  },
  "request_id": "req_abc123",
  "retry_after": 60
}
```

**エラー (500 Internal Server Error)** - OpenAI API障害:
```json
{
  "error": {
    "code": "SEARCH_FAILED",
    "message": "検索処理に失敗しました",
    "details": [
      "内部エラーが発生しました。しばらく経ってから再度お試しください。"
    ]
  },
  "request_id": "req_abc123"
}
```

### ステータスコード規約
- `200 OK` - 検索成功（関連契約が0件でも200を返す）
- `400 Bad Request` - クエリ不正、バリデーションエラー
- `401 Unauthorized` - 認証エラー
- `429 Too Many Requests` - レート制限
- `500 Internal Server Error` - OpenAI APIエラー、DBエラー、pgvectorエラー

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

### 既存テーブル: `contracts`
RAG検索では既存の `contracts` テーブルを検索対象とする。変更なし。

### 新規テーブル: `contract_embeddings`
契約情報のEmbeddingを保存するテーブル。事前にバッチ処理で生成しておく。

```prisma
model ContractEmbedding {
  id          String   @id @default(cuid())
  contractId  String   @unique @map("contract_id")
  embedding   Unsupported("vector(1536)") // pgvector (OpenAI text-embedding-3-small: 1536次元)
  content     String   @db.Text // 検索用のテキストコンテンツ（契約番号、物件名、住所、賃料等）
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")

  contract    Contract @relation(fields: [contractId], references: [id], onDelete: Cascade)

  @@index([contractId])
  @@map("contract_embeddings")
}
```

**content フィールドの構成**:
```
契約番号: C-2024-089
契約種別: 賃貸借契約
物件名: 渋谷店舗 1F
住所: 東京都渋谷区渋谷1-1-1
契約期間: 2024年4月1日 ～ 2026年3月31日
賃料: 月額800,000円
敷金: 2,400,000円
貸主: 株式会社ABC不動産
借主: 株式会社XYZ商事
更新条件: 自動更新
解約予告期間: 3ヶ月前
```

### 新規テーブル: `search_histories`
検索履歴を保存するテーブル。

```prisma
model SearchHistory {
  id          String    @id @default(cuid())
  userId      String    @map("user_id")
  query       String    // 検索クエリ
  answer      String    @db.Text // AI生成回答
  resultCount Int       @map("result_count") // 検索結果件数
  tokensUsed  Int       @map("tokens_used") // 使用トークン数
  processingTime Int    @map("processing_time") // 処理時間（ミリ秒）
  createdAt   DateTime  @default(now()) @map("created_at")

  user        User      @relation(fields: [userId], references: [id])

  @@index([userId])
  @@index([createdAt])
  @@map("search_histories")
}
```

### pgvector拡張の有効化
PostgreSQLでpgvector拡張を有効化する必要がある。

```sql
-- PostgreSQLでpgvector拡張を有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- contract_embeddingsテーブルのインデックス作成（HNSW）
CREATE INDEX ON contract_embeddings USING hnsw (embedding vector_cosine_ops);
```

### データのライフサイクル
1. **Embedding作成**: 契約作成時（POST /api/extraction）または別途バッチ処理で実行
2. **Embedding更新**: 契約更新時に再生成
3. **Embedding削除**: 契約削除時にCascadeで削除
4. **検索履歴保存**: 検索実行時に自動保存

### 監査項目
- SearchHistory に検索履歴を自動記録
- AuditLog には記録しない（検索は閲覧のみのため）

### データ保持期間
- **ContractEmbedding**: 契約と同じライフサイクル
- **SearchHistory**: 6ヶ月間保持（定期削除バッチで古いデータを削除）

---

## D. 非機能要件

### 性能目標
- **レイテンシ**: p95 < 5秒（Embedding生成: 1秒、ベクトル検索: 0.5秒、LLM回答生成: 3秒）
- **タイムアウト**: 10秒
- **スループット**: 30 req/min（全ユーザー合計）
- **同時実行**: 最大10リクエスト同時処理

### レート制限・スロットリング
- **ユーザーごと制限**: 30回/分
- **429エラー**: `Retry-After: 60`（1分後に再試行）
- 実装方法: Redisまたはメモリベースのレート制限（simple-rate-limiter使用）

### セキュリティ
- **認証**: NextAuth.js セッション必須
- **入力検証**:
  - クエリ長: 5〜500文字
  - XSS対策: クエリのサニタイズ
- **OpenAI APIキー**:
  - 環境変数で管理
  - ログに出力しない
- **プロンプトインジェクション対策**:
  - システムプロンプトとユーザー入力を明確に分離
  - ユーザー入力のエスケープ処理

### ログ/監視
- **ログ形式**: JSON構造化ログ
  ```json
  {
    "level": "info",
    "timestamp": "2025-12-17T12:00:00.000Z",
    "request_id": "req_abc123",
    "user_id": "user123",
    "action": "rag_search",
    "query": "来年3月末に満了する賃貸契約を教えて",
    "result_count": 5,
    "tokens_used": 1250,
    "processing_time": 3200,
    "top_relevance_score": 0.98
  }
  ```
- **メトリクス**:
  - 検索成功率（target: > 95%）
  - 平均処理時間
  - 平均関連度スコア
  - OpenAI APIエラー率
- **アラート条件**:
  - エラー率 > 5%（5分間）
  - p95レイテンシ > 8秒
  - OpenAI API接続エラー

### 可用性・冗長化
- **RPO/RTO**: N/A（ステートレスな検索API）
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
  - 関数名: `searchContracts`, `generateAnswer`（camelCase）
  - 定数: `MAX_QUERY_LENGTH`（UPPER_SNAKE_CASE）

### コミット規約
```
feat(api): Add RAG search endpoint

- Implement POST /api/rag with OpenAI Embeddings
- Add pgvector integration for similarity search
- Add LLM answer generation with GPT-4
- Add search history recording
```

### PR運用
- **レビュー観点**:
  - セキュリティ（プロンプトインジェクション対策、認証）
  - 性能（ベクトル検索のクエリ最適化）
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

### 外部連携1: OpenAI Embeddings API

**SDK**: `openai` v4

**認証**:
```typescript
import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
})
```

**Embedding生成処理**:
```typescript
// クエリをEmbeddingに変換
const embeddingResponse = await openai.embeddings.create({
  model: 'text-embedding-3-small', // 1536次元
  input: query,
})

const queryEmbedding = embeddingResponse.data[0].embedding
// queryEmbedding は number[] 型（長さ1536）
```

**エラーハンドリング**:
- OpenAI APIエラー時は3回リトライ（指数バックオフ）
- レート制限エラー時は429エラーを返す

### 外部連携2: PostgreSQL pgvector

**ベクトル類似度検索**:
```typescript
import { prisma } from '@/lib/prisma'

// コサイン類似度によるベクトル検索（上位10件）
const results = await prisma.$queryRaw<ContractWithSimilarity[]>`
  SELECT
    c.id,
    c.contract_number,
    c.type,
    c.status,
    c.start_date,
    c.end_date,
    cd.property_name,
    cd.property_address,
    cd.monthly_rent,
    ce.content as excerpt,
    1 - (ce.embedding <=> ${JSON.stringify(queryEmbedding)}::vector) as relevance_score
  FROM contracts c
  JOIN contract_embeddings ce ON ce.contract_id = c.id
  LEFT JOIN contract_details cd ON cd.contract_id = c.id
  WHERE c.status = 'ACTIVE'
  ORDER BY ce.embedding <=> ${JSON.stringify(queryEmbedding)}::vector
  LIMIT ${limit}
`

// relevance_score: 0.0〜1.0（1.0が完全一致）
```

**インデックス戦略**:
- HNSW（Hierarchical Navigable Small World）インデックスを使用
- コサイン類似度（`vector_cosine_ops`）で検索

### 外部連携3: OpenAI GPT-4（回答生成）

**プロンプト設計**:
```typescript
const systemPrompt = `
あなたは不動産契約管理システムのAIアシスタントです。
ユーザーからの質問に対して、検索された契約情報を元に正確で分かりやすい回答を生成してください。

回答のルール:
- 契約番号、物件名、賃料、契約期間などの具体的な情報を含める
- 箇条書きで読みやすく整理する
- 金額は千円単位のカンマ区切りで表示（例: ¥800,000）
- 日付はYYYY年MM月DD日形式で表示
- 契約の更新期限が近い場合は注意喚起を含める
- 検索結果が0件の場合は、検索条件の変更を提案する

回答の形式:
1. 要約（検索結果の概要）
2. 詳細リスト（各契約の情報）
3. 補足情報（必要な場合）
`

const userPrompt = `
【ユーザーの質問】
${query}

【検索された契約情報】
${results.map((r, i) => `
${i + 1}. 契約番号: ${r.contractNumber}
   物件名: ${r.propertyName}
   住所: ${r.propertyAddress}
   契約期間: ${formatDate(r.startDate)} ～ ${formatDate(r.endDate)}
   賃料: ${formatCurrency(r.monthlyRent)}
   関連度: ${(r.relevanceScore * 100).toFixed(0)}%
`).join('\n')}

上記の情報を元に、ユーザーの質問に回答してください。
`

const response = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: userPrompt },
  ],
  temperature: 0.3, // 一貫性を重視
  max_tokens: 1500,
})

const answer = response.choices[0].message.content!
```

**トークン数管理**:
- システムプロンプト: 約200トークン
- 検索結果1件あたり: 約100トークン
- 回答生成: 最大1500トークン
- 合計: 約2000〜3000トークン/リクエスト

### 内部連携: Prisma

**トランザクション**: 不要（検索のみ）

**検索履歴の保存**:
```typescript
await prisma.searchHistory.create({
  data: {
    userId: session.user.id,
    query,
    answer,
    resultCount: results.length,
    tokensUsed: response.usage?.total_tokens || 0,
    processingTime: Date.now() - startTime,
  },
})
```

---

## 開発フロー

### Step 0: キックオフ
- スコープ確認: RAG検索（Embedding生成 + ベクトル検索 + LLM回答生成）
- Must: 自然言語検索、関連契約取得、回答生成
- Should: 検索履歴記録、関連度スコア表示
- Could: 検索結果のキャッシング（v2）
- DoD: 検索精度80%以上、レイテンシ5秒以内、エラーハンドリング完備

### Step 1: 仕様の確定
- ✅ 上記OpenAPI仕様で確定
- エラー形式、認証方式は既存APIと統一

### Step 2: 土台構築
1. **pgvector拡張の有効化**:
   ```bash
   # PostgreSQLでpgvector拡張を有効化
   psql -U postgres -d contract_manage -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

2. **Prismaスキーマ更新**:
   ```bash
   # ContractEmbedding, SearchHistory モデルをschema.prismaに追加
   npx prisma migrate dev --name add_embeddings_and_search_history
   npx prisma generate
   ```

3. **OpenAI SDK インストール**:
   ```bash
   npm install openai
   ```

4. **環境変数設定**（`.env.local`）:
   ```env
   OPENAI_API_KEY=sk-...
   DATABASE_URL="postgresql://user:password@localhost:5432/contract_manage"
   ```

5. **Embedding事前生成スクリプト作成**（`scripts/generate-embeddings.ts`）:
   ```bash
   # 既存の全契約データのEmbeddingを生成
   npx ts-node scripts/generate-embeddings.ts
   ```

### Step 3: 実装
1. **Embedding生成関数** (`lib/embeddings.ts`):
   - `generateEmbedding(text: string): Promise<number[]>`
   - `generateContractContent(contract: Contract): string` - 契約情報をテキストに変換

2. **ベクトル検索関数** (`lib/vectorSearch.ts`):
   - `searchSimilarContracts(queryEmbedding: number[], limit: number): Promise<ContractWithSimilarity[]>`

3. **回答生成関数** (`lib/answerGeneration.ts`):
   - `generateAnswer(query: string, contracts: ContractWithSimilarity[]): Promise<string>`

4. **API Route実装** (`app/api/rag/route.ts`):
   - 認証チェック（NextAuth）
   - クエリバリデーション（5〜500文字）
   - レート制限チェック
   - Embedding生成（OpenAI Embeddings API）
   - ベクトル検索（pgvector）
   - 回答生成（OpenAI GPT-4）
   - 検索履歴記録（SearchHistory）
   - エラーハンドリング

### Step 4: テスト
1. **ユニットテスト**（Jest）:
   - `embeddings.ts` の各関数
   - `vectorSearch.ts` の各関数
   - `answerGeneration.ts` の各関数

2. **API統合テスト**:
   - 正常系: 自然言語検索成功、関連契約取得、回答生成
   - 異常系: クエリ不正（短すぎる/長すぎる）、認証エラー、OpenAI APIエラー
   - エッジケース: 検索結果0件、関連度スコア低い

3. **検索精度評価**:
   - テストケース10問を用意（例: 「来年3月末に満了する賃貸契約」「敷金が賃料の3ヶ月分以上の契約」等）
   - 各テストケースで上位3件に関連契約が含まれるか評価
   - 目標精度: 80%以上（10問中8問以上）

4. **負荷テスト**（オプション）:
   - 同時10リクエスト、p95 < 5秒を確認

### Step 5: デプロイ・運用
1. local環境でテスト
2. PostgreSQLでpgvector拡張を有効化
3. 既存契約データのEmbedding事前生成（バッチ実行）
4. 監視ダッシュボード確認（レイテンシ、エラー率、関連度スコア）
5. Runbook作成:
   - OpenAI APIエラー時 → APIキー確認、リトライ
   - ベクトル検索が遅い時 → インデックス確認、VACUUM ANALYZE実行
   - 検索精度が低い時 → Embeddingの再生成、プロンプトチューニング

---

## チケット詳細

### タイトル
`[Phase4-1] POST /api/rag - RAG検索実装`

### 目的
自然言語による契約検索機能を提供し、ユーザーが直感的に契約情報を検索できるようにする。

### 対象エンドポイント
`POST /api/rag`（上記OpenAPI仕様参照）

### 受け入れ条件
- [ ] 自然言語クエリでの契約検索が成功する
- [ ] OpenAI Embeddings APIでクエリをEmbedding化できる
- [ ] pgvectorでベクトル類似度検索ができる
- [ ] 上位10件の関連契約が取得される
- [ ] LLM（GPT-4）で自然な回答が生成される
- [ ] 関連度スコアが表示される（0.0〜1.0）
- [ ] 検索履歴がSearchHistoryに保存される
- [ ] 以下のバリデーションが動作する:
  - [ ] クエリが短すぎる（5文字未満） → 400エラー
  - [ ] クエリが長すぎる（500文字超過） → 400エラー
  - [ ] レート制限超過 → 429エラー
- [ ] 未認証時に401エラーが返る
- [ ] OpenAI APIエラー時に500エラーが返る
- [ ] ログが構造化形式で出力される（request_id含む）
- [ ] 検索精度評価で80%以上を達成
- [ ] ESLint/Prettierエラーなし
- [ ] ビルドが成功する

### 影響範囲
- **新規ファイル**:
  - `app/api/rag/route.ts`
  - `lib/embeddings.ts`
  - `lib/vectorSearch.ts`
  - `lib/answerGeneration.ts`
  - `scripts/generate-embeddings.ts`（バッチスクリプト）
- **新規テーブル**: `contract_embeddings`, `search_histories`
- **環境変数**: OPENAI_API_KEY

### 依存
- PostgreSQLでpgvector拡張が有効化されていること
- OpenAI APIキー発行完了
- `openai` パッケージインストール完了
- 既存契約データのEmbedding事前生成完了

### サンプルリクエスト
```bash
curl -X POST http://localhost:3001/api/rag \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "来年3月末に満了する賃貸契約を教えて",
    "limit": 10
  }'
```

### サンプルレスポンス
上記「仕様」参照

---

## 🔧 技術補足

### pgvectorのインストール（PostgreSQL）

```bash
# Ubuntuの場合
sudo apt install postgresql-15-pgvector

# macOS (Homebrew)の場合
brew install pgvector

# Dockerの場合
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  pgvector/pgvector:pg15
```

### Embedding生成バッチスクリプト（`scripts/generate-embeddings.ts`）

```typescript
import { PrismaClient } from '@prisma/client'
import OpenAI from 'openai'

const prisma = new PrismaClient()
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY! })

async function generateContractContent(contract: any): Promise<string> {
  const details = contract.details
  const parties = contract.parties

  return `
契約番号: ${contract.contractNumber}
契約種別: ${contract.type}
物件名: ${details?.propertyName || ''}
住所: ${details?.propertyAddress || ''}
契約期間: ${formatDate(contract.startDate)} ～ ${formatDate(contract.endDate)}
賃料: 月額${formatCurrency(details?.monthlyRent)}
敷金: ${formatCurrency(details?.deposit)}
貸主: ${parties.find(p => p.partyType === 'LESSOR')?.name || ''}
借主: ${parties.find(p => p.partyType === 'LESSEE')?.name || ''}
更新条件: ${contract.renewalType || ''}
解約予告期間: ${contract.noticePeriodMonths ? `${contract.noticePeriodMonths}ヶ月前` : ''}
`.trim()
}

async function generateEmbedding(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text,
  })
  return response.data[0].embedding
}

async function main() {
  const contracts = await prisma.contract.findMany({
    include: {
      details: true,
      parties: true,
    },
  })

  console.log(`Processing ${contracts.length} contracts...`)

  for (const contract of contracts) {
    try {
      const content = await generateContractContent(contract)
      const embedding = await generateEmbedding(content)

      await prisma.contractEmbedding.upsert({
        where: { contractId: contract.id },
        create: {
          contractId: contract.id,
          content,
          embedding: JSON.stringify(embedding),
        },
        update: {
          content,
          embedding: JSON.stringify(embedding),
        },
      })

      console.log(`✓ ${contract.contractNumber}`)
    } catch (error) {
      console.error(`✗ ${contract.contractNumber}:`, error)
    }
  }

  console.log('Done!')
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
```

---

**作成者**: Claude Code
**最終更新**: 2025-12-17
