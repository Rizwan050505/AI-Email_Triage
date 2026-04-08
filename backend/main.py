from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import routes
from backend.database.database import engine
from backend.models import db_models
from env.email_env import EmailTriageEnv, Action
from pydantic import BaseModel

env_simulator = EmailTriageEnv()

class ResetReq(BaseModel):
    task_id: str = "email-triage-easy"

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Email Triage System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app.include_router(routes.router, prefix="/api")

# Mount the static frontend directory for relative asset access if needed
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def serve_frontend():
    # Serve the beautiful email triage UI directly on the Hackathon page!
    return FileResponse(os.path.join("frontend", "index.html"))

@app.post("/reset")
def reset_env(req: ResetReq):
    obs = env_simulator.reset(task_id=req.task_id)
    return obs

@app.get("/state")
def get_state():
    return env_simulator.state()

@app.post("/state")
def post_state():
    return env_simulator.state()

@app.post("/step")
def step_env(action: Action):
    obs, reward, done, info = env_simulator.step(action)
    return {
        "observation": obs,
        "reward": reward.step_reward,
        "done": done,
        "info": info
    }

@app.post("/close")
def close_env():
    env_simulator.close()
    return {"status": "ok"}

