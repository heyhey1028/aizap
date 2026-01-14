"""aizap-bff: LINE Webhook 受信、LIFF API エンドポイント"""
# Deploy test: verify app-deploy.yml changes

import os

from fastapi import FastAPI, Request, Response

app = FastAPI(title="aizap-bff")


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    """LINE Webhook 受信

    1. LINE 署名検証
    2. Pub/Sub に Publish
    3. 即座に 200 返却（2秒以内）
    """
    # TODO: LINE 署名検証
    # TODO: Pub/Sub に Publish
    return Response(status_code=200)


@app.post("/api/run")
async def api_run(request: Request):
    """LIFF API: エージェント実行（同期）

    1. LINE Login 検証
    2. ADK /run に中継
    """
    # TODO: LINE Login 検証
    # TODO: ADK に中継
    return {"message": "not implemented"}


@app.get("/api/run_sse")
async def api_run_sse(request: Request):
    """LIFF API: エージェント実行（SSE ストリーミング）

    1. LINE Login 検証
    2. ADK /run_sse に SSE 中継
    """
    # TODO: LINE Login 検証
    # TODO: ADK に SSE 中継
    return {"message": "not implemented"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
