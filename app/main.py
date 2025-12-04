from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db import engine, get_db, Base
from app.routes.ingest import ingestRouter
from app.routes.query import queryRouter
from app.routes.metrics import metricsRouter
from app.routes.rollup import rollupRouter
from app.routes.anomaly import anomalyRouter
from app.routes.backfill import backfillRouter
from app.schema_fix import fix_schema
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(ingestRouter)
app.include_router(queryRouter)
app.include_router(metricsRouter)
app.include_router(rollupRouter)
app.include_router(anomalyRouter)
app.include_router(backfillRouter)

@app.on_event("startup")
def on_startup():
    fix_schema()

@app.get("/", tags=["dashboard"])
def home():
    return FileResponse("static/dashboard.html")

@app.get("/dashboard", tags=["dashboard"])
def dashboard():
    return FileResponse("static/dashboard.html")

@app.get("/health", tags=["health"])
def health_check():
    return {"message":"Timeseries service is up and running"}

@app.get("/db/status", tags=["health"])
def db_status(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "message": "Database connection is successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection error: {str(e)}"
        }