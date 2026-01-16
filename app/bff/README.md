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

| 変数名 | 説明                 | デフォルト |
| ------ | -------------------- | ---------- |
| `PORT` | サーバーのポート番号 | `8080`     |

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

TBD

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
