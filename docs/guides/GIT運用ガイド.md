# Git運用ガイド - 契約管理アプリ

**作成日**: 2025-12-17
**対象**: 契約管理アプリ開発チーム

このドキュメントでは、このプロジェクトでのGit/GitHub運用ルールを説明します。

---

## 📋 目次

1. [基本ルール](#基本ルール)
2. [ブランチ戦略](#ブランチ戦略)
3. [日々のワークフロー](#日々のワークフロー)
4. [Pull Request運用](#pull-request運用)
5. [コミット規約](#コミット規約)
6. [GitHub機能の活用](#github機能の活用)
7. [セットアップ済みの機能](#セットアップ済みの機能)
8. [よくある問題と対処法](#よくある問題と対処法)

---

## 基本ルール

### 🚨 絶対に守ること

1. **main ブランチに直接 push しない**
   - 全ての変更は Pull Request 経由
2. **APIキー・秘密情報をコミットしない**
   - `.env` ファイルは `.gitignore` に含まれています
   - 誤ってコミットした場合は直ちにキーを無効化
3. **CIが通らないとマージできない**
   - ESLint, TypeScript, テスト, ビルドが全て成功必須
4. **PRは小さく（数百行以内を推奨）**
   - 大きなPRはレビューが困難
   - 機能ごとに分割

### ✅ 推奨事項

- コミットメッセージは規約に従う（Conventional Commits）
- PRテンプレートを埋める
- レビューは24時間以内に開始
- Draft PRを活用して早めにフィードバックを得る

---

## ブランチ戦略

### ブランチの種類

```
main (保護ブランチ)
  ↑
  PR
  ↑
feat/login-api (作業ブランチ)
```

#### `main` ブランチ
- 常にデプロイ可能な状態
- 直接pushは禁止（GitHub設定で保護済み）
- PR経由のみマージ可能
- CI必須、レビュー1名以上必須

#### 作業ブランチ
- `feat/xxx`: 新機能
- `fix/xxx`: バグ修正
- `chore/xxx`: 雑務（依存関係更新、設定変更等）
- `docs/xxx`: ドキュメント更新

### ブランチの命名例

```bash
# 良い例
feat/upload-api
fix/contract-list-pagination
chore/update-prisma
docs/api-documentation

# 悪い例
feature    # 何をするか不明
new-code   # 抽象的すぎ
test123    # 意味不明
```

---

## 日々のワークフロー

### 新しい機能を開発する場合

```bash
# 1. main の最新を取得
git checkout main
git pull origin main

# 2. 作業ブランチを作成
git checkout -b feat/upload-api

# 3. 開発・コミット
# ... コーディング ...
git add .
git commit -m "feat: add file upload endpoint"

# 4. リモートにプッシュ
git push -u origin feat/upload-api

# 5. GitHubでPRを作成
# ブラウザでGitHubを開き、「Compare & pull request」をクリック
```

### 複数回のコミットを行う場合

```bash
# コミット1
git add .
git commit -m "feat: add upload validation"
git push

# コミット2（追加の変更）
git add .
git commit -m "feat: add S3 integration"
git push

# PR作成後も追加のコミットをプッシュできます
```

### コンフリクトが発生した場合

```bash
# main の最新を取り込む
git fetch origin
git rebase origin/main

# コンフリクトを解決
# エディタでファイルを編集

git add .
git rebase --continue

# リモートに強制プッシュ（rebase後は必要）
git push -f origin feat/upload-api
```

---

## Pull Request運用

### PRを作成する前のチェックリスト

- [ ] ローカルでテストが通る（`npm test`）
- [ ] ESLint/Prettierエラーがない（`npm run lint`, `npm run format`）
- [ ] TypeScriptエラーがない（`npx tsc --noEmit`）
- [ ] ビルドが成功する（`npm run build`）
- [ ] 動作確認済み

### PRテンプレートの記入

PRを作成すると、以下のテンプレートが表示されます。**全ての項目を記入してください**：

1. **何をしたか（要約）**: このPRの目的
2. **変更内容の詳細**: 技術的な詳細
3. **どう確認したか**: 動作確認の手順（スクリーンショット、curlコマンド等）
4. **影響範囲**: チェックボックスで選択
5. **セキュリティ**: セキュリティチェック項目を確認
6. **テスト**: テストの有無
7. **関連Issue**: Closes #123 等

### PRのサイズ

| サイズ | 行数 | 推奨 |
|-------|-----|------|
| 小 | 〜300行 | ✅ 理想的 |
| 中 | 300〜500行 | ⚠️ 問題なし |
| 大 | 500〜1000行 | ⚠️ 分割を検討 |
| 特大 | 1000行〜 | ❌ 必ず分割 |

### レビュープロセス

```
PR作成
  ↓
自動でレビュワーがアサイン（CODEOWNERS）
  ↓
CIが自動実行（lint, test, build等）
  ↓
レビュワーがコードレビュー
  ↓
修正が必要な場合は追加のコミットをプッシュ
  ↓
Approve後、マージ
```

### レビュー観点

レビュワーは以下の観点で確認します：

1. **仕様**: 要件定義・設計書通りか
2. **セキュリティ**: 認証・認可、入力バリデーション、SQLインジェクション・XSS対策
3. **エラーハンドリング**: 例外処理が適切か
4. **テスト**: テストがあるか、カバレッジは十分か
5. **ログ**: 必要な情報がログに出力されているか
6. **パフォーマンス**: 明らかな性能問題がないか
7. **可読性**: 変数名、関数名が適切か

---

## コミット規約

### Conventional Commits

コミットメッセージは以下のフォーマットに従ってください：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### type（必須）

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: コードスタイル（機能変更なし）
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: 雑務

### scope（オプション）

- `api`: APIに関する変更
- `ui`: UIに関する変更
- `db`: データベースに関する変更
- `auth`: 認証に関する変更
- `ci`: CI/CDに関する変更

### 例

```bash
# シンプルな例
git commit -m "feat: add login endpoint"

# スコープ付き
git commit -m "fix(api): correct pagination logic"

# 詳細な説明付き
git commit -m "feat(ui): add dark mode toggle

Implement theme switcher in header.
User preference is saved to localStorage.

Closes #123"

# Breaking change
git commit -m "refactor(api)!: change contract API response

BREAKING CHANGE: Contract API now returns nested details."
```

---

## GitHub機能の活用

### Issues

- **機能要望**: `[FEATURE]` タグで作成
- **バグ報告**: `[BUG]` タグで作成
- PRと紐付け: `Closes #123` でマージ時に自動Close

### Projects

- GitHub Projectsでタスク管理
- ボード: To Do → In Progress → Review → Done

### Actions（CI/CD）

自動で以下が実行されます：

1. **Lint**: ESLint + Prettier
2. **Type Check**: TypeScript
3. **Test**: Jest
4. **Build**: Next.js build
5. **Prisma Validate**: スキーマ検証
6. **Security Check**: npm audit + 秘密情報チェック

### Branch Protection

`main` ブランチには以下の保護設定が推奨されます：

- PR必須
- CI必須（全てのチェックが成功）
- 直pushを禁止
- レビュー1名以上必須

### CODEOWNERS

特定のファイルに変更があると、自動でレビュワーがアサインされます：

- `/app/api/**` → @backend-team
- `/app/components/**` → @frontend-team
- `/app/prisma/**` → @backend-team @database-admin
- `.github/**` → @tech-lead

---

## セットアップ済みの機能

このプロジェクトには以下のGitHub運用ファイルが既にセットアップされています：

### 1. CI/CDワークフロー

**ファイル**: `.github/workflows/ci.yml`

**実行内容**:
- ESLint + Prettier チェック
- TypeScript型チェック
- Jest テスト実行
- Next.js ビルド
- Prismaスキーマ検証
- セキュリティチェック（npm audit, 秘密情報チェック）

### 2. PRテンプレート

**ファイル**: `.github/pull_request_template.md`

PRを作成すると自動で表示されます。以下の項目を記入：
- 何をしたか
- どう確認したか
- 影響範囲
- セキュリティチェック
- テスト
- 関連Issue

### 3. Issueテンプレート

**ファイル**:
- `.github/ISSUE_TEMPLATE/feature_request.md` - 機能要望
- `.github/ISSUE_TEMPLATE/bug_report.md` - バグ報告

GitHub上で Issue を作成する際に選択できます。

### 4. CODEOWNERS

**ファイル**: `.github/CODEOWNERS`

ファイルごとに自動でレビュワーをアサインします。チームに合わせて編集してください。

### 5. 貢献ガイド

**ファイル**: `.github/CONTRIBUTING.md`

開発環境のセットアップ、ブランチ戦略、コミット規約等の詳細ガイド。

---

## よくある問題と対処法

### Q1: CIが失敗する

**A**: ローカルで以下を実行して確認：

```bash
npm run lint          # ESLint
npm run format:check  # Prettier
npx tsc --noEmit      # TypeScript
npm test              # テスト
npm run build         # ビルド
```

エラーを修正してコミット・プッシュすると、CIが再実行されます。

### Q2: コンフリクトが発生した

**A**: mainの最新を取り込んで解決：

```bash
git fetch origin
git rebase origin/main

# コンフリクトを解決
# エディタでファイルを編集

git add .
git rebase --continue
git push -f origin feat/your-feature
```

### Q3: 間違ってAPIキーをコミットした

**A**: 以下の手順で対応：

1. **速やかにAPIキーを無効化**
2. 履歴から削除（BFG Repo-Cleaner or git filter-branch）
3. 新しいAPIキーを発行して `.env.local` に設定

**重要**: コミットを削除しただけでは履歴に残ります。必ずキーを無効化してください。

### Q4: PRが大きくなってしまった

**A**: 機能ごとに分割してください：

```bash
# 現在のブランチをバックアップ
git branch feat/upload-api-backup

# 小さなPRを作成
git checkout main
git checkout -b feat/upload-validation
# 必要なファイルだけコミット
git add app/lib/fileValidation.ts
git commit -m "feat: add file validation"
git push -u origin feat/upload-validation
# PRを作成

# 残りの部分も同様に分割
```

### Q5: 直前のコミットメッセージを修正したい

**A**: まだpushしていない場合：

```bash
git commit --amend -m "feat: correct commit message"
```

既にpushした場合は、そのままにするか、新しいコミットを追加してください。

### Q6: mainに直接pushしてしまった

**A**: GitHub設定でブランチ保護を有効にしていれば拒否されます。もし通ってしまった場合は：

```bash
# 最後のコミットを取り消し（まだpushしていない場合）
git reset --soft HEAD~1

# 既にpushした場合はrevert
git revert HEAD
git push origin main
```

---

## チェックリスト

### 初回セットアップ時

- [ ] リポジトリをクローン
- [ ] 依存関係をインストール（`npm install`）
- [ ] `.env.local` を設定
- [ ] Prismaセットアップ（`npx prisma generate`, `npx prisma migrate dev`）
- [ ] 開発サーバーが起動することを確認（`npm run dev`）
- [ ] CODEOWNERSのチーム名を実際のGitHubチーム名に更新

### PR作成前

- [ ] ESLint/Prettierエラーなし（`npm run lint`, `npm run format`）
- [ ] TypeScriptエラーなし（`npx tsc --noEmit`）
- [ ] テストが通る（`npm test`）
- [ ] ビルドが成功する（`npm run build`）
- [ ] 動作確認済み（スクリーンショット/ログ保存）

### PR作成時

- [ ] PRテンプレートの全項目を記入
- [ ] 関連Issueを紐付け（`Closes #123`）
- [ ] レビュワーを指定（自動アサインも可）
- [ ] PRのサイズが適切（500行以内を推奨）

---

## 参考資料

### 社内ドキュメント

- [API開発ロードマップ](API開発ロードマップ.md)
- [API実装状況](API実装状況.md)
- [Phase 3 作業パッケージ](Phase3_作業パッケージ_README.md)
- [要件定義書](要件定義書.md)
- [システム設計書](システム設計書.md)

### 外部リンク

- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## サポート

わからないことがあれば：

- **技術的な質問**: `#dev-support` Slackチャンネル
- **Git/GitHub操作**: `#git-help` Slackチャンネル
- **緊急の問題**: テックリードに直接連絡

---

**作成者**: Claude Code
**作成日**: 2025-12-17
**最終更新**: 2025-12-17
