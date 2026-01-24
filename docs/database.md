# データベース設計

## 概要

aizap では PostgreSQL を使用し、Prisma ORM でデータアクセスを行います。

| 項目 | 詳細 |
|------|------|
| DBMS | PostgreSQL 17 |
| ORM | Prisma 7.x |
| インフラ | Google Cloud SQL |

## ER図

```mermaid
erDiagram
    users ||--o{ goals : "has"
    users ||--o{ habits : "has"
    goals ||--o{ goal_progress : "tracks"
    goals ||--o{ habits : "optional"
    habits ||--o{ habit_logs : "logs"

    users {
        uuid id PK
        text line_user_id UK "LINE user_id"
        text display_name
        text session_id "Agent Engine session"
        text secret_value "encrypted secret"
        text secret_salt "salt for encryption"
        timestamp created_at
        timestamp updated_at
    }

    goals {
        uuid id PK
        uuid user_id FK
        enum goal_type "quantitative / qualitative"
        text type "weight, body_fat, sleep etc."
        text description
        decimal target_value "for quantitative"
        text unit "kg, %, hours etc."
        enum status "active / achieved / abandoned"
        timestamp created_at
        timestamp updated_at
    }

    goal_progress {
        uuid id PK
        uuid goal_id FK
        decimal value
        timestamp recorded_at
        timestamp created_at
    }

    habits {
        uuid id PK
        uuid user_id FK
        uuid goal_id FK "nullable"
        text name
        text type "exercise, meal, sleep etc."
        text unit "km, kcal, hours etc."
        text target_frequency "daily, weekly etc."
        decimal target_value "per session"
        timestamp created_at
        timestamp updated_at
    }

    habit_logs {
        uuid id PK
        uuid habit_id FK
        decimal value
        text note
        timestamp performed_at
        timestamp created_at
    }
```

## テーブル定義

### users

ユーザー情報と Agent Engine セッションを管理する。

| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| id | UUID | PK | ユーザーID |
| line_user_id | TEXT | UNIQUE, NOT NULL | LINE の user_id |
| display_name | TEXT | NOT NULL | 表示名 |
| session_id | TEXT | | Agent Engine セッションID |
| secret_value | TEXT | | 暗号化されたシークレット |
| secret_salt | TEXT | | 暗号化用ソルト |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

### goals

ユーザーの目標を管理する。定量的・定性的の両方に対応。

| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| id | UUID | PK | 目標ID |
| user_id | UUID | FK(users), NOT NULL | ユーザーID |
| goal_type | ENUM | NOT NULL | `quantitative` / `qualitative` |
| type | TEXT | | 目標の種類（weight, body_fat, sleep など） |
| description | TEXT | | 目標の説明 |
| target_value | DECIMAL | | 目標値（定量目標の場合） |
| unit | TEXT | | 単位（kg, %, hours など） |
| status | ENUM | NOT NULL | `active` / `achieved` / `abandoned` |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

**goal_type による使い分け:**

| goal_type | type | description | target_value | unit |
|-----------|------|-------------|--------------|------|
| quantitative | 必須 | 任意 | 必須 | 必須 |
| qualitative | null | 必須 | null | null |

### goal_progress

目標に対する進捗（現在地）を記録する。

| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| id | UUID | PK | 進捗ID |
| goal_id | UUID | FK(goals), NOT NULL | 目標ID |
| value | DECIMAL | NOT NULL | 記録値 |
| recorded_at | TIMESTAMP | NOT NULL | 記録日時 |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

### habits

目標達成のために行う習慣を定義する。

| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| id | UUID | PK | 習慣ID |
| user_id | UUID | FK(users), NOT NULL | ユーザーID |
| goal_id | UUID | FK(goals) | 関連する目標ID（任意） |
| name | TEXT | NOT NULL | 習慣名 |
| type | TEXT | NOT NULL | 種類（exercise, meal, sleep など） |
| unit | TEXT | | 単位（km, kcal, hours など） |
| target_frequency | TEXT | | 頻度目標（daily, weekly など） |
| target_value | DECIMAL | | 1回あたりの目標値 |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

### habit_logs

習慣の実施記録を保存する。

| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| id | UUID | PK | ログID |
| habit_id | UUID | FK(habits), NOT NULL | 習慣ID |
| value | DECIMAL | | 実績値 |
| note | TEXT | | メモ（「朝食」「朝ラン」など） |
| performed_at | TIMESTAMP | NOT NULL | 実施日時 |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

## リレーション

| 親テーブル | 子テーブル | 関係 | 説明 |
|-----------|-----------|------|------|
| users | goals | 1:N | ユーザーは複数の目標を持てる |
| users | habits | 1:N | ユーザーは複数の習慣を持てる |
| goals | goal_progress | 1:N | 目標に対して複数の進捗を記録 |
| goals | habits | 1:N (optional) | 習慣は任意で目標に紐づく |
| habits | habit_logs | 1:N | 習慣に対して複数のログを記録 |

## 使用例

### 定量的な目標とその進捗

```
User: 田中さん
  └── Goal: 体重60kgにする (quantitative)
        ├── type: "weight"
        ├── target_value: 60
        ├── unit: "kg"
        │
        ├── Progress: 1/20 → 63.0kg
        ├── Progress: 1/22 → 62.5kg
        └── Progress: 1/24 → 62.0kg
```

### 定性的な目標

```
User: 田中さん
  └── Goal: 健康的な生活習慣を身につける (qualitative)
        ├── description: "健康的な生活習慣を身につける"
        └── status: "active"
```

### 目標に紐づく習慣

```
User: 田中さん
  ├── Goal: 体重60kg
  │
  └── Habit: ランニング → Goal「体重60kg」に紐づく
        ├── target_frequency: "daily"
        ├── target_value: 5
        ├── unit: "km"
        │
        ├── Log: 1/24 5km (達成)
        ├── Log: 1/25 3km (未達成)
        └── Log: 1/26 6km (達成)
```

### 目標に紐づかない習慣

```
User: 田中さん
  └── Habit: 水を2L飲む (goal_id = null)
        ├── target_frequency: "daily"
        ├── target_value: 2
        ├── unit: "L"
        │
        └── Log: 1/24 2L
```

## 設計方針

### 目標管理

- **定量的目標**: 体重、体脂肪率など数値で測定可能な目標
- **定性的目標**: 「健康になりたい」など数値化しにくい目標
- 両方を同じ `goals` テーブルで管理し、`goal_type` で区別する

### 習慣管理

- 習慣（habits）には頻度目標（`target_frequency`）を設定可能
- 習慣は目標に紐づけることもできるし、単独でも管理できる
- 「今週何回達成できたか」などの振り返りに活用

### Agent Engine セッション

- `users.session_id` で Agent Engine のセッションを管理
- 1ユーザー = 1セッションの関係
