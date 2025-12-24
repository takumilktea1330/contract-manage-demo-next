# PostgreSQL移行ガイド

**作成日**: 2025-12-17
**対象**: SQLite → PostgreSQL への移行

このドキュメントでは、開発環境をSQLiteからPostgreSQLに移行する手順を説明します。

---

## 📋 目次

1. [移行の概要](#移行の概要)
2. [PostgreSQLのセットアップ](#postgresqlのセットアップ)
3. [データベースの初期化](#データベースの初期化)
4. [動作確認](#動作確認)
5. [トラブルシューティング](#トラブルシューティング)
6. [本番環境への適用](#本番環境への適用)

---

## 移行の概要

### 変更内容

| 項目 | 変更前（SQLite） | 変更後（PostgreSQL） |
|-----|-----------------|-------------------|
| データベース | `dev.db` ファイル | PostgreSQL 16（Docker） |
| 接続文字列 | `file:./dev.db` | `postgresql://postgres:postgres@localhost:5432/contract_manage` |
| Prismaプロバイダー | `sqlite` | `postgresql` |
| 長いテキスト | `String` | `String @db.Text` |

### 移行理由

- **本番環境との一致**: 本番環境ではPostgreSQLを使用
- **高度な機能**: 全文検索、pgvector（RAG検索）等
- **並行処理**: 複数ユーザーの同時アクセスに強い
- **トランザクション**: より堅牢なトランザクション処理

### 変更されたファイル

- ✅ `docker-compose.yml` - PostgreSQL + pgAdmin
- ✅ `prisma/schema.prisma` - プロバイダー変更、@db.Text追加
- ✅ `.env.local` - DATABASE_URL更新
- ✅ `.dockerignore` - Docker用の除外設定

---

## PostgreSQLのセットアップ

### 1. Dockerのインストール確認

```bash
# Dockerがインストールされているか確認
docker --version
docker-compose --version

# インストールされていない場合は以下を参考にインストール
# https://docs.docker.com/get-docker/
```

### 2. PostgreSQLコンテナの起動

```bash
cd /home/ryom/contract-manage-demo-next/app

# PostgreSQLとpgAdminを起動
docker-compose up -d

# 起動確認
docker-compose ps

# ログ確認（エラーがないか）
docker-compose logs postgres
```

**期待される出力**:
```
NAME                      IMAGE                  STATUS
contract-app-postgres     postgres:16-alpine     Up 10 seconds (healthy)
contract-app-pgadmin      dpage/pgadmin4:latest  Up 10 seconds
```

### 3. PostgreSQLの接続確認

```bash
# PostgreSQLに接続してみる
docker exec -it contract-app-postgres psql -U postgres -d contract_manage

# 接続できたら以下が表示される:
# psql (16.x)
# Type "help" for help.
#
# contract_manage=#

# データベース一覧を表示
\l

# 終了
\q
```

### 4. pgAdmin（オプション）

ブラウザで `http://localhost:5050` を開いてpgAdminにアクセスできます。

**ログイン情報**:
- Email: `admin@example.com`
- Password: `admin`

**サーバー接続設定**:
- Host: `postgres`（Dockerネットワーク内）
- Port: `5432`
- Username: `postgres`
- Password: `postgres`
- Database: `contract_manage`

---

## データベースの初期化

### 1. 古いSQLiteデータベースの削除（オプション）

```bash
cd /home/ryom/contract-manage-demo-next/app

# 念のためバックアップ
cp prisma/dev.db prisma/dev.db.backup

# SQLiteファイルを削除（PostgreSQLを使うので不要）
rm -f prisma/dev.db prisma/dev.db-journal
```

### 2. Prismaマイグレーションのリセット

```bash
# 古いマイグレーション履歴を削除
rm -rf prisma/migrations

# Prismaクライアントを再生成
npx prisma generate
```

### 3. 新しいマイグレーションの作成

```bash
# PostgreSQL用の初期マイグレーションを作成
npx prisma migrate dev --name init_postgresql

# 成功すると以下が表示される:
# ✔ Generated Prisma Client
# ✔ The migration has been created successfully.
```

**重要**: この時点でPostgreSQLに全てのテーブルが作成されます。

### 4. シードデータの投入

```bash
# シードデータを投入（管理者ユーザー + サンプル契約）
npx prisma db seed

# 成功すると以下が表示される:
# 🌱  Seeding...
# ✅ Seed data created successfully
```

### 5. データの確認

```bash
# Prisma Studioでデータを確認
npx prisma studio

# ブラウザが自動で開き、http://localhost:5555 にアクセス
# GUI上でデータを確認・編集できます
```

または、psqlで確認:

```bash
docker exec -it contract-app-postgres psql -U postgres -d contract_manage

# テーブル一覧
\dt

# ユーザー一覧
SELECT id, email, name, role FROM users;

# 契約一覧
SELECT id, contract_number, type, status FROM contracts;

# 終了
\q
```

---

## 動作確認

### 1. 開発サーバーの起動

```bash
cd /home/ryom/contract-manage-demo-next/app

# 開発サーバーを起動
npm run dev

# 正常に起動すると:
# ▲ Next.js 15.x.x
# - Local:        http://localhost:3001
```

### 2. アプリケーションの動作確認

#### ブラウザでアクセス

`http://localhost:3001` を開く

#### ログイン

- Email: `admin@example.com`
- Password: `password123`

#### 動作確認項目

- [ ] ログインできる
- [ ] ダッシュボードが表示される
- [ ] 契約一覧が表示される（シードデータ1件）
- [ ] 契約詳細が表示される
- [ ] 契約作成ができる
- [ ] 契約更新ができる
- [ ] 検証ページにアクセスできる

### 3. APIの動作確認

```bash
# 契約一覧取得（要認証）
# まずブラウザでログインしてセッションCookieを取得してから:

curl -X GET http://localhost:3001/api/contracts \
  -H "Cookie: next-auth.session-token=YOUR_SESSION_TOKEN"

# または、新規ユーザー登録で確認（認証不要）
curl -X POST http://localhost:3001/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "テストユーザー",
    "role": "USER"
  }'
```

---

## トラブルシューティング

### Q1: Dockerコンテナが起動しない

**エラー**: `Error response from daemon: driver failed programming external connectivity`

**解決策**:
```bash
# ポート5432が既に使用されている可能性
# 既存のPostgreSQLサービスを停止
sudo systemctl stop postgresql

# または、docker-compose.ymlのポートを変更
# ports:
#   - '5433:5432'  # 5432 → 5433 に変更
```

### Q2: マイグレーションが失敗する

**エラー**: `Can't reach database server at localhost:5432`

**解決策**:
```bash
# PostgreSQLコンテナが起動しているか確認
docker-compose ps

# 起動していなければ起動
docker-compose up -d

# DATABASE_URLが正しいか確認
cat .env.local | grep DATABASE_URL

# 正しい接続文字列:
# DATABASE_URL="postgresql://postgres:postgres@localhost:5432/contract_manage?schema=public"
```

### Q3: Prisma Clientのエラー

**エラー**: `PrismaClient is unable to run in this browser environment`

**解決策**:
```bash
# Prismaクライアントを再生成
npx prisma generate

# node_modulesを削除して再インストール
rm -rf node_modules
npm install
```

### Q4: シードデータが投入できない

**エラー**: `Unique constraint failed on the fields: (email)`

**解決策**:
```bash
# データベースをリセット
npx prisma migrate reset

# これにより以下が実行される:
# 1. 全てのデータ削除
# 2. マイグレーション再実行
# 3. シード再実行
```

### Q5: bore.pubトンネルが動かない

bore.pubトンネルを再起動:

```bash
# 古いプロセスを停止
pkill -f "bore local"

# 新しいトンネルを起動（ポート3001を忘れずに）
nohup bore local 3001 --to bore.pub > /tmp/bore.log 2>&1 &

# 新しいURLを確認
grep "listening at" /tmp/bore.log
```

---

## 本番環境への適用

### 1. 本番用PostgreSQLの準備

本番環境では、マネージドPostgreSQLサービスの使用を推奨します:

- **AWS RDS for PostgreSQL**
- **Google Cloud SQL for PostgreSQL**
- **Azure Database for PostgreSQL**
- **Supabase** (無料枠あり)
- **Neon** (無料枠あり)

### 2. 環境変数の設定

本番環境の `.env.production` を作成:

```env
# 本番用PostgreSQL接続文字列
DATABASE_URL="postgresql://username:password@your-db-host:5432/contract_manage?schema=public&sslmode=require"

NEXTAUTH_URL="https://your-production-domain.com"
NEXTAUTH_SECRET="STRONG_RANDOM_SECRET_KEY_HERE"

# AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-northeast-1
S3_BUCKET_NAME=

# OpenAI
OPENAI_API_KEY=
```

**重要**: 本番環境では必ず `sslmode=require` を付けてSSL接続を強制してください。

### 3. マイグレーションの実行

```bash
# 本番環境でのマイグレーション実行
npx prisma migrate deploy

# シードデータは本番では実行しない（必要に応じて手動で作成）
```

### 4. バックアップ設定

本番PostgreSQLの自動バックアップを設定:

- **RDS**: 自動バックアップを有効化（デフォルトで有効）
- **Cloud SQL**: 自動バックアップを有効化
- **手動**: pg_dump で定期バックアップ

```bash
# 手動バックアップの例
pg_dump -h your-db-host -U username -d contract_manage > backup_$(date +%Y%m%d).sql
```

---

## チェックリスト

### 移行前

- [ ] Dockerがインストールされている
- [ ] 既存のSQLiteデータのバックアップを取った（必要に応じて）
- [ ] チーム全員に移行を通知した

### 移行中

- [ ] `docker-compose up -d` でPostgreSQLを起動した
- [ ] `npx prisma migrate dev --name init_postgresql` でマイグレーション作成
- [ ] `npx prisma db seed` でシードデータ投入
- [ ] `npm run dev` で開発サーバーが起動した

### 移行後

- [ ] ブラウザでログインできることを確認
- [ ] 契約一覧・詳細が表示されることを確認
- [ ] APIが正常に動作することを確認
- [ ] Prisma Studioでデータが見えることを確認
- [ ] Git運用ガイドの環境変数セクションを更新した

---

## 参考情報

### 接続情報まとめ

| サービス | URL | 認証情報 |
|---------|-----|---------|
| Next.jsアプリ | http://localhost:3001 | admin@example.com / password123 |
| PostgreSQL | localhost:5432 | postgres / postgres |
| pgAdmin | http://localhost:5050 | admin@example.com / admin |
| Prisma Studio | http://localhost:5555 | 認証不要 |
| bore.pub | http://bore.pub:2181 | 認証不要 |

### よく使うコマンド

```bash
# PostgreSQL起動
docker-compose up -d

# PostgreSQL停止
docker-compose down

# PostgreSQL再起動
docker-compose restart postgres

# ログ確認
docker-compose logs -f postgres

# データベースをリセット（全データ削除）
npx prisma migrate reset

# マイグレーション作成
npx prisma migrate dev --name migration_name

# Prisma Studio起動
npx prisma studio

# Prismaクライアント再生成
npx prisma generate
```

---

## 関連ドキュメント

- [Prisma PostgreSQL](https://www.prisma.io/docs/concepts/database-connectors/postgresql)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL公式](https://www.postgresql.org/docs/)
- [システム設計書](システム設計書.md) - 3章データベース設計

---

**作成者**: Claude Code
**作成日**: 2025-12-17

PostgreSQLへの移行が完了しました！
