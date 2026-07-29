from fastapi import FastAPI
from app.api import upload, classify, pnl, qbo, reconcile, ui

app = FastAPI(
    title="Finz Data Engineering Challenge",
    version="1.0.0"
)

app.include_router(upload.router)
app.include_router(classify.router)
app.include_router(pnl.router)
app.include_router(qbo.router)
app.include_router(reconcile.router)
app.include_router(ui.router)

@app.get("/")
def home():
    return {"message": "Finz Backend API Operational. Access Dashboard at /ui"}