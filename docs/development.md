# 開発ガイド

## ローカル開発セットアップ

### 前提条件

- Python 3.10〜3.12
- Google Cloud SDK (`gcloud`)
- GCP プロジェクトへのアクセス権

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/heyhey1028/aizap.git
cd aizap/app/adk

# uv をインストール
brew install uv
# または: curl -LsSf https://astral.sh/uv/install.sh | sh

# 仮想環境を作成
uv venv

# 依存関係をインストール
uv sync

# GCP 認証
gcloud auth application-default login

# 環境変数を設定
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_PROJECT=aizap-dev
export GOOGLE_CLOUD_LOCATION=asia-northeast1
```

## ADK コマンド

| コマンド | 説明 | セッション |
|---------|------|-----------|
| `uv run adk web` | ブラウザベース開発 UI | InMemorySessionService |
| `uv run adk run` | ターミナル対話型テスト | InMemorySessionService |
| `uv run adk api_server` | ローカル REST API サーバー | InMemorySessionService |

### 実行例

```bash
cd app/adk

# ブラウザで開発 UI を起動（ドロップダウンからエージェントを選択）
uv run adk web agents
# => http://localhost:8000 でアクセス

# ターミナルで対話
uv run adk run agents/health_advisor

# REST API サーバーを起動
uv run adk api_server agents/health_advisor
```

## Agent Engine デプロイ

本番環境では Vertex AI Agent Engine にデプロイします。
Agent Engine は自動的に VertexAiSessionService を使用してセッションを永続化します。

> **Note**: Agent Engine は Python 3.10〜3.12 のみサポートしています。

### 手動デプロイ（ADK CLI）

```bash
cd app/adk

# staging_bucket は Terraform で作成済み: gs://${PROJECT_ID}-staging
uv run adk deploy agent_engine \
  --project=aizap-dev \
  --region=asia-northeast1 \
  --staging_bucket=gs://aizap-dev-staging \
  --display_name="aizap-health-advisor" \
  agents/health_advisor
```

### GitHub Actions からデプロイ（推奨）

1. Actions → **Deploy Agent Engine** → **Run workflow**
2. environment を選択（dev / prod）
3. 実行（`app/adk/agents/` 配下の全エージェントが自動デプロイされます）

## データベース（Prisma）

Worker の DB スキーマは Prisma で管理します。
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

### ローカル開発

```bash
# リポジトリ直下で起動
docker compose up -d

cd app/worker
export DATABASE_URL="postgresql://postgres@localhost:5432/aizap?schema=public"
pnpm prisma migrate dev
```

`pnpm prisma migrate dev` で生成される `prisma/migrations/**` は必ずコミットしてください。

### デプロイ時のマイグレーション

dev / prod は Cloud Run Job で `prisma migrate deploy` を実行します。

## Terraform（ローカル実行）

インフラの変更は基本的に **GitHub Actions** で実行します（PR で plan、main push で apply）。

ローカルで plan を確認したい場合：

```bash
# GCP 認証
gcloud auth application-default login

cd infra/dev

# 初期化
terraform init

# プラン確認
terraform plan \
  -var=project_id=aizap-dev \
  -var=region=asia-northeast1 \
  -var=environment=dev \
  -var=image_bff=gcr.io/cloudrun/hello \
  -var=image_worker=gcr.io/cloudrun/hello
```

> **Note**: `image_*` には現在デプロイ中のイメージを指定してください。
> GitHub Actions では自動で現在のイメージを取得します。
