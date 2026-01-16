# aizap-bff

LINE Webhook 受信、LIFF API エンドポイント

## 概要

aizap-bff は LINE Bot の Webhook を受信し、LIFF アプリケーション向けの API を提供する BFF (Backend for Frontend) サービスです。

## 技術スタック

- **フレームワーク**: [Hono](https://hono.dev/) - 高速な Web フレームワーク
- **ランタイム**: Node.js 22+
- **言語**: TypeScript
- **パッケージマネージャー**: pnpm 9+
- **LINE SDK**: [@line/bot-sdk](https://github.com/line/line-bot-sdk-nodejs)

## Get Started

1. 依存関係のインストール

```bash
cd /path/to/app/bff
corepack enable
pnpm install
```

2. `.env.example`をコピーして`.env`ファイルを作成：

```bash
cp .env.example .env
```

3. `.env`ファイルを編集して以下を設定する

```bash
LINE_CHANNEL_SECRET=your_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
```

- aizap_devのチャネルにつなげる場合

```bash
gcloud auth login
gcloud secrets versions access latest --secret="LINE_CHANNEL_SECRET" --project="aizap-dev"
gcloud secrets versions access latest --secret="LINE_CHANNEL_ACCESS_TOKEN" --project="aizap-dev"
```

- 自身の作成したチャネルにつなげる場合
  - [LINE 開発者コンソール](https://developers.line.biz/console/)にアクセス
  - プロバイダーとチャネルを選択
  - 「Messaging API」タブから「Channel secret」をコピー
  - 「Messaging API」タブから「Channel access token」をコピー（または発行）

4. 開発サーバーを起動

```bash
# 開発モード（ホットリロード対応）
pnpm dev
```

5. ngrok を使用して接続

- [ngrok](https://ngrok.com/) をインストール

```bash
brew install ngrok
```

- [アカウントを作成](https://dashboard.ngrok.com/signup)して認証トークンを設定
- dashboardにてトークンを入手し認証する

```bash
ngrok config add-authtoken <your auth token>
```

- 別のターミナルで ngrok を起動

```bash
ngrok http 8080
```

- ngrok が表示する HTTPS URL（例: `https://xxxx-xxxx-xxxx.ngrok-free.app`）をコピー

- LINE 開発者コンソールで Webhook URL を設定:
  - URL: `https://xxxx-xxxx-xxxx.ngrok-free.app/api/webhook`
  - Webhook の利用を有効化

## シークレット管理

LINE Bot のシークレットは Google Cloud Secret Manager で管理します。

```bash
# dev
export PROJECT_ID="aizap-dev"

# prod
export PROJECT_ID="aizap-prod"

# シークレットを保存
echo -n "シークレット値" | gcloud secrets versions add "LINE_CHANNEL_SECRET" --data-file=- --project=${PROJECT_ID}
echo -n "アクセストークン値" | gcloud secrets versions add "LINE_CHANNEL_ACCESS_TOKEN" --data-file=- --project=${PROJECT_ID}

# シークレットを取得
gcloud secrets versions access latest --secret="LINE_CHANNEL_SECRET" --project=${PROJECT_ID}
gcloud secrets versions access latest --secret="LINE_CHANNEL_ACCESS_TOKEN" --project=${PROJECT_ID}
```

## Others

- ビルド

```bash
# TypeScript をコンパイル
pnpm build
```

- Lint

```bash
# ESLint でコードをチェック
pnpm lint

# 自動修正
pnpm lint:fix
```

- format

```bash
# Prettier でコードをフォーマット
pnpm format

# フォーマットチェックのみ
pnpm format:check
```

- typeチェック

```bash
# TypeScript の型チェックのみ実行（ビルドしない）
pnpm type-check
```

## Docker

### ビルド

```bash
docker build -t aizap-bff .
```

### 実行

```bash
docker run -p 8080:8080 aizap-bff
```

## デプロイ

このサービスは Google Cloud Run にデプロイされます。

詳細は [../docs/cicd.md](../docs/cicd.md) を参照してください。
