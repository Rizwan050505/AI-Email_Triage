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

app.include_router(routes.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to AI Email Triage API"}
