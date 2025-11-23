from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import engine, get_db, Base
from app.models import raw_metrics

# Create database tables
Base.metadata.create_all(bind=engine)

app=FastAPI()

@app.get("/")
def home():
    return {"message":"OK"}

@app.get("/health")
def health_check():
    return {"message":"Timeseries service is up and running"}

@app.get("/db/status")
def db_status(db: Session = Depends(get_db)):
    """Check database connection status"""
    try:
        # Test connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "message": "Database connection is successfull"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection error: {str(e)}"
        }