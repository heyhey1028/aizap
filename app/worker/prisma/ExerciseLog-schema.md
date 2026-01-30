# ExerciseLog Schema Documentation

## 概要

`ExerciseLog` モデルは、ユーザーの運動記録を管理するためのテーブルです。ランニング、筋力トレーニング、ヨガなど、あらゆる種類の運動を統一的に記録できます。

## テーブル名

`exercise_logs`

## フィールド一覧

| フィールド名 | 型 | NULL許可 | デフォルト | DB カラム名 | 説明 | 値の例 |
|------------|-----|---------|-----------|------------|------|--------|
| `id` | String | ✗ | `uuid()` | `id` | 運動ログの一意ID（UUID） | `"550e8400-e29b-41d4-a716-446655440000"` |
| `userId` | String | ✗ | - | `user_id` | ユーザーID（`UserSession.userId` と紐づく） | `"U1234567890abcdef"` |
| `exerciseName` | String | ✗ | - | `exercise_name` | 運動種目名 | `"running"`, `"bench_press"`, `"yoga"`, `"squat"` |
| `sets` | Json | ✗ | - | `sets` | セット記録の配列（JSON） | 詳細は下記「sets フィールドの構造」参照 |
| `category` | String | ✓ | - | `category` | 運動カテゴリ | `"strength"`, `"cardio"`, `"flexibility"`, `null` |
| `muscleGroup` | String | ✓ | - | `muscle_group` | 対象筋群（筋トレの場合） | `"chest"`, `"back"`, `"legs"`, `"shoulders"`, `"arms"`, `"core"`, `null` |
| `totalSets` | Int | ✗ | - | `total_sets` | 合計セット数（`sets` から集計） | `1`, `3`, `5` |
| `totalReps` | Int | ✓ | - | `total_reps` | 合計回数（筋トレの場合、`sets` から集計） | `27`, `null` |
| `totalDuration` | Int | ✓ | - | `total_duration` | 合計時間（分単位、`sets` から集計） | `30`, `60`, `null` |
| `totalDistance` | Float | ✓ | - | `total_distance` | 合計距離（km単位、`sets` から集計） | `5.2`, `10.5`, `null` |
| `totalVolume` | Float | ✓ | - | `total_volume` | 合計ボリューム（重量×回数の合計、`sets` から集計） | `2160.0`, `null` |
| `note` | String | ✓ | - | `note` | ユーザーのメモ | `"朝ラン"`, `"胸の日"`, `"目標達成！"`, `null` |
| `recordedAt` | DateTime | ✗ | `now()` | `recorded_at` | 運動を実際に行った日時 | `2026-01-30T09:00:00Z` |
| `createdAt` | DateTime | ✗ | `now()` | `created_at` | レコードがDBに作成された日時 | `2026-01-30T09:05:00Z` |
| `user` | UserSession | - | - | - | リレーション（Prisma専用、DBには存在しない） | - |

## sets フィールドの構造

`sets` フィールドは JSON 配列で、各セットの詳細情報を保持します。運動の種類によって含まれるフィールドが異なります。

### 型定義

```typescript
type SetRecord = {
  duration?: number;  // 時間（分）
  distance?: number;  // 距離（km）
  weight?: number;    // 重量（kg）
  reps?: number;      // 回数
};
```

### 有酸素運動（ランニング、ウォーキング）

| 運動種目 | sets の例 | 説明 |
|---------|-----------|------|
| ランニング | `[{ "duration": 30, "distance": 5.2 }]` | 30分間で5.2km走った |
| ウォーキング | `[{ "duration": 45, "distance": 3.0 }]` | 45分間で3.0km歩いた |
| ランニング（距離不明） | `[{ "duration": 30 }]` | 30分間走った（距離は記録なし） |

### 筋力トレーニング

| 運動種目 | sets の例 | 説明 |
|---------|-----------|------|
| ベンチプレス | `[{ "weight": 80, "reps": 10 }, { "weight": 80, "reps": 9 }, { "weight": 80, "reps": 8 }]` | 80kg×10回、80kg×9回、80kg×8回の3セット |
| スクワット | `[{ "weight": 100, "reps": 12 }, { "weight": 100, "reps": 12 }]` | 100kg×12回を2セット |
| 懸垂（自重） | `[{ "reps": 10 }, { "reps": 8 }, { "reps": 6 }]` | 10回、8回、6回の3セット（体重のみ） |
| プランク | `[{ "duration": 1 }]` | 1分間キープ |

### 時間ベース（ヨガ、ストレッチ）

| 運動種目 | sets の例 | 説明 |
|---------|-----------|------|
| ヨガ | `[{ "duration": 60 }]` | 60分間のヨガセッション |
| ストレッチ | `[{ "duration": 15 }]` | 15分間のストレッチ |

## category（運動カテゴリ）の値

| 値 | 説明 | 該当する運動例 |
|----|------|--------------|
| `"strength"` | 筋力トレーニング | ベンチプレス、スクワット、デッドリフト、懸垂 |
| `"cardio"` | 有酸素運動 | ランニング、ウォーキング、サイクリング、水泳 |
| `"flexibility"` | 柔軟性・バランス | ヨガ、ストレッチ、ピラティス |
| `null` | 未分類 | - |

## muscleGroup（対象筋群）の値

筋力トレーニング（`category: "strength"`）の場合に使用します。

| 値 | 説明 | 該当する運動例 |
|----|------|--------------|
| `"chest"` | 胸筋 | ベンチプレス、ダンベルフライ、プッシュアップ |
| `"back"` | 背筋 | 懸垂、デッドリフト、ベントオーバーロウ |
| `"legs"` | 脚 | スクワット、レッグプレス、ランジ |
| `"shoulders"` | 肩 | ショルダープレス、サイドレイズ |
| `"arms"` | 腕（二頭筋・三頭筋） | カール、トライセップエクステンション |
| `"core"` | 体幹 | プランク、クランチ、レッグレイズ |
| `null` | 該当なし | 有酸素運動、ヨガなど |

## exerciseName（運動種目名）の例

| カテゴリ | exerciseName の例 |
|---------|------------------|
| 筋力トレーニング | `bench_press`, `squat`, `deadlift`, `pull_up`, `push_up`, `shoulder_press`, `bicep_curl`, `plank` |
| 有酸素運動 | `running`, `walking`, `cycling`, `swimming`, `jump_rope` |
| 柔軟性・バランス | `yoga`, `stretching`, `pilates` |

## 集計フィールドの計算方法

集計フィールド（`total*`）は、`sets` から自動計算されます。

| フィールド | 計算方法 | 例 |
|-----------|---------|-----|
| `totalSets` | `sets.length` | `[{...}, {...}, {...}]` → `3` |
| `totalReps` | `sets.reduce((sum, s) => sum + (s.reps || 0), 0)` | `[{reps: 10}, {reps: 9}, {reps: 8}]` → `27` |
| `totalDuration` | `sets.reduce((sum, s) => sum + (s.duration || 0), 0)` | `[{duration: 30}]` → `30` |
| `totalDistance` | `sets.reduce((sum, s) => sum + (s.distance || 0), 0)` | `[{distance: 5.2}]` → `5.2` |
| `totalVolume` | `sets.reduce((sum, s) => sum + (s.weight || 0) * (s.reps || 0), 0)` | `[{weight: 80, reps: 10}, {weight: 80, reps: 9}]` → `1520` |

## インデックス

パフォーマンス最適化のため、以下のインデックスが設定されています。

| インデックス | 対象カラム | 用途 |
|------------|-----------|------|
| Primary Key | `id` | レコードの一意識別 |
| Index 1 | `user_id`, `recorded_at DESC` | ユーザーの最新記録を高速取得 |
| Index 2 | `user_id`, `exercise_name`, `recorded_at DESC` | 特定種目の履歴を高速取得 |
| Index 3 | `user_id`, `category` | カテゴリ別の集計を高速化 |

## リレーション

| フィールド | 関連モデル | 関係 | onDelete | 説明 |
|-----------|----------|------|----------|------|
| `user` | `UserSession` | Many-to-One | CASCADE | ユーザーが削除されると、関連する運動記録も削除される |

## 使用例

### ランニング記録

```typescript
{
  id: "550e8400-e29b-41d4-a716-446655440000",
  userId: "U1234567890abcdef",
  exerciseName: "running",
  sets: [{ duration: 30, distance: 5.2 }],
  category: "cardio",
  muscleGroup: null,
  totalSets: 1,
  totalReps: null,
  totalDuration: 30,
  totalDistance: 5.2,
  totalVolume: null,
  note: "朝ラン",
  recordedAt: new Date("2026-01-30T09:00:00Z"),
  createdAt: new Date("2026-01-30T09:05:00Z")
}
```

### ベンチプレス記録

```typescript
{
  id: "660e8400-e29b-41d4-a716-446655440001",
  userId: "U1234567890abcdef",
  exerciseName: "bench_press",
  sets: [
    { weight: 80, reps: 10 },
    { weight: 80, reps: 9 },
    { weight: 80, reps: 8 }
  ],
  category: "strength",
  muscleGroup: "chest",
  totalSets: 3,
  totalReps: 27,
  totalDuration: null,
  totalDistance: null,
  totalVolume: 2160,
  note: "胸の日",
  recordedAt: new Date("2026-01-30T19:00:00Z"),
  createdAt: new Date("2026-01-30T19:10:00Z")
}
```

### ヨガ記録

```typescript
{
  id: "770e8400-e29b-41d4-a716-446655440002",
  userId: "U1234567890abcdef",
  exerciseName: "yoga",
  sets: [{ duration: 60 }],
  category: "flexibility",
  muscleGroup: null,
  totalSets: 1,
  totalReps: null,
  totalDuration: 60,
  totalDistance: null,
  totalVolume: null,
  note: "パワーヨガ",
  recordedAt: new Date("2026-01-30T07:00:00Z"),
  createdAt: new Date("2026-01-30T07:05:00Z")
}
```

## バリデーション推奨事項

アプリケーション層で以下のバリデーションを実装することを推奨します：

1. **sets フィールド**
   - 必ず配列であること
   - 少なくとも1つの要素を含むこと
   - 各要素は `SetRecord` 型に準拠すること

2. **category と muscleGroup**
   - `category` が `"strength"` の場合のみ `muscleGroup` を設定
   - 定義された値のみを許可（Enum的に扱う）

3. **集計フィールド**
   - `sets` から計算された値と一致すること
   - ヘルパー関数で自動計算を推奨

4. **recordedAt と createdAt**
   - `recordedAt` は未来の日時を許可しない
   - `createdAt >= recordedAt` であること（システム時刻の信頼性に依存）

詳細は `/app/worker/src/types/exercise-log.ts` および `/app/worker/src/utils/exercise-calculations.ts` を参照してください。
