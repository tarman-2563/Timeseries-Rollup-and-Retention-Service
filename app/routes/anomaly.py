from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.anomaly_service import AnomalyService
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
    try:
        import json
        parsed_labels = json.loads(labels) if labels else {}
        
        anomaly_service = AnomalyService(db)
        result = anomaly_service.detect_anomalies(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            threshold=threshold,
            labels=parsed_labels
        )
        
        if result.total_points == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data found for the given query"
            )
        
        return result
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid labels format. Must be valid JSON string."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting anomalies: {str(e)}"
        )
