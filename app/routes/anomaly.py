from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.controllers.anomaly_controller import AnomalyController
from app.schemas.anomaly import AnomalyDetectionResponse
from datetime import datetime
from typing import Optional

anomalyRouter = APIRouter(prefix="/anomaly", tags=["anomaly"])

@anomalyRouter.get("/detect", response_model=AnomalyDetectionResponse, status_code=status.HTTP_200_OK)
async def detect_anomalies(
    metric_name: str = Query(..., description="Name of the metric to analyze"),
    start_time: datetime = Query(..., description="Start time for analysis"),
    end_time: datetime = Query(..., description="End time for analysis"),
    threshold: float = Query(3.0, ge=1.0, le=5.0, description="Z-score threshold (default: 3.0)"),
    labels: Optional[str] = Query(None, description="Labels as JSON string"),
    db: Session = Depends(get_db)
):
    return await AnomalyController.detect_anomalies(
        metric_name, start_time, end_time, threshold, labels, db
    )
