from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import routes
from backend.database.database import engine
from backend.models import db_models

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
