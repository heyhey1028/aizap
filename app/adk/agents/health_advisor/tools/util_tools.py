"""汎用ユーティリティツール

特定のテーブルに紐づかない、エージェント制御や共通処理用のツール。
全てのサブエージェントから利用可能。
"""

from google.adk.tools import ToolContext

def finish_task(summary: str, tool_context: ToolContext) -> dict:
    """タスク完了時に呼び出します。制御をルートエージェントに戻します。

    このツールを呼ぶと、対話権がルートエージェントに戻ります。
    呼び出し後は追加のメッセージを生成せず、処理を終了してください。

    Args:
        summary: 完了したタスクの要約（例: 記録した運動内容の要約）。ルートエージェントに渡されます。
        tool_context: ADKが提供するToolContext。
    """
    tool_context.actions.transfer_to_agent = "root_agent"
    return {
        "status": "success",
        "data": summary,
        "next_agent": "root_agent",
        "terminate_sub_segment": True,
    }
