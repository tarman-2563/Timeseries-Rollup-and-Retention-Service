from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session
from app.db import get_db
from sqlalchemy import text

metricsRouter=APIRouter(prefix="/metrics",tags=["metrics"])

@metricsRouter.get("/test/connection")
def test_connection(db:Session=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return{
            "status":"connected",
            "message":"Database connection successful"
        }
    except Exception as e:
        return{
            "status":"error",
            "message":f"Database connection failed:{str(e)}"
        }