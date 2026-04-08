from __future__ import annotations
import json, os, sys, uuid
from typing import Dict
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import CryptoAction, CryptoObservation, CryptoState, StepResult
from server.environment import CryptoTradingEnvironment

app = FastAPI(
    title="Crypto Trader OpenEnv",
    description="A real-world RL environment for LLM-based crypto trading agents.",
    version="1.0.0",
)

_sessions: Dict[str, CryptoTradingEnvironment] = {}

def _get_or_create(session_id: str) -> CryptoTradingEnvironment:
    if session_id not in _sessions:
        _sessions[session_id] = CryptoTradingEnvironment()
    return _sessions[session_id]

@app.get("/")
async def index():
    return HTMLResponse("""
    <html><body style="font-family:monospace;padding:2em;background:#111;color:#0f0">
    <h2>💰 Crypto Trader OpenEnv</h2>
    <p>Environment: <b>crypto-trader-v1</b></p>
    <p>Endpoints: POST /reset &nbsp;|&nbsp; POST /step &nbsp;|&nbsp; GET /state &nbsp;|&nbsp; WS /ws</p>
    <p><a href="/docs" style="color:#0af">API Docs →</a></p>
    </body></html>
    """)

@app.post("/reset", response_model=CryptoObservation)
async def reset(session_id: str = "default"):
    env = _get_or_create(session_id)
    return env.reset()

@app.post("/step", response_model=StepResult)
async def step(action: CryptoAction, session_id: str = "default"):
    env = _get_or_create(session_id)
    try:
        return env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state", response_model=CryptoState)
async def get_state(session_id: str = "default"):
    env = _get_or_create(session_id)
    return env.state

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    env = CryptoTradingEnvironment()
    _sessions[session_id] = env
    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            cmd = msg.get("command")
            if cmd == "reset":
                await websocket.send_text(env.reset().model_dump_json())
            elif cmd == "step":
                action = CryptoAction(**msg.get("action", {}))
                await websocket.send_text(env.step(action).model_dump_json())
            elif cmd == "state":
                await websocket.send_text(env.state.model_dump_json())
            else:
                await websocket.send_text(json.dumps({"error": f"Unknown command: {cmd}"}))
    except WebSocketDisconnect:
        _sessions.pop(session_id, None)

if __name__ == "__main__":
    workers = int(os.getenv("WORKERS", "1"))
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, workers=workers)