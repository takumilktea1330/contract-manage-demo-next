# Phase 3 API開発 - 作業分担計画

**作成日**: 2025-12-17
**対象**: Phase 3 アップロード・処理API（4個）
**想定開発期間**: 7.5日（並行開発で3〜4日に短縮可能）

---

## 📊 全体概要

### 開発するAPI一覧

| API | エンドポイント | 主な機能 | 工数 | 技術要素 |
|-----|--------------|---------|-----|---------|
| API-1 | POST /api/upload | ファイルアップロード | 2日 | AWS S3, Multipart, バリデーション |
| API-2 | GET /api/upload/[jobId] | 状態取得 | 0.5日 | Prisma, 権限チェック |
| API-3 | POST /api/ocr | OCR処理 | 2日 | Amazon Textract, S3連携 |
| API-4 | POST /api/extraction | LLM情報抽出 | 3日 | OpenAI API, プロンプトエンジニアリング |

**総工数**: 7.5日

---

## 👥 推奨作業分担パターン

### パターンA: 2名体制（推奨）

#### 担当者A: インフラ・アップロード担当
- **担当API**: API-1（POST /api/upload）、API-2（GET /api/upload/[jobId]）
- **工数**: 2.5日
- **スキルセット**:
  - AWS S3 の知識
  - ファイルアップロード処理の経験
  - Next.js API Route の経験
- **作業内容**:
  1. AWS S3 セットアップ（バケット作成、IAM設定）
  2. S3クライアント実装（`lib/s3.ts`）
  3. ファイルバリデーション実装（`lib/fileValidation.ts`）
  4. POST /api/upload 実装
  5. GET /api/upload/[jobId] 実装
  6. テスト作成・実行

#### 担当者B: AI・処理担当
- **担当API**: API-3（POST /api/ocr）、API-4（POST /api/extraction）
- **工数**: 5日
- **スキルセット**:
  - Amazon Textract の知識（または学習意欲）
  - OpenAI API / Claude API の経験
  - プロンプトエンジニアリングの経験
  - LLM出力の構造化データ変換経験
- **作業内容**:
  1. Amazon Textract セットアップ（IAM設定）
  2. Textractクライアント実装（`lib/textract.ts`）
  3. POST /api/ocr 実装
  4. OpenAI API セットアップ
  5. LLM連携実装（`lib/llm.ts`）
  6. プロンプト設計・チューニング
  7. POST /api/extraction 実装
  8. 精度評価・改善
  9. テスト作成・実行

#### 並行開発スケジュール（2名）

| 日数 | 担当者A（インフラ） | 担当者B（AI） | マイルストーン |
|-----|-----------------|--------------|--------------|
| 1日目 | AWS S3セットアップ<br>S3クライアント実装 | Amazon Textractセットアップ<br>Textractクライアント実装 | 環境構築完了 |
| 2日目 | API-1実装（アップロード）<br>ファイルバリデーション | API-3実装（OCR）<br>S3連携 | API-1, API-3実装完了 |
| 3日目 | API-2実装（状態取得）<br>API-1テスト | API-3テスト<br>OpenAI APIセットアップ | API-1, API-2完了 |
| 4日目 | 統合テスト支援<br>ドキュメント作成 | API-4実装（LLM抽出）<br>プロンプト設計 | API-3完了 |
| 5日目 | - | API-4テスト<br>精度評価・改善 | Phase 3完了 |

**完了予定**: 5日（並行開発）

---

### パターンB: 3名体制（最速）

#### 担当者A: アップロード専門
- **担当API**: API-1（POST /api/upload）、API-2（GET /api/upload/[jobId]）
- **工数**: 2.5日

#### 担当者B: OCR専門
- **担当API**: API-3（POST /api/ocr）
- **工数**: 2日

#### 担当者C: LLM専門
- **担当API**: API-4（POST /api/extraction）
- **工数**: 3日

#### 並行開発スケジュール（3名）

| 日数 | 担当者A | 担当者B | 担当者C | マイルストーン |
|-----|--------|--------|--------|--------------|
| 1日目 | AWS S3セットアップ<br>S3クライアント | Textractセットアップ<br>Textractクライアント | OpenAI APIセットアップ<br>プロンプト設計 | 環境構築完了 |
| 2日目 | API-1実装 | API-3実装 | LLM連携実装 | - |
| 3日目 | API-2実装<br>テスト | API-3テスト | API-4実装 | API-1, API-2, API-3完了 |
| 4日目 | 統合テスト支援 | 統合テスト支援 | API-4テスト<br>精度評価 | Phase 3完了 |

**完了予定**: 3〜4日（並行開発）

---

### パターンC: 1名体制（シーケンシャル）

全てのAPIを1名が順番に実装。

#### スケジュール

| 週 | 作業内容 | API | 状態 |
|----|---------|-----|------|
| Week 1前半 | AWS環境構築 + API-1実装 | API-1 | ✅ |
| Week 1後半 | API-2実装 + API-3環境構築 | API-2 | ✅ |
| Week 2前半 | API-3実装 + テスト | API-3 | ✅ |
| Week 2後半 | API-4実装（LLM） | API-4 | 🔄 |
| Week 3前半 | API-4テスト + 精度改善 | API-4 | ✅ |

**完了予定**: 8〜10日

---

## 📦 作業パッケージの渡し方

### 担当者への情報提供

各担当者に以下のドキュメントを渡してください：

1. **全員必須**:
   - `API開発作業パッケージ_Phase3.md`（本パッケージ）
   - `API実装状況.md`（Phase 1, 2の実装状況）
   - `api-dev-docs.txt`（API開発ベストプラクティス）
   - `システム設計書.md`（全体アーキテクチャ）

2. **担当者A（アップロード）**:
   - API-1、API-2のセクション（作業パッケージから抜粋）
   - AWS S3 セットアップ手順
   - 環境変数設定方法

3. **担当者B（OCR）**:
   - API-3のセクション
   - Amazon Textract セットアップ手順
   - S3クライアント（担当者Aが実装）への依存

4. **担当者C（LLM）**:
   - API-4のセクション
   - OpenAI API ドキュメント
   - プロンプトエンジニアリングのベストプラクティス

---

## 🔗 API間の依存関係

```
API-1 (POST /api/upload)
  ↓ S3クライアント、UploadJobモデル
API-2 (GET /api/upload/[jobId])
  ↓ UploadJob作成済み
API-3 (POST /api/ocr)
  ↓ ocrResult作成済み
API-4 (POST /api/extraction)
```

### 依存関係の解消方法

#### 担当者Aが先行（推奨）
1. **Day 1**: 担当者AがS3クライアント実装（`lib/s3.ts`）
2. **Day 1夕方**: S3クライアントをコミット → 担当者Bが利用可能
3. **Day 2**: 各担当者が並行開発

#### 依存を減らす工夫
- **モックデータ使用**: 担当者BはS3完成前にモックで開発開始
- **インターフェース先行**: S3クライアントのインターフェースを先に決める

```typescript
// lib/s3.ts (インターフェース定義)
export interface S3UploadResult {
  s3Key: string
  s3Url: string
}

export async function uploadToS3(
  file: File,
  jobId: string
): Promise<S3UploadResult> {
  // 実装は後で
  throw new Error('Not implemented')
}
```

---

## ✅ チェックリスト（各担当者が確認）

### 開発開始前（全員）

- [ ] リポジトリをclone/pull済み
- [ ] Node.js 18+ インストール済み
- [ ] `npm install` 実行済み
- [ ] `.env.local` ファイル作成済み
- [ ] ローカルでアプリが起動できることを確認（`npm run dev`）
- [ ] Phase 1, 2のAPIが動作することを確認（`curl`でテスト）
- [ ] 作業パッケージを熟読した
- [ ] 自分の担当APIの仕様を理解した

### 開発開始前（担当者A: アップロード）

- [ ] AWSアカウントにアクセスできる
- [ ] AWS CLIインストール済み（`aws --version`）
- [ ] AWS認証情報を設定済み（`aws configure`）
- [ ] S3バケット作成権限がある
- [ ] IAMユーザー作成権限がある
- [ ] `@aws-sdk/client-s3` パッケージの基本を理解した

### 開発開始前（担当者B: OCR）

- [ ] AWSアカウントにアクセスできる（担当者Aと共通）
- [ ] Textractサービスの基本を理解した
- [ ] `@aws-sdk/client-textract` のドキュメントを読んだ
- [ ] 担当者AのS3クライアント完成を待つ or モックで先行開発

### 開発開始前（担当者C: LLM）

- [ ] OpenAI APIキーを取得済み
- [ ] OpenAI API の基本を理解した（Chat Completions API）
- [ ] `openai` パッケージのドキュメントを読んだ
- [ ] JSON出力形式（`response_format`）を理解した
- [ ] 担当者BのOCR完成を待つ or サンプルテキストで先行開発

---

## 📞 コミュニケーション計画

### 毎日のスタンドアップ（15分）

各担当者が報告:
1. 昨日やったこと
2. 今日やること
3. ブロッカー（困っていること）

### 週次レビュー

- 実装したAPIのデモ
- コードレビュー
- 精度評価（API-4のconfidenceScore等）

### Slack/チャットチャンネル

- `#phase3-api-dev` チャンネル作成
- 質問・相談はここで
- コードレビュー依頼もここで

---

## 🧪 統合テスト計画

### API-1, API-2 統合テスト（担当者A）

```bash
# 1. ファイルアップロード
curl -X POST http://localhost:3001/api/upload \
  -H "Cookie: next-auth.session-token=xxx" \
  -F "file=@test.pdf" \
  -F "description=テスト"

# レスポンスからjobIdを取得

# 2. ステータス確認
curl -X GET http://localhost:3001/api/upload/{jobId} \
  -H "Cookie: next-auth.session-token=xxx"
```

### API-3 統合テスト（担当者B）

```bash
# 前提: API-1でアップロード済み、jobIdを取得済み

# OCR処理開始
curl -X POST http://localhost:3001/api/ocr \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{"jobId": "{jobId}"}'

# ステータス確認（2秒おきにポーリング）
curl -X GET http://localhost:3001/api/upload/{jobId} \
  -H "Cookie: next-auth.session-token=xxx"

# ocrResult が返ってくることを確認
```

### API-4 統合テスト（担当者C）

```bash
# 前提: API-3でOCR完了済み、jobIdを取得済み

# 情報抽出
curl -X POST http://localhost:3001/api/extraction \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d '{"jobId": "{jobId}"}'

# レスポンスからcontractIdを取得

# 作成された契約を確認
curl -X GET http://localhost:3001/api/contracts/{contractId} \
  -H "Cookie: next-auth.session-token=xxx"
```

### エンドツーエンドテスト（全員）

```bash
# 1. アップロード
RESPONSE=$(curl -s -X POST http://localhost:3001/api/upload \
  -H "Cookie: next-auth.session-token=xxx" \
  -F "file=@sample_contract.pdf")

JOB_ID=$(echo $RESPONSE | jq -r '.job.id')

# 2. OCR処理
curl -X POST http://localhost:3001/api/ocr \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d "{\"jobId\": \"$JOB_ID\"}"

# 3. ステータス確認（COMPLETED になるまで待つ）
while true; do
  STATUS=$(curl -s -X GET http://localhost:3001/api/upload/$JOB_ID \
    -H "Cookie: next-auth.session-token=xxx" | jq -r '.job.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "COMPLETED" ]; then break; fi
  sleep 2
done

# 4. 情報抽出
curl -X POST http://localhost:3001/api/extraction \
  -H "Cookie: next-auth.session-token=xxx" \
  -H "Content-Type: application/json" \
  -d "{\"jobId\": \"$JOB_ID\"}"

# 5. 作成された契約を確認
curl -X GET http://localhost:3001/api/contracts \
  -H "Cookie: next-auth.session-token=xxx"
```

---

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 問題1: S3アップロードが403エラー

**原因**: IAMポリシーが不足
**解決**:
```bash
aws iam attach-user-policy \
  --user-name contract-app-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

#### 問題2: Textractが400エラー（InvalidParameterException）

**原因**: PDFファイルサイズが大きすぎる（5MB超）
**解決**:
- DetectDocumentText（同期）は5MB制限
- StartDocumentTextDetection（非同期）を使用（10MB以上）

#### 問題3: OpenAI API が429エラー（Rate Limit）

**原因**: RPM/TPM制限超過
**解決**:
- リトライロジック実装（Exponential Backoff）
- 有料プランにアップグレード

#### 問題4: LLM抽出精度が低い（confidenceScore < 0.5）

**原因**: プロンプトが不適切、OCRテキストが不正確
**解決**:
- プロンプトにサンプル出力を追加（Few-shot Learning）
- OCRテキストの前処理（ノイズ除去）
- モデルを GPT-4o → GPT-4o-mini 以上に変更

---

## 📚 参考資料

### 公式ドキュメント

- [Next.js 15 API Routes](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
- [AWS SDK for JavaScript v3](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/)
- [Amazon S3](https://docs.aws.amazon.com/s3/)
- [Amazon Textract](https://docs.aws.amazon.com/textract/)
- [OpenAI API](https://platform.openai.com/docs/)
- [Prisma](https://www.prisma.io/docs/)

### 社内ドキュメント

- `api-dev-docs.txt` - API開発ベストプラクティス
- `システム設計書.md` - 全体アーキテクチャ
- `要件定義書.md` - 機能要件・非機能要件
- `API実装状況.md` - Phase 1, 2の実装詳細

---

## 🎯 成功の定義

Phase 3が成功したと言えるのは以下の条件を全て満たした時:

1. **機能要件**:
   - [ ] PDFアップロード → OCR → LLM抽出 → Contract作成の一連のフローが動作する
   - [ ] 実際の契約書PDFで動作することを確認済み
   - [ ] エラーハンドリングが全て実装されている

2. **品質要件**:
   - [ ] OCR精度: 印刷文字で95%以上
   - [ ] LLM抽出精度: 主要項目で90%以上
   - [ ] confidenceScore: 平均0.8以上
   - [ ] テストカバレッジ: 80%以上（ユニット + 統合）

3. **非機能要件**:
   - [ ] API-1レイテンシ: p95 < 3秒
   - [ ] API-3レイテンシ: 1ページあたり2〜5秒
   - [ ] API-4レイテンシ: p95 < 10秒
   - [ ] エラー率: < 1%

4. **運用要件**:
   - [ ] ログが構造化形式で出力されている
   - [ ] AuditLogに全アクションが記録されている
   - [ ] ドキュメントが更新されている
   - [ ] ESLint/Prettierエラーなし
   - [ ] ビルドが成功する

---

## 📅 マイルストーン

| マイルストーン | 完了条件 | 期日 |
|--------------|---------|------|
| M1: 環境構築完了 | AWS S3/Textract/OpenAI セットアップ完了 | Day 1 |
| M2: API-1, API-2完了 | アップロード・状態取得が動作 | Day 3 |
| M3: API-3完了 | OCR処理が動作 | Day 4 |
| M4: API-4完了 | LLM抽出・Contract作成が動作 | Day 5 |
| M5: Phase 3完了 | E2Eテスト通過、ドキュメント更新 | Day 5 |

---

## 🙋 質問・相談

わからないことがあれば以下に連絡:

- **技術的な質問**: `#phase3-api-dev` Slackチャンネル
- **仕様の確認**: プロダクトオーナー / テックリード
- **AWS権限の問題**: インフラ担当者
- **緊急の問題**: 直接電話/DM

---

**作成者**: Claude Code
**承認者**: （プロジェクトマネージャー名）
**最終更新**: 2025-12-17
