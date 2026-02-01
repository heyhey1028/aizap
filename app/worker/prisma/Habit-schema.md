# Habit Schema Documentation

## 概要

`Habit` モデルは、運動と食事に関する詳細な行動計画を管理するためのテーブルです。Goalテーブルのラフな習慣情報を具体化し、以下の機能を実現します：

- 運動習慣の計画管理（種目、目標値、スケジュール）
- リマインド送信の基盤データ
- スケジュール自動登録
- ExerciseLogとの対応による進捗追跡

## テーブル名

`habits`

## フィールド一覧

| カテゴリ | フィールド名 | 型 | NULL許可 | DB カラム名 | 説明 | 値の例 |
|----------|------------|-----|---------|------------|------|--------|
| **基本** | `habitType` | String | ✗ | `habit_type` | 習慣の種類 | `"exercise"`, `"meal"` |
| | `title` | String | ✗ | `title` | 習慣のタイトル | `"朝のランニング"`, `"夜の筋トレ"` |
| **ルーティン** | `routineId` | String | ✓ | `routine_id` | 複数習慣のグルーピング用識別子 | `"morning-workout"`, `null` |
| | `routineName` | String | ✓ | `routine_name` | ルーティンの表示名 | `"朝のワークアウト"`, `null` |
| | `orderInRoutine` | Int | ✓ | `order_in_routine` | ルーティン内の実行順序 | `1`, `2`, `3`, `null` |
| **運動習慣** | `exerciseName` | String | ✓ | `exercise_name` | 運動種目名 | `"running"`, `"bench_press"`, `null` |
| | `category` | String | ✓ | `category` | 運動カテゴリ | `"strength"`, `"cardio"`, `"flexibility"`, `null` |
| | `targetSets` | Int | ✓ | `target_sets` | 目標セット数 | `3`, `5`, `null` |
| | `targetReps` | Int | ✓ | `target_reps` | 目標レップ数 | `10`, `12`, `null` |
| | `targetDuration` | Int | ✓ | `target_duration` | 目標時間（分単位） | `30`, `60`, `null` |
| | `targetDistance` | Float | ✓ | `target_distance` | 目標距離（km単位） | `5.0`, `10.0`, `null` |
| **食事習慣** | `mealType` | String | ✓ | `meal_type` | 食事の種類 ※Phase 2 | `"breakfast"`, `"lunch"`, `"dinner"`, `"snack"`, `null` |
| | `targetCalories` | Int | ✓ | `target_calories` | 目標カロリー ※Phase 2 | `400`, `600`, `null` |
| | `targetProteins` | Int | ✓ | `target_proteins` | 一日に摂るべきタンパク質の量（g）※Phase 2 | `30`, `40`, `null` |
| | `targetFats` | Int | ✓ | `target_fats` | 一日に摂るべき脂質の量（g）※Phase 2 | `15`, `20`, `null` |
| | `targetCarbohydrates` | Int | ✓ | `target_carbohydrates` | 一日に摂るべき炭水化物の量（g）※Phase 2 | `50`, `80`, `null` |
| **スケジュール** | `frequency` | String | ✗ | `frequency` | 実行頻度 | `"daily"`, `"weekly"`, `"custom"` |
| | `daysOfWeek` | Json | ✓ | `days_of_week` | 実行曜日（JSONB配列） | `["monday", "wednesday", "friday"]`, `null` |
| | `timeOfDay` | String | ✓ | `time_of_day` | 実行時刻（HH:MM形式） | `"07:00"`, `"19:30"`, `null` |
| **ステータス** | `isActive` | Boolean | ✗ | `is_active` | 有効/無効フラグ | `true`, `false` |
| | `startDate` | DateTime | ✗ | `start_date` | 実行期間の開始日 | `2026-01-31T00:00:00Z` |
| | `endDate` | DateTime | ✗ | `end_date` | 実行期間の終了日 | `2026-03-31T23:59:59Z` |
| **リレーション** | `userId` | String | ✗ | `user_id` | ユーザーID | `"U1234567890abcdef"` |
| | `goalId` | String | ✓ | `goal_id` | 関連する目標ID | `"goal-123-456"`, `null` |
| | `user` | UserSession | - | - | - | リレーション（Prisma専用） | - |
| | `goal` | Goal | - | - | - | リレーション（Prisma専用） | - |

## フィールド詳細

### daysOfWeek フィールドの構造

`daysOfWeek` フィールドは JSONB 配列で、週のうちどの曜日に習慣を実行するかを指定します。`frequency="weekly"` の場合に使用します。

**型定義:**
```typescript
type DayOfWeek = 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday'
```

**例:**

| 頻度パターン | daysOfWeek の値 | 説明 |
|------------|----------------|------|
| 毎週月水金 | `["monday", "wednesday", "friday"]` | 週3回のトレーニング |
| 毎週火木 | `["tuesday", "thursday"]` | 週2回のトレーニング |
| 週末のみ | `["saturday", "sunday"]` | 土日のみ |
| 毎日 | `null` | `frequency="daily"` の場合は不要 |

### habitType（習慣の種類）の値

| 値 | 説明 | 使用するフィールド |
|----|------|------------------|
| `"exercise"` | 運動習慣 | `exerciseName`, `category`, `targetSets`, `targetReps`, `targetDuration`, `targetDistance` |
| `"meal"` | 食事習慣 ※Phase 2 | `mealType`, `targetCalories`, `targetProteins`, `targetFats`, `targetCarbohydrates` |

### category（運動カテゴリ）の値

`habitType="exercise"` の場合に使用します。

| 値 | 説明 | 該当する運動例 |
|----|------|--------------|
| `"strength"` | 筋力トレーニング | ベンチプレス、スクワット、デッドリフト、懸垂 |
| `"cardio"` | 有酸素運動 | ランニング、ウォーキング、サイクリング、水泳 |
| `"flexibility"` | 柔軟性・バランス | ヨガ、ストレッチ、ピラティス |
| `null` | 未分類 | - |

### mealType（食事の種類）の値

`habitType="meal"` の場合に使用します。※Phase 2で本格実装

| 値 | 説明 | 時間帯の目安 |
|----|------|------------|
| `"breakfast"` | 朝食 | 6:00-10:00 |
| `"lunch"` | 昼食 | 11:00-14:00 |
| `"dinner"` | 夕食 | 17:00-21:00 |
| `"snack"` | 間食・おやつ | その他の時間帯 |
| `null` | 該当なし | - |

### frequency（実行頻度）の値

| 値 | 説明 | daysOfWeek の要否 |
|----|------|------------------|
| `"daily"` | 毎日実行 | 不要（`null`） |
| `"weekly"` | 週単位で実行 | 必須（曜日を配列で指定） |
| `"custom"` | カスタム設定 | 将来的に特定日指定など |

## インデックス

パフォーマンス最適化のため、以下のインデックスが設定されています。

| インデックス | 対象カラム | 用途 |
|------------|-----------|------|
| **Index 1** | `user_id`, `habit_type`, `is_active` | ユーザーの有効な習慣を種類別に取得 |
| **Index 2** | `user_id`, `routine_id` | ルーティンでグルーピング取得 |
| **Index 3** | `user_id`, `start_date` | 開始日順に習慣を取得 |
| **Index 4** | `goal_id` | 特定目標に紐づく習慣を取得 |

## リレーション

| フィールド | 関連モデル | リレーション | onDelete | 説明 |
|-----------|----------|------------|----------|------|
| `user` | `UserSession` | `user_id` → `user_sessions.user_id` | CASCADE | ユーザーが削除されると、関連する習慣も削除される |
| `goal` | `Goal` | `goal_id` → `goals.id` | SET NULL | 目標が削除されても、習慣は残る（goalIdがNULLになる） |

## 設計ポイント

### 個別レコード管理
複合運動（ランニング+筋トレ）は別レコードとして保存し、`routine_id`でグルーピングします。これにより、各運動の詳細な管理が可能になります。

### ExerciseLogとの整合性
1運動種目=1レコードの設計により、計画（Habit）と実績（ExerciseLog）を正確に対応させることができます。

### 食事習慣対応
Phase 2での拡張を見据えたスキーマ設計となっています。

## 使用例

### 例1: 週3回の朝ランニング習慣

```typescript
{
  userId: "U1234567890abcdef",
  goalId: "goal-123-456",
  habitType: "exercise",
  title: "朝のランニング",

  routineId: null,
  routineName: null,
  orderInRoutine: null,

  exerciseName: "running",
  category: "cardio",
  targetSets: null,
  targetReps: null,
  targetDuration: 30,
  targetDistance: 5.0,

  mealType: null,
  targetCalories: null,
  targetProteins: null,
  targetFats: null,
  targetCarbohydrates: null,

  frequency: "weekly",
  daysOfWeek: ["monday", "wednesday", "friday"],
  timeOfDay: "07:00",

  isActive: true,
  startDate: new Date("2026-01-31T00:00:00Z"),
  endDate: new Date("2026-03-31T23:59:59Z")
}
```

### 例2: 週2回の筋トレ習慣（ベンチプレス）

```typescript
{
  userId: "U1234567890abcdef",
  goalId: "goal-123-456",
  habitType: "exercise",
  title: "ベンチプレス",

  routineId: null,
  routineName: null,
  orderInRoutine: null,

  exerciseName: "bench_press",
  category: "strength",
  targetSets: 3,
  targetReps: 10,
  targetDuration: null,
  targetDistance: null,

  mealType: null,
  targetCalories: null,
  targetProteins: null,
  targetFats: null,
  targetCarbohydrates: null,

  frequency: "weekly",
  daysOfWeek: ["tuesday", "thursday"],
  timeOfDay: "19:00",

  isActive: true,
  startDate: new Date("2026-01-31T00:00:00Z"),
  endDate: new Date("2026-03-31T23:59:59Z")
}
```

### 例3: ルーティンとしてグルーピング（朝のワークアウト）

#### 3-1: ウォーミングアップランニング

```typescript
{
  userId: "U1234567890abcdef",
  goalId: "goal-123-456",
  habitType: "exercise",
  title: "ウォーミングアップランニング",

  routineId: "morning-workout",
  routineName: "朝のワークアウト",
  orderInRoutine: 1,

  exerciseName: "running",
  category: "cardio",
  targetSets: null,
  targetReps: null,
  targetDuration: 10,
  targetDistance: null,

  mealType: null,
  targetCalories: null,
  targetProteins: null,
  targetFats: null,
  targetCarbohydrates: null,

  frequency: "weekly",
  daysOfWeek: ["monday", "wednesday", "friday"],
  timeOfDay: "07:00",

  isActive: true,
  startDate: new Date("2026-01-31T00:00:00Z"),
  endDate: new Date("2026-03-31T23:59:59Z")
}
```

#### 3-2: メインの筋トレ（ベンチプレス）

```typescript
{
  userId: "U1234567890abcdef",
  goalId: "goal-123-456",
  habitType: "exercise",
  title: "ベンチプレス",

  routineId: "morning-workout",
  routineName: "朝のワークアウト",
  orderInRoutine: 2,

  exerciseName: "bench_press",
  category: "strength",
  targetSets: 3,
  targetReps: 10,
  targetDuration: null,
  targetDistance: null,

  mealType: null,
  targetCalories: null,
  targetProteins: null,
  targetFats: null,
  targetCarbohydrates: null,

  frequency: "weekly",
  daysOfWeek: ["monday", "wednesday", "friday"],
  timeOfDay: "07:15",

  isActive: true,
  startDate: new Date("2026-01-31T00:00:00Z"),
  endDate: new Date("2026-03-31T23:59:59Z")
}
```

#### 3-3: クールダウン（ストレッチ）

```typescript
{
  userId: "U1234567890abcdef",
  goalId: "goal-123-456",
  habitType: "exercise",
  title: "ストレッチ",

  routineId: "morning-workout",
  routineName: "朝のワークアウト",
  orderInRoutine: 3,

  exerciseName: "stretching",
  category: "flexibility",
  targetSets: null,
  targetReps: null,
  targetDuration: 10,
  targetDistance: null,

  mealType: null,
  targetCalories: null,
  targetProteins: null,
  targetFats: null,
  targetCarbohydrates: null,

  frequency: "weekly",
  daysOfWeek: ["monday", "wednesday", "friday"],
  timeOfDay: "07:45",

  isActive: true,
  startDate: new Date("2026-01-31T00:00:00Z"),
  endDate: new Date("2026-03-31T23:59:59Z")
}
```

### 例4: 食事習慣（Phase 2）

```typescript
{
  userId: "U1234567890abcdef",
  goalId: "goal-123-456",
  habitType: "meal",
  title: "低糖質な朝食",

  routineId: null,
  routineName: null,
  orderInRoutine: null,

  exerciseName: null,
  category: null,
  targetSets: null,
  targetReps: null,
  targetDuration: null,
  targetDistance: null,

  mealType: "breakfast",
  targetCalories: 400,
  targetProteins: 30,
  targetFats: 15,
  targetCarbohydrates: 30,

  frequency: "daily",
  daysOfWeek: null,
  timeOfDay: "08:00",

  isActive: true,
  startDate: new Date("2026-01-31T00:00:00Z"),
  endDate: new Date("2026-03-31T23:59:59Z")
}
```

## ExerciseLogとの関係

`Habit` テーブルは運動の**計画**を管理し、`ExerciseLog` テーブルは運動の**実績**を記録します。

### 計画と実績の対応

```typescript
// 計画: ランニングの習慣
Habit {
  exerciseName: "running",
  targetDuration: 30,
  targetDistance: 5.0,
  daysOfWeek: ["monday", "wednesday", "friday"]
}

// 実績: ランニングのログ
ExerciseLog {
  exerciseName: "running",
  totalDuration: 32,  // 目標より2分多く達成
  totalDistance: 5.2,  // 目標より0.2km多く達成
  recordedAt: "2026-01-31T07:30:00Z"
}
```

### 達成度チェックの例

```typescript
function checkHabitAchievement(habit: Habit, log: ExerciseLog): boolean {
  // 運動種目が一致するか
  if (habit.exerciseName !== log.exerciseName) {
    return false
  }

  // 目標値と実績を比較
  if (habit.targetDuration && log.totalDuration) {
    if (log.totalDuration < habit.targetDuration) return false
  }

  if (habit.targetDistance && log.totalDistance) {
    if (log.totalDistance < habit.targetDistance) return false
  }

  if (habit.targetSets && log.totalSets) {
    if (log.totalSets < habit.targetSets) return false
  }

  if (habit.targetReps && log.totalReps) {
    if (log.totalReps < habit.targetReps) return false
  }

  return true
}
```

## バリデーション推奨事項

アプリケーション層で以下のバリデーションを実装することを推奨します：

### 1. habitType による条件付きバリデーション

```typescript
// habitType="exercise" の場合
if (habit.habitType === 'exercise') {
  // exerciseName は必須
  if (!habit.exerciseName) {
    throw new Error('exerciseName is required for exercise habits')
  }

  // 食事習慣フィールドは全てnull
  if (habit.mealType || habit.targetCalories || habit.targetProteins) {
    throw new Error('Meal fields should be null for exercise habits')
  }
}

// habitType="meal" の場合
if (habit.habitType === 'meal') {
  // mealType は必須（Phase 2）
  if (!habit.mealType) {
    throw new Error('mealType is required for meal habits')
  }

  // 運動習慣フィールドは全てnull
  if (habit.exerciseName || habit.targetSets || habit.targetReps) {
    throw new Error('Exercise fields should be null for meal habits')
  }
}
```

### 2. frequency による daysOfWeek のバリデーション

```typescript
// frequency="daily" の場合
if (habit.frequency === 'daily') {
  // daysOfWeek は不要（null推奨）
  if (habit.daysOfWeek) {
    console.warn('daysOfWeek is not needed for daily habits')
  }
}

// frequency="weekly" の場合
if (habit.frequency === 'weekly') {
  // daysOfWeek は必須
  if (!habit.daysOfWeek || habit.daysOfWeek.length === 0) {
    throw new Error('daysOfWeek is required for weekly habits')
  }

  // 有効な曜日のみ許可
  const validDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
  for (const day of habit.daysOfWeek) {
    if (!validDays.includes(day)) {
      throw new Error(`Invalid day: ${day}`)
    }
  }
}
```

### 3. routineId によるバリデーション

```typescript
// routineId がある場合
if (habit.routineId) {
  // routineName も必須
  if (!habit.routineName) {
    throw new Error('routineName is required when routineId is set')
  }

  // orderInRoutine も必須
  if (!habit.orderInRoutine) {
    throw new Error('orderInRoutine is required when routineId is set')
  }

  // orderInRoutine は1以上
  if (habit.orderInRoutine < 1) {
    throw new Error('orderInRoutine must be greater than 0')
  }
}
```

### 4. timeOfDay のフォーマットバリデーション

```typescript
// timeOfDay は "HH:MM" 形式
if (habit.timeOfDay) {
  const timeRegex = /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/
  if (!timeRegex.test(habit.timeOfDay)) {
    throw new Error('timeOfDay must be in HH:MM format (e.g., "07:00", "19:30")')
  }
}
```

### 5. 目標値のバリデーション

```typescript
// 目標値は正の数でなければならない
if (habit.targetSets !== null && habit.targetSets <= 0) {
  throw new Error('targetSets must be greater than 0')
}

if (habit.targetReps !== null && habit.targetReps <= 0) {
  throw new Error('targetReps must be greater than 0')
}

if (habit.targetDuration !== null && habit.targetDuration <= 0) {
  throw new Error('targetDuration must be greater than 0')
}

if (habit.targetDistance !== null && habit.targetDistance <= 0) {
  throw new Error('targetDistance must be greater than 0')
}

if (habit.targetCalories !== null && habit.targetCalories <= 0) {
  throw new Error('targetCalories must be greater than 0')
}

if (habit.targetProteins !== null && habit.targetProteins < 0) {
  throw new Error('targetProteins must be non-negative')
}

if (habit.targetFats !== null && habit.targetFats < 0) {
  throw new Error('targetFats must be non-negative')
}

if (habit.targetCarbohydrates !== null && habit.targetCarbohydrates < 0) {
  throw new Error('targetCarbohydrates must be non-negative')
}
```

## 今後の拡張予定

### Phase 2: 食事習慣の本格実装

- MealLogテーブルの追加
- 食事習慣フィールド（mealType、target栄養素）の本格的な利用
- 栄養バランスの分析機能

### Phase 3以降: 高度な機能

- 達成報酬システム
- 習慣の自動調整機能（実績から目標値を最適化）
- 習慣の依存関係管理
- 習慣テンプレート機能
