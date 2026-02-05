# Exercise Log Tools

ExerciseLogs テーブルへの書き込みと読み込みを行う ADK ツールです。

## 提供しているツール

### 1. `create_exercise_log`

運動記録を作成します。

**パラメータ:**

- `exercise_name` (必須): 運動名
- `sets` (必須): セット情報のリスト（JSON）
- `total_sets` (必須): 総セット数
- `category` (オプション): カテゴリ（strength, cardio, flexibility など）
- `muscle_group` (オプション): 対象筋肉群（chest, legs, back など）
- `total_reps` (オプション): 総レップ数
- `total_duration` (オプション): 総時間（秒）
- `total_distance` (オプション): 総距離（km）
- `total_volume` (オプション): 総ボリューム（kg）
- `note` (オプション): メモ
- `recorded_at` (オプション): 記録日時（ISO 8601 形式）

**使用例:**

```python
# 筋トレの記録
result = await create_exercise_log(
    tool_context=ctx,
    exercise_name="ベンチプレス",
    sets=[
        {"reps": 10, "weight": 50},
        {"reps": 8, "weight": 55},
        {"reps": 6, "weight": 60}
    ],
    total_sets=3,
    category="strength",
    muscle_group="chest",
    total_reps=24,
    total_volume=1650.0,
    note="フォームを意識して実施"
)

# 有酸素運動の記録
result = await create_exercise_log(
    tool_context=ctx,
    exercise_name="ランニング",
    sets=[{"duration": 1800, "distance": 5.0}],
    total_sets=1,
    category="cardio",
    total_duration=1800,
    total_distance=5.0,
)
```

### 2. `get_exercise_logs`

ユーザーの運動記録を取得します（記録日時の降順）。

**パラメータ:**

- `limit` (オプション): 取得件数の上限（デフォルト: 10）
- `offset` (オプション): 取得開始位置（デフォルト: 0）

**使用例:**

```python
# 最新 10 件を取得
result = await get_exercise_logs(tool_context=ctx)

# 最新 20 件を取得
result = await get_exercise_logs(tool_context=ctx, limit=20)

# ページネーション（11 件目から 10 件）
result = await get_exercise_logs(tool_context=ctx, limit=10, offset=10)
```

### 3. `get_exercise_logs_by_name`

特定の運動名で記録を取得します（記録日時の降順）。

**パラメータ:**

- `exercise_name` (必須): 運動名
- `limit` (オプション): 取得件数の上限（デフォルト: 10）

**使用例:**

```python
# ベンチプレスの記録を取得
result = await get_exercise_logs_by_name(
    tool_context=ctx,
    exercise_name="ベンチプレス"
)

# ランニングの記録を最新 5 件取得
result = await get_exercise_logs_by_name(
    tool_context=ctx,
    exercise_name="ランニング",
    limit=5
)
```

## エージェントへの統合方法

### 新しいサブエージェントを作成する場合

```python
# sub_agents/exercise_tracker.py
from google.adk.agents import Agent
from ..tools import (
    create_exercise_log,
    get_exercise_logs,
    get_exercise_logs_by_name,
)

exercise_tracker_agent = Agent(
    name="exercise_tracker_agent",
    description="運動記録の管理。運動の記録・履歴確認を担当。",
    instruction="""あなたは運動記録管理エージェントです。

## 役割
- ユーザーの運動記録を作成する
- 過去の運動記録を取得する
- 特定の運動の履歴を確認する

## 使用するツール
- create_exercise_log: 運動記録を作成
- get_exercise_logs: 運動記録の一覧を取得
- get_exercise_logs_by_name: 特定の運動名で記録を取得
""",
    tools=[
        create_exercise_log,
        get_exercise_logs,
        get_exercise_logs_by_name,
    ],
)
```

### 既存のエージェントに追加する場合

```python
# 既存のエージェントの tools に追加
from .tools import (
    create_exercise_log,
    get_exercise_logs,
    get_exercise_logs_by_name,
)

my_agent = Agent(
    name="my_agent",
    tools=[
        # 既存のツール...
        create_exercise_log,
        get_exercise_logs,
        get_exercise_logs_by_name,
    ],
)
```

## レスポンス形式

すべてのツールは以下の形式で結果を返します：

```python
{
    "status": "success" | "not_found" | "error",
    "message": "結果メッセージ",
    # その他の情報（ツールによって異なる）
}
```

## ログ出力

すべてのツールは構造化ログを出力します：

- INFO: 正常な操作（作成、取得）
- WARNING: 軽微な問題（日時のパース失敗など）
- ERROR: エラー発生時

ログには `user_id`、`exercise_name`、操作の詳細が含まれます。
