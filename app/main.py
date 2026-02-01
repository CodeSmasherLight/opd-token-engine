from fastapi import FastAPI
from app.core import state



app = FastAPI(title="OPD Token Allocation Engine")

@app.get("/health")
def health_check():
    return {"status": "ok"}
