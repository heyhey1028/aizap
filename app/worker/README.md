# aizap-worker

Pub/Sub からメッセージを受信し、Agent Engine を呼び出して LINE に返信する Worker サービス

## 概要

aizap-worker は Cloud Pub/Sub の Push サブスクリプションからメッセージを受信し、Vertex AI Agent Engine にクエリを送信して、LINE Push API で返信を行う Worker サービスです。

## 技術スタック

- **フレームワーク**: [Hono](https://hono.dev/) - 高速な Web フレームワーク
- **ランタイム**: Node.js 22+
- **言語**: TypeScript
- **パッケージマネージャー**: pnpm 9+
- **LINE SDK**: [@line/bot-sdk](https://github.com/line/line-bot-sdk-nodejs)
- **GCP 認証**: [google-auth-library](https://github.com/googleapis/google-auth-library-nodejs)

## Get Started

1. 依存関係のインストール

```bash
cd /path/to/app/worker
corepack enable
pnpm install
```

2. `.env` ファイルを作成

```bash
GCP_PROJECT_ID=<your_project_id>
GCP_REGION=<your_region>
AGENT_ENGINE_RESOURCE_ID=<your_agent_engine_resource_id>
GCS_MEDIA_BUCKET_NAME=<your_gcs_media_bucket_name>
LINE_CHANNEL_ACCESS_TOKEN=<your_channel_access_token>
DATABASE_URL=postgresql://postgres@localhost:5432/aizap?schema=public
```

- Secret Manager から取得する場合

```bash
gcloud auth login
gcloud secrets versions access latest --secret="LINE_CHANNEL_ACCESS_TOKEN" --project="<your_project_id>"
```

- Agent Engine の Resource ID は GCP Console の Agent Engine ページで確認できます
- GCS のバケット名は `${project_id}-line-media` を想定しています

3. GCP 認証（ADC）を設定

```bash
gcloud auth application-default login
```

4. 開発サーバーを起動

```bash
pnpm dev
```

## Prisma / データベース

ローカル開発ではリポジトリ直下の `docker-compose.yml` を使用します。
Prisma CLI の実行には `DATABASE_URL` が必須です（`.env` は自動で読み込まれません）。

### Docker Compose の操作

```bash
# 起動
docker compose up -d
# 停止
docker compose stop
# 再開
docker compose start
# 停止して削除
docker compose down
# ログ
docker compose logs -f postgres
```

```bash
# リポジトリ直下で実行
docker compose up -d

cd app/worker
export DATABASE_URL="postgresql://postgres@localhost:5432/aizap?schema=public"
pnpm prisma migrate dev
```

本番・dev 環境は Cloud Run Job で `prisma migrate deploy` を実行します。
Prisma Client の生成が必要な場合は `pnpm prisma:generate` を実行してください。
`pnpm prisma migrate dev` で生成される `prisma/migrations/**` は必ずコミットしてください。

## ローカル E2E テスト

BFF → Pub/Sub → Worker → Agent Engine のフロー全体をローカルでテストする手順です。

### 1. Pub/Sub Emulator を起動

```bash
gcloud components install pubsub-emulator
gcloud beta emulators pubsub-env-init

# 別ターミナルで起動
gcloud beta emulators pubsub-start --project=aizap-dev
```

### 2. Topic と Subscription を作成

```bash
export PUBSUB_EMULATOR_HOST=localhost:8085
export PROJECT_ID=<your_project_id>

# Topic 作成
curl -s -X PUT "http://localhost:8085/v1/projects/${PROJECT_ID}/topics/line-webhook"

# Subscription 作成（Worker に Push）
curl -s -X PUT "http://localhost:8085/v1/projects/${PROJECT_ID}/subscriptions/line-webhook-sub" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "projects/'${PROJECT_ID}'/topics/line-webhook",
    "pushConfig": {
      "pushEndpoint": "http://localhost:8081/webhook"
    }
  }'
```

### 3. BFF を起動

```bash
cd app/bff
PUBSUB_EMULATOR_HOST=localhost:8085 GOOGLE_CLOUD_PROJECT=${PROJECT_ID} pnpm dev
```

### 4. Worker を起動（別ターミナル）

```bash
cd app/worker
PORT=8081 pnpm dev
```

### 5. テストリクエストを送信

LINE の署名付きリクエストを BFF に送信します。

```bash
LINE_SECRET=$(gcloud secrets versions access latest --secret=LINE_CHANNEL_SECRET --project=${PROJECT_ID})

BODY='{"events":[{"type":"message","replyToken":"dummy","source":{"type":"user","userId":"Uxxxxxxxxxxxxx"},"timestamp":1700000000000,"message":{"type":"text","id":"12345","text":"こんにちは"}}]}'

SIGNATURE=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$LINE_SECRET" -binary | base64)

curl -X POST "http://localhost:8080/api/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Line-Signature: $SIGNATURE" \
  -d "$BODY"
```

**注意**: ダミー userId ではLINE Push API が 400 エラーになりますが、BFF → Pub/Sub → Worker → Agent Engine のフローは確認できます。

## Others

- ビルド

```bash
pnpm build
```

- Lint

```bash
pnpm lint
pnpm lint:fix
```

- フォーマット

```bash
pnpm format
pnpm format:check
```

- 型チェック

```bash
pnpm type-check
```

## Docker

### ビルド

```bash
docker build -t aizap-worker .
```

### 実行

```bash
docker run -p 8080:8080 aizap-worker
```

## デプロイ

このサービスは Google Cloud Run にデプロイされます。

詳細は [../../docs/cicd.md](../../docs/cicd.md) を参照してください。
