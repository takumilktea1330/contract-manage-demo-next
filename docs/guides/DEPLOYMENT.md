# 契約管理APP デプロイ手順書

このドキュメントでは、契約管理アプリを**Vercel**にデプロイして一般公開する手順を説明します。

---

## 📋 前提条件

- [x] GitHubアカウント
- [x] GitHubリポジトリ: `https://github.com/axion15tth/contract-manage-demo-next.git`
- [x] ビルドが正常に完了すること（確認済み）

---

## 🚀 Vercelへのデプロイ手順

### ステップ1: Vercelアカウントの作成

1. [Vercel公式サイト](https://vercel.com)にアクセス
2. 「Sign Up」をクリック
3. **GitHubアカウントでサインアップ**を選択（推奨）
4. GitHubとの連携を許可

### ステップ2: GitHubの変更をコミット・プッシュ

ビルドエラー修正が完了したので、変更をGitHubにプッシュします。

```bash
cd /home/ryom/contract-manage-demo-next

# 変更ファイルを確認
git status

# 修正ファイルをステージング
git add app/app/(dashboard)/contracts/\[id\]/page.tsx
git add app/app/(dashboard)/contracts/\[id\]/verify/page.tsx
git add app/app/(dashboard)/contracts/page.tsx

# コミット
git commit -m "Fix Next.js 15 build errors for Vercel deployment

- Fix dynamic route params to use Promise type in server components
- Use useParams() hook in client components instead of props
- Remove useSearchParams() to avoid Suspense boundary issues"

# GitHubにプッシュ
git push origin main
```

### ステップ3: Vercelでプロジェクトをインポート

1. Vercelダッシュボードにログイン
2. 「Add New...」→「Project」をクリック
3. 「Import Git Repository」セクションで、GitHubリポジトリを選択
   - リポジトリ名: `contract-manage-demo-next`
4. 「Import」をクリック

### ステップ4: プロジェクト設定

#### 基本設定

| 設定項目 | 値 |
|---------|---|
| **Framework Preset** | Next.js（自動検出） |
| **Root Directory** | `app` ⚠️ 重要！ |
| **Build Command** | `npm run build`（デフォルト） |
| **Output Directory** | `.next`（デフォルト） |
| **Install Command** | `npm install`（デフォルト） |

⚠️ **重要**: Root Directory を `app` に設定してください。プロジェクト構造が以下のようになっているためです：

```
contract-manage-demo-next/
├── app/              ← Next.jsアプリ（ここをルートに設定）
│   ├── app/
│   ├── components/
│   ├── package.json
│   └── next.config.js
└── llm-experiment/   ← LLM実験フレームワーク
```

#### 環境変数（オプション）

現在のデモでは環境変数は不要ですが、将来的に必要になる場合は以下を設定します：

```env
# 将来的に必要な環境変数（現在は不要）
# DATABASE_URL=
# NEXTAUTH_SECRET=
# NEXTAUTH_URL=
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# OPENAI_API_KEY=
```

### ステップ5: デプロイ実行

1. 設定を確認後、「Deploy」ボタンをクリック
2. デプロイプロセスが開始されます
   - ✓ ソースコード取得
   - ✓ 依存関係インストール
   - ✓ ビルド実行
   - ✓ デプロイ完了
3. 通常2-3分で完了します

### ステップ6: デプロイ完了

デプロイが成功すると、以下のURLが発行されます：

- **Production URL**: `https://contract-manage-demo-next.vercel.app`
- **プロジェクト URL**: `https://contract-manage-demo-next-<ユーザー名>.vercel.app`

---

## 🌐 カスタムドメインの設定（オプション）

独自ドメインを使用する場合：

1. Vercelプロジェクトダッシュボードの「Settings」→「Domains」に移動
2. カスタムドメインを追加
3. DNSレコードを設定（Vercelが指示を表示）
4. SSL証明書は自動で発行されます

---

## 🔄 自動デプロイの設定

Vercelでは**GitHubとの連携により自動デプロイ**が有効化されています：

### 動作
- `main`ブランチへのプッシュ → **本番環境に自動デプロイ**
- プルリクエスト作成 → **プレビュー環境を自動生成**

### 自動デプロイの無効化（必要な場合）
1. Vercelプロジェクト「Settings」→「Git」
2. 「Production Branch」の設定を変更
3. または「Ignored Build Step」を設定

---

## 🧪 デプロイ後の確認事項

### 1. 画面動作確認

以下の画面が正常に表示されることを確認：

- [ ] ログイン画面（`/login`）
- [ ] ダッシュボード（`/dashboard`）
- [ ] 契約書アップロード（`/upload`）
- [ ] AI契約検索（`/contracts`）
- [ ] 契約詳細（`/contracts/[id]`）
- [ ] 検証画面（`/contracts/[id]/verify`）
- [ ] レントロール作成（`/rentroll`）
- [ ] 期限管理（`/calendar`）
- [ ] 通常検索（`/search`）

### 2. パフォーマンス確認

- [ ] ページ読み込み速度が2秒以内
- [ ] Google Maps が正常に表示される
- [ ] グラフ・チャートが正常に表示される
- [ ] タイピングアニメーションが動作する

### 3. レスポンシブ確認（推奨）

- [ ] デスクトップ（1920x1080）
- [ ] ノートPC（1366x768）
- [ ] タブレット（768x1024）※ 一部機能制限あり

---

## 🔧 トラブルシューティング

### ビルドエラーが発生する場合

#### 問題: `Module not found: Can't resolve...`

**解決策**: 依存関係が不足している可能性があります。

```bash
# ローカルで確認
cd app
npm install

# package-lock.json をコミット
git add package-lock.json
git commit -m "Add missing dependencies"
git push
```

#### 問題: `Type error: ...`

**解決策**: TypeScriptのビルドエラーです。

```bash
# ローカルで型チェック
cd app
npm run build

# エラーを修正後、コミット・プッシュ
```

#### 問題: Root Directory の設定ミス

**症状**: `package.json not found` エラー

**解決策**:
1. Vercelプロジェクト「Settings」→「General」
2. 「Root Directory」を `app` に変更
3. 「Save」後、「Redeploy」

### ページが404エラーになる場合

**原因**: ルーティング設定の問題

**解決策**:
1. `app/app/` ディレクトリ構造を確認
2. `page.tsx` ファイルが正しい場所にあるか確認
3. 動的ルート `[id]` のフォルダ名を確認

### 環境変数が反映されない場合

**解決策**:
1. Vercel「Settings」→「Environment Variables」
2. 変数を追加・編集
3. 「Redeploy」を実行（自動では反映されない）

---

## 📊 デプロイ後のモニタリング

### Vercel Analyticsの有効化（推奨）

1. Vercelプロジェクトダッシュボード
2. 「Analytics」タブをクリック
3. 「Enable Analytics」をクリック

**確認できる指標**:
- ページビュー数
- ユニークビジター数
- 平均読み込み時間
- Core Web Vitals（LCP, FID, CLS）

### ログの確認

1. 「Deployments」タブ
2. 対象デプロイをクリック
3. 「Build Logs」でビルドログを確認
4. 「Function Logs」でランタイムログを確認

---

## 🔒 セキュリティ注意事項

### 現在のデモの制約

⚠️ **このアプリはデモンストレーション目的です**

- 実際の認証機能はありません
- データベースに接続していません
- すべてモックデータです
- 本番環境での利用は非推奨です

### 本番化する場合の必須対応

本番環境で使用する場合は、以下の実装が必要です：

1. **認証・認可**
   - NextAuth.js の実装
   - パスワードハッシュ化
   - セッション管理

2. **データベース**
   - PostgreSQL の設定
   - Prisma ORM の実装
   - データ暗号化

3. **API セキュリティ**
   - CSRF 対策
   - Rate Limiting
   - APIキーの環境変数化

4. **詳細**: `/実装整合性分析レポート.md` を参照

---

## 📞 サポート

### 公式ドキュメント

- [Next.js ドキュメント](https://nextjs.org/docs)
- [Vercel ドキュメント](https://vercel.com/docs)
- [Vercel デプロイガイド](https://vercel.com/docs/deployments/overview)

### トラブル時の連絡先

- GitHub Issues: `https://github.com/axion15tth/contract-manage-demo-next/issues`

---

## 🎉 デプロイ完了！

おめでとうございます！アプリが正常にデプロイされました。

**公開URL**: `https://contract-manage-demo-next.vercel.app`

このURLを共有することで、誰でもデモアプリにアクセスできます。

---

**作成日**: 2025-12-11
**バージョン**: 1.0.0
**Next.js バージョン**: 15.5.4
