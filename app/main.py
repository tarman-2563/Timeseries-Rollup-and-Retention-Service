from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import engine, get_db, Base
from app.models import raw_metrics
from app.routes.ingest import ingestRouter
from app.routes.query import queryRouter
from app.schema_fix import fix_schema
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

app=FastAPI()

app.include_router(ingestRouter)
app.include_router(queryRouter)

@app.on_event("startup")
def on_startup():
    fix_schema()

@app.get("/")
def home():
    return {"message":"OK"}

@app.get("/health")
def health_check():
    return {"message":"Timeseries service is up and running"}

@app.get("/db/status")
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