# Health Advisor Tools

ExerciseLogs テーブルおよび Habits テーブルへの書き込みと読み込みを行う ADK ツールです。

## 提供しているツール

## Exercise Log Tools

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
    create_exercise_habit,
    create_meal_habit,
    get_habits,
    get_habits_by_goal,
    get_habits_by_routine,
    update_habit,
    deactivate_habit,
    activate_habit,
    finish_task,
)

my_agent = Agent(
    name="my_agent",
    tools=[
        # 既存のツール...
        create_exercise_log,
        get_exercise_logs,
        get_exercise_logs_by_name,
        create_exercise_habit,
        create_meal_habit,
        get_habits,
        get_habits_by_goal,
        get_habits_by_routine,
        update_habit,
        deactivate_habit,
        activate_habit,
        finish_task,
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

## Habit Tools

### 1. `create_exercise_habit`

運動習慣計画を作成します。

**パラメータ:**

- `title` (必須): タイトル（例: ベンチプレス、モーニングランニング）
- `frequency` (必須): 頻度（"daily", "weekly", "custom"）
- `goal_id` (オプション): 関連する目標 ID
- `description` (オプション): 説明
- `routine_id` (オプション): ルーティン ID（複数の習慣をグループ化）
- `routine_name` (オプション): ルーティン名
- `order_in_routine` (オプション): ルーティン内の順序
- `exercise_name` (オプション): 運動名
- `category` (オプション): カテゴリ（strength, cardio, flexibility）
- `muscle_group` (オプション): 対象筋肉群（chest, legs, back 等）
- `target_sets` (オプション): 目標セット数
- `target_reps` (オプション): 目標レップ数
- `target_duration` (オプション): 目標時間（秒）
- `target_distance` (オプション): 目標距離（km）
- `target_weight` (オプション): 目標重量（kg）
- `days_of_week` (オプション): 曜日リスト（例: ["monday", "wednesday"]）
- `time_of_day` (オプション): 時刻（HH:MM 形式）
- `is_active` (オプション): アクティブ状態（デフォルト: True）
- `start_date` (オプション): 開始日時（ISO 8601 形式）
- `end_date` (オプション): 終了日時（ISO 8601 形式）
- `notes` (オプション): メモ
- `priority` (オプション): 優先度（1-5）

**使用例:**

```python
# 筋トレ習慣の作成
result = await create_exercise_habit(
    tool_context=ctx,
    title="ベンチプレス",
    frequency="weekly",
    exercise_name="ベンチプレス",
    category="strength",
    muscle_group="chest",
    target_sets=3,
    target_reps=10,
    target_weight=60.0,
    days_of_week=["monday", "thursday"],
    time_of_day="18:00",
)

# 有酸素運動習慣の作成
result = await create_exercise_habit(
    tool_context=ctx,
    title="モーニングランニング",
    frequency="daily",
    exercise_name="ランニング",
    category="cardio",
    target_duration=1800,
    target_distance=5.0,
    time_of_day="06:00",
)
```

### 2. `create_meal_habit`

食事習慣計画を作成します。

**パラメータ:**

- `title` (必須): タイトル（例: 朝食、プロテイン摂取）
- `frequency` (必須): 頻度（"daily", "weekly", "custom"）
- `goal_id` (オプション): 関連する目標 ID
- `description` (オプション): 説明
- `routine_id` (オプション): ルーティン ID（複数の習慣をグループ化）
- `routine_name` (オプション): ルーティン名
- `order_in_routine` (オプション): ルーティン内の順序
- `meal_type` (オプション): 食事タイプ（breakfast, lunch, dinner, snack）
- `target_calories` (オプション): 目標カロリー
- `target_proteins` (オプション): 目標タンパク質（g）
- `target_fats` (オプション): 目標脂質（g）
- `target_carbohydrates` (オプション): 目標炭水化物（g）
- `meal_guidelines` (オプション): 食事ガイドライン
- `days_of_week` (オプション): 曜日リスト（例: ["monday", "wednesday"]）
- `time_of_day` (オプション): 時刻（HH:MM 形式）
- `is_active` (オプション): アクティブ状態（デフォルト: True）
- `start_date` (オプション): 開始日時（ISO 8601 形式）
- `end_date` (オプション): 終了日時（ISO 8601 形式）
- `notes` (オプション): メモ
- `priority` (オプション): 優先度（1-5）

**使用例:**

```python
# 朝食習慣の作成
result = await create_meal_habit(
    tool_context=ctx,
    title="朝食",
    frequency="daily",
    meal_type="breakfast",
    target_calories=500,
    target_proteins=30,
    target_fats=15,
    target_carbohydrates=50,
    time_of_day="07:00",
)

# プロテイン摂取習慣の作成
result = await create_meal_habit(
    tool_context=ctx,
    title="トレーニング後プロテイン",
    frequency="weekly",
    meal_type="snack",
    target_calories=150,
    target_proteins=25,
    days_of_week=["monday", "wednesday", "friday"],
    time_of_day="19:00",
)
```

### 3. `get_habits`

ユーザーの習慣計画を取得します（開始日の降順）。

**パラメータ:**

- `habit_type` (オプション): 習慣タイプでフィルタ（"exercise" または "meal"）
- `is_active` (オプション): アクティブ状態でフィルタ
- `limit` (オプション): 取得件数の上限（デフォルト: 100）
- `offset` (オプション): 取得開始位置（デフォルト: 0）

**使用例:**

```python
# 全習慣を取得
result = await get_habits(tool_context=ctx)

# アクティブな運動習慣のみ取得
result = await get_habits(
    tool_context=ctx,
    habit_type="exercise",
    is_active=True
)
```

### 4. `get_habits_by_goal`

目標 ID に紐づく習慣計画を取得します。

**パラメータ:**

- `goal_id` (必須): 目標 ID
- `is_active` (オプション): アクティブ状態でフィルタ
- `limit` (オプション): 取得件数の上限（デフォルト: 100）

**使用例:**

```python
result = await get_habits_by_goal(
    tool_context=ctx,
    goal_id="goal-123",
    is_active=True
)
```

### 5. `get_habits_by_routine`

ルーティン ID に紐づく習慣計画を取得します（ルーティン内の順序順）。

**パラメータ:**

- `routine_id` (必須): ルーティン ID
- `is_active` (オプション): アクティブ状態でフィルタ

**使用例:**

```python
result = await get_habits_by_routine(
    tool_context=ctx,
    routine_id="morning-routine",
    is_active=True
)
```

### 6. `update_habit`

習慣計画を更新します。

**パラメータ:**

- `habit_id` (必須): 習慣計画 ID
- `**kwargs`: 更新するフィールド値（例: title, target_sets 等）

**使用例:**

```python
# タイトルを更新
result = await update_habit(
    tool_context=ctx,
    habit_id="habit-123",
    title="新しいタイトル"
)

# 目標値を更新
result = await update_habit(
    tool_context=ctx,
    habit_id="habit-123",
    target_sets=4,
    target_reps=12
)
```

### 7. `deactivate_habit`

習慣計画を非アクティブ化します。

**パラメータ:**

- `habit_id` (必須): 習慣計画 ID

**使用例:**

```python
result = await deactivate_habit(
    tool_context=ctx,
    habit_id="habit-123"
)
```

### 8. `activate_habit`

習慣計画をアクティブ化します。

**パラメータ:**

- `habit_id` (必須): 習慣計画 ID

**使用例:**

```python
result = await activate_habit(
    tool_context=ctx,
    habit_id="habit-123"
)
```

## ログ出力

すべてのツールは構造化ログを出力します：

- INFO: 正常な操作（作成、取得）
- WARNING: 軽微な問題（日時のパース失敗など）
- ERROR: エラー発生時

ログには `user_id`、`exercise_name` または `habit_id`、操作の詳細が含まれます。
