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
├── README.md
├── app/
│   └── agents/
│       └── health_advisor/        # 健康アドバイザーエージェント
│           ├── __init__.py
│           ├── agent.py           # root_agent (メインエージェント)
│           ├── utils.py           # 共通ツール
│           └── sub_agents/        # サブエージェント
│               ├── __init__.py
│               ├── goal_setting.py      # 目標設定エージェント
│               ├── pre_meal_advisor.py  # 食事前アドバイスエージェント
│               └── meal_record.py       # 食事記録エージェント
└── infra/                         # インフラ (Terraform, Pulumi, etc.)
```

## エージェント構成

```
root_agent (gemini-2.5-flash)
├── goal_setting_agent      # 健康目標の設定・確認
├── pre_meal_advisor_agent  # 食事前のアドバイス・レシピ提案
└── meal_record_agent       # 食事の記録・カロリー推定
```

### 委譲の仕組み

1. ユーザーからのメッセージが `root_agent` に到達
2. `root_agent` がメッセージ内容を解析
3. 各サブエージェントの `description` を参照し、適切なエージェントに委譲
4. サブエージェントがツールを使用して処理を実行
5. 結果をユーザーに返却

## セットアップ

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/your-org/aizap.git
cd aizap/app/agents

# 仮想環境を作成
python -m venv .venv
source .venv/bin/activate

# 依存関係をインストール
pip install google-adk

# 環境変数を設定
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_PROJECT=xxxxxx
export GOOGLE_CLOUD_LOCATION=asia-northeast1
```

## 実行方法

### ADK Web UI で実行

```bash
adk web --port 8000
```