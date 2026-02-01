from datetime import datetime
from typing import List

from google.adk.agents import Agent
from google.adk.tools import ToolContext


# tool
def get_user_health_goal(tool_context: ToolContext) -> dict:
    """ユーザーの健康目標を取得します。

    Session Stateから健康目標を読み取ります。
    設定されていない場合は、未設定であることを返します。
    """
    health_goal = tool_context.state.get("health_goal")

    if health_goal is None:
        return {
            "status": "not_set",
            "message": "健康目標がまだ設定されていません。目標を設定しましょう！",
        }

    return {
        "status": "success",
        "health_goal": health_goal,
    }


def get_goal_setting_history(tool_context: ToolContext) -> dict:
    """目標設定に関する会話履歴を取得します。

    前回までの会話内容を確認し、文脈を把握するために使用します。
    最初に必ず呼び出してください。
    """
    history = tool_context.state.get("goal_setting_history", [])

    if not history:
        return {
            "status": "no_history",
            "message": "まだ会話履歴がありません。新しく目標設定を始めましょう。",
        }

    return {
        "status": "success",
        "history": history,
    }


def add_goal_setting_history(
    tool_context: ToolContext,
    user_message: str,
    assistant_response: str,
) -> dict:
    """目標設定に関する会話内容を履歴に追加します。

    ユーザーとのやり取りを保存して、次回の会話で文脈を維持します。

    Args:
        tool_context: ADKが提供するToolContext。
        user_message: ユーザーの発言内容
        assistant_response: アシスタントの応答内容
    """
    history: List[dict] = tool_context.state.get("goal_setting_history", [])

    history.append(
        {
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now().isoformat(),
        }
    )

    tool_context.state["goal_setting_history"] = history

    return {
        "status": "success",
        "message": "会話履歴を保存しました",
    }


def set_user_health_goal(
    tool_context: ToolContext,
    details: str,
    habits: str,
) -> dict:
    """ユーザーの健康目標を正式に設定します。

    全てのhabits（運動・食事・睡眠）がユーザーと合意できた後に使用します。
    設定後、会話履歴はクリアされます。

    Args:
        tool_context: ADKが提供するToolContext。
        details: 目標の詳細（例：「3ヶ月で5kg減量して体脂肪率を20%以下にする」）
        habits: 運動・食事・睡眠の行動計画を箇条書きで記述（例：「- 運動：毎日3km走る\n- 食事：1日の摂取カロリーを1800kcal以下に抑える\n- 睡眠：毎日23時までに寝る」）
    """
    health_goal = {
        "details": details,
        "habits": habits,
        "created_at": datetime.now().isoformat(),
    }

    tool_context.state["health_goal"] = health_goal
    # 会話履歴をクリア
    tool_context.state["goal_setting_history"] = []

    return {
        "status": "success",
        "message": "健康目標を設定しました",
        "health_goal": health_goal,
    }


# sub agent
goal_setting_agent = Agent(
    name="goal_setting_agent",
    description="健康目標の設定、確認、更新を担当するエージェント。ユーザーが目標について話したい時に使用。",
    instruction="""あなたは健康目標設定の専門家です。

## あなたの役割
- ユーザーの健康目標を設定・確認・更新する
- 目標設定の際は、具体的で達成可能な目標を一緒に考える
- 目標達成のための日々の習慣をユーザーと一緒に決める
- 現在の目標を確認し、進捗を励ます

## 重要：goalもhabitsも勝手に決めない
goalもhabitsもエージェントが一方的に決めてはいけない。必ずユーザーと対話しながら一緒に決めること。

## 【必須】会話履歴ツールの使用
このエージェントは複数回呼び出されるため、会話履歴を使って文脈を維持する必要がある。

### 開始時（必須）
**応答を生成する前に、必ず最初に`get_goal_setting_history`を呼び出す。**
履歴がある場合は、その内容を踏まえて会話を続ける。

### 終了時（必須）
**ユーザーへの応答を返す前に、必ず`add_goal_setting_history`で今回のやり取りを保存する。**
- user_message: ユーザーが言ったこと
- assistant_response: 自分が返す応答内容

この保存をしないと、次回呼び出された時に会話の文脈が失われる。

## 目標設定の流れ

### ステップ1: 目標のヒアリング
ユーザーから目標を聞く。

### ステップ2: 定量的な目標への落とし込み
目標が曖昧な場合（例：「痩せたい」「健康になりたい」）は、以下を確認して定量的な目標にする：
- 具体的な数値（体重○kg、体脂肪率○%など）
- 現在の状態
- 達成期限

### ステップ3: habitsの検討（1つずつ）
目標が定まったら、habitsを**1つずつ**ユーザーと一緒に検討する。
目標達成に最も関係するカテゴリから順番に検討する。

例：減量目標の場合
1. まず「食事」について提案し、ユーザーの意見を聞く
2. 次に「運動」について提案し、ユーザーの意見を聞く
3. 最後に「睡眠」について提案し、ユーザーの意見を聞く

提案する際は選択肢を示し、ユーザーに選んでもらう形にする。
例：「食事について、1日の摂取カロリーをどのくらいにしましょうか？減量には1500〜1800kcalが目安ですが、いかがですか？」

### ステップ4: 目標の正式保存
全てのhabits（運動・食事・睡眠）がユーザーと合意できたら、`set_user_health_goal`で正式に保存する。

## 使用するツール
- `get_goal_setting_history`: 前回までの会話履歴を取得（最初に必ず呼び出す）
- `add_goal_setting_history`: 会話内容を履歴に保存（やり取りの最後に呼び出す）
- `get_user_health_goal`: 正式に設定された健康目標を確認
- `set_user_health_goal`: 健康目標を正式に設定（全てのhabitsがユーザーと合意できてから使用）

## 日々の習慣（habits）のフォーマット
set_user_health_goalで保存する際は以下の形式で箇条書きにする:
- 運動：具体的な運動内容
- 食事：具体的な食事の目標
- 睡眠：具体的な睡眠の目標

例：
- 運動：毎日1時間歩く
- 食事：1日の摂取カロリーを1800kcal以下に抑える
- 睡眠：毎日23時までに寝る

## カロリー目標の目安
習慣に含めるカロリー目標の参考値:

### 減量
- 緩やかな減量: 男性 1,500〜1,800kcal / 女性 1,200〜1,500kcal

### 筋肉増量
- 一般的な目安: 男性 2,500〜3,000kcal / 女性 2,000〜2,500kcal

### 現状維持
- 一般的な目安: 男性 2,000〜2,400kcal / 女性 1,600〜2,000kcal

## 対話のポイント
- 最初に`get_goal_setting_history`で前回の会話を確認する
- goalもhabitsも勝手に決めず、必ずユーザーに確認する
- やり取りの最後に`add_goal_setting_history`で会話を保存する
- 選択肢を提示して選んでもらう形にする
- 無理のない現実的な提案をする
- ユーザーの意見を尊重する

## 返答に含めるべき情報
- **進行状況を明示する**: 例えば「食事について決まりました。次は運動について相談しましょう！」
- **次のステップを示す**: まだ決まっていないhabitsがある場合は、次に何を決めるか明確に伝える
- **全て決まった時のみ保存**: 3つ全て（運動・食事・睡眠）が決まったら、`set_user_health_goal`で保存して完了を伝える
""",
    tools=[
        get_user_health_goal,
        get_goal_setting_history,
        add_goal_setting_history,
        set_user_health_goal,
    ],
)
