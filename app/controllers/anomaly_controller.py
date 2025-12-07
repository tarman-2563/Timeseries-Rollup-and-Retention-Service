from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.anomaly_service import AnomalyService
from app.schemas.anomaly import AnomalyDetectionResponse
from datetime import datetime
from typing import Optional, Dict
import json


class AnomalyController:
    
    @staticmethod
    async def detect_anomalies(
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        threshold: float,
        labels: Optional[str],
        db: Session
    ) -> AnomalyDetectionResponse:
        try:
            parsed_labels = AnomalyController._parse_labels(labels)
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
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error detecting anomalies: {str(e)}"
            )
    
    @staticmethod
    def _parse_labels(labels_json: Optional[str]) -> Dict[str, str]:
        if not labels_json:
            return {}
        
        try:
            return json.loads(labels_json)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid labels format. Must be valid JSON string."
            )
