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

### `GET /`

Hello World を返す（動作確認用）

**レスポンス:**

```
Hello, World!
```

## 今後の実装予定

以下のエンドポイントを順次実装予定です。

- `GET /health` - ヘルスチェック
- `POST /webhook` - LINE Webhook 受信
  - LINE 署名検証
  - Pub/Sub に Publish
- `POST /api/run` - LIFF API: エージェント実行（同期）
  - LINE Login 検証
  - ADK /run に中継
- `GET /api/run_sse` - LIFF API: エージェント実行（SSE ストリーミング）
  - LINE Login 検証
  - ADK /run_sse に SSE 中継

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
