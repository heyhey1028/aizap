# DB アクセス層

ADK から Cloud SQL PostgreSQL にアクセスするためのリポジトリ層。

## ディレクトリ構造

```text
db/
├── config.py           # 接続設定（Cloud SQL Python Connector）
├── models/             # SQLAlchemy モデル
│   ├── base.py
│   ├── user_session.py
│   ├── goal.py
│   └── exercise_log.py
└── repositories/       # リポジトリ（CRUD 操作）
    ├── base.py
    ├── user_session.py
    ├── goal.py
    └── exercise_log.py
```

## 重要: Prisma スキーマとの同期

**`models/` のファイルは `app/worker/prisma/schema.prisma` と必ず一致させる必要があります。**

### 変更が必要なタイミング

1. **Prisma スキーマにテーブルを追加した場合**
   - `models/` に新しいモデルファイルを作成
   - `models/__init__.py` にエクスポートを追加
   - 必要に応じて `repositories/` にリポジトリを追加

2. **Prisma スキーマのカラムを変更した場合**
   - 対応する `models/*.py` のフィールドを更新

3. **Prisma スキーマにインデックスを追加した場合**
   - 対応する `models/*.py` の `__table_args__` を更新

### 変更が不要なタイミング

- マイグレーションの実行（Worker 側で管理）
- データの読み書き（リポジトリ層を使用）

## ADK ツールからの使い方

### 基本的な使い方

```python
from db.config import get_async_session
from db.repositories import GoalRepository

async def my_tool(tool_context: ToolContext) -> dict:
    user_id = tool_context.user_id
    
    async with get_async_session() as session:
        repo = GoalRepository(session)
        goal = await repo.get_by_user_id(user_id)
        
        if goal is None:
            return {"status": "not_found"}
        
        return {"status": "success", "goal": goal.details}
```

### リポジトリのメソッド

各リポジトリは `BaseRepository` を継承しており、以下の共通メソッドがあります：

| メソッド | 説明 |
|----------|------|
| `get_by_id(id)` | ID でレコードを取得 |
| `get_all(limit, offset)` | 全レコードを取得 |
| `create(**kwargs)` | レコードを作成 |
| `update(id, **kwargs)` | レコードを更新 |
| `delete(id)` | レコードを削除 |

各リポジトリには追加のメソッドもあります（例: `GoalRepository.get_by_user_id()`）。

### エラーハンドリング

```python
from utils.logger import get_logger

logger = get_logger(__name__)

async def my_tool(tool_context: ToolContext) -> dict:
    try:
        async with get_async_session() as session:
            repo = GoalRepository(session)
            await repo.create_goal(user_id=user_id, details="...", habits="...")
            logger.info("目標を保存しました", user_id=user_id)
    except Exception as e:
        logger.error("DB への保存に失敗", user_id=user_id, error=str(e))
        # エラー時も処理を続行する場合はここで return しない
```

## 環境変数

| 環境変数 | 説明 | ローカル | Agent Engine |
|----------|------|----------|--------------|
| `CLOUD_SQL_INSTANCE` | インスタンス接続名 | 必須 | 必須 |
| `DB_NAME` | データベース名 | 必須 | 必須 |
| `DB_USER` | IAM ユーザー | 不要（ADC から取得） | 必須 |

### ローカル開発

サービスアカウントのなりすましを使って ADK サービスアカウントの権限で接続します。

```bash
# 1. サービスアカウントのなりすましでユーザーアカウント（開発者）が ADC を設定
gcloud auth application-default login \
  --impersonate-service-account=aizap-adk-sa@aizap-dev.iam.gserviceaccount.com

# 2. 環境変数を設定
export CLOUD_SQL_INSTANCE=aizap-dev:asia-northeast1:aizap-postgres-dev
export DB_NAME=aizap

# 3. テスト実行
uv run python db/test_db.py
```

## 注意事項

- **マイグレーションは Worker 側で管理** - ADK 側ではスキーマ変更を行わない
- **user_id の取得** - `tool_context.user_id` から取得（Agent Engine API で渡される）
