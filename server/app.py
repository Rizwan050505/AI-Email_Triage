import uvicorn
from backend.main import app

def start():
    uvicorn.run("backend.main:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    start()
