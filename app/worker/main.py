"""aizap-worker: Pub/Sub Push 受信 → ADK 呼び出し → LINE 返信"""
# Deploy test: verify app-deploy.yml changes

import os

from fastapi import FastAPI, Request

app = FastAPI(title="aizap-worker")


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    """Pub/Sub Push 受信

    1. Pub/Sub メッセージをデコード
    2. ADK /run を呼び出し
    3. LINE reply/push で返信
    """
    # TODO: Pub/Sub メッセージをデコード
    # TODO: ADK /run を呼び出し
    # TODO: LINE reply/push で返信
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
