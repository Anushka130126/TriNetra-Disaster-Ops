import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv

from app.env import DisasterEnv
from app.models import Action

# Load environment variables securely
load_dotenv()

app = FastAPI(title="Disaster Ops Enterprise API", version="3.0.0")

# Security: Allow frontend to communicate with backend across different domains
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:7860"),
    "http://127.0.0.1:7860",
    "*" # Note: In strict production, remove "*" and use exact domains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = DisasterEnv()

# --- WEBSOCKET MANAGER (Real-Time Engine) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send initial state upon connection
        await websocket.send_json(env.state())

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# --- ROUTES ---
if os.path.exists("frontend"):
    app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse("frontend/index.html")

@app.get("/script.js")
def get_script():
    return FileResponse("frontend/script.js", media_type="application/javascript")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for manual overrides from the UI
            data = await websocket.receive_json()
            if data.get("type") == "manual_override":
                action = Action(**data.get("action"))
                obs, reward, done, info = env.step(action)
                await manager.broadcast(env.state())
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/reset")
async def reset(scenario_id: str = "triage_basic"):
    state_obj = env.reset(task_id=scenario_id)
    await manager.broadcast({
        "type": "RESET",
        "data": env.state()
    })

    return getattr(state_obj, "model_dump", state_obj.dict)()

@app.post("/step")
async def step(action: Action):
    """The AI agent calls this endpoint via HTTP POST"""
    obs, reward, done, info = env.step(action)

    # Instantly push the new state to the frontend UI
    await manager.broadcast(env.state())

    return {
        "observation": getattr(obs, "model_dump", obs.dict)(),
        "reward": round(reward, 3),
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    return env.state()

def main():
    import uvicorn
    # Note: Since we moved this to the server folder, we tell uvicorn to look at server.app
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=True)

if __name__ == "__main__":
    main()