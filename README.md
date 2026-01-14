# aizap

AI Nutritionist & Coaching - 健康アドバイザーエージェント

## 概要

aizap は Google ADK (Agent Development Kit) を使用した AI 健康アドバイザーです。
ユーザーの健康目標設定、食事前アドバイス、食事記録をサポートします。

## MVP 機能

- **健康目標設定**: 減量、筋肉増量、睡眠改善などの目標を設定・管理
- **食事前アドバイス**: 時間帯や過去の食事を考慮したメニュー提案
- **食事記録**: テキストや画像から食事内容とカロリーを記録

## ディレクトリ構成

```
aizap/
├── .github/
│   ├── actions/                    # 再利用可能な Composite Actions
│   └── workflows/                  # CI/CD ワークフロー
├── app/
│   ├── bff/                        # LINE Webhook, LIFF API
│   ├── worker/                     # Pub/Sub -> Agent Engine -> LINE
│   └── adk/                        # ADK エージェント
│       └── agents/
│           └── health_advisor/
├── infra/
│   ├── dev/                        # 開発環境 Terraform
│   ├── prod/                       # 本番環境 Terraform
│   └── modules/                    # 共通モジュール
├── docs/                           # 詳細ドキュメント
└── README.md
```

## クイックスタート

### 1. リポジトリをクローン

```bash
git clone https://github.com/heyhey1028/aizap.git
cd aizap/app/adk
```

### 2. セットアップ

```bash
# 仮想環境を作成・有効化
python -m venv .venv
source .venv/bin/activate

# ADK をインストール
pip install google-adk

# GCP 認証
gcloud auth application-default login

# 環境変数を設定
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_PROJECT=aizap-dev
export GOOGLE_CLOUD_LOCATION=asia-northeast1
```

### 3. ADK を起動

```bash
adk web agents/health_advisor
```

ブラウザで http://localhost:8000 にアクセス

## ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| [アーキテクチャ](docs/architecture.md) | システム構成、コンポーネント、環境 |
| [CI/CD](docs/cicd.md) | ワークフロー、Composite Actions、デプロイ |
| [開発ガイド](docs/development.md) | ローカル開発、ADK コマンド、デプロイ手順 |
