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

## セットアップ

### 前提条件

- Node.js 22.0.0 以上
- pnpm 9.0.0 以上

### インストール

```bash
corepack enable
# 依存関係をインストール
pnpm install
```

## 開発

### ローカル開発サーバー起動

```bash
# 開発モード（ホットリロード対応）
pnpm dev
```

サーバーは `http://localhost:8080` で起動します。

### 環境変数

#### ローカル開発環境での設定

ローカル開発環境では、`.env`ファイルを使用して環境変数を設定できます。`pnpm dev`を実行すると、自動的に`.env`ファイルから環境変数を読み込みます。

1. `.env.example`をコピーして`.env`ファイルを作成：

```bash
cp .env.example .env
```

2. `.env`ファイルを編集して、LINE 開発者コンソールから取得した値を設定：

```bash
LINE_CHANNEL_SECRET=your_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
```

3. LINE 開発者コンソールで値を取得：
   - [LINE 開発者コンソール](https://developers.line.biz/console/)にアクセス
   - プロバイダーとチャネルを選択
   - 「Messaging API」タブから「Channel secret」をコピー
   - 「Messaging API」タブから「Channel access token」をコピー（または発行）

#### 環境変数一覧

| 変数名                      | 説明                          | 必須   | デフォルト |
| --------------------------- | ----------------------------- | ------ | ---------- |
| `LINE_CHANNEL_SECRET`       | LINE チャネルシークレット     | はい   | -          |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE チャネルアクセストークン | はい   | -          |
| `PORT`                      | サーバーのポート番号          | いいえ | `8080`     |

> **注意**: 本番環境や`pnpm start`では、`.env`ファイルは使用されません。環境変数を直接設定してください。

### シークレット管理

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

## ビルド

```bash
# TypeScript をコンパイル
pnpm build
```

ビルド結果は `dist/` ディレクトリに出力されます。

## 実行

```bash
# ビルド済みのアプリケーションを起動
pnpm start
```

## コード品質

### Lint

```bash
# ESLint でコードをチェック
pnpm lint

# 自動修正
pnpm lint:fix
```

### フォーマット

```bash
# Prettier でコードをフォーマット
pnpm format

# フォーマットチェックのみ
pnpm format:check
```

### 型チェック

```bash
# TypeScript の型チェックのみ実行（ビルドしない）
pnpm type-check
```

## エンドポイント

### Webhook

LINE Bot の Webhook を受信するエンドポイントです。

- **URL**: `POST /api/webhook`
- **説明**: LINE プラットフォームから送信されるイベント（メッセージ、フォローなど）を受信します。
- **レスポンス**:
  - 成功時: `200 OK` を返却
  - エラー時: `500 Internal Server Error` を返却

### ローカル開発での Webhook テスト

ローカル開発環境で LINE Webhook をテストするには、ローカルサーバーを外部に公開する必要があります。

#### ngrok を使用する場合

1. [ngrok](https://ngrok.com/) をインストール
2. アカウントを作成して認証トークンを設定
3. サーバーを起動:
   ```bash
   pnpm dev
   ```
4. 別のターミナルで ngrok を起動:
   ```bash
   ngrok http 8080
   ```
5. ngrok が表示する HTTPS URL（例: `https://xxxx-xxxx-xxxx.ngrok-free.app`）をコピー
6. LINE 開発者コンソールで Webhook URL を設定:
   - URL: `https://xxxx-xxxx-xxxx.ngrok-free.app/api/webhook`
   - Webhook の利用を有効化

#### テスト手順

1. ローカルサーバーを起動（`pnpm dev`）
2. トンネルツールで外部公開
3. LINE 開発者コンソールで Webhook URL を設定
4. LINE アプリからメッセージを送信
5. サーバーのログで受信内容を確認

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
