from sqlalchemy.orm import Session
from app.models.raw_metrics import RawMetrics
from app.schemas.anomaly import AnomalyDetectionResponse, AnomalyDataPoint
from datetime import datetime
from typing import Dict, Optional
import statistics

class AnomalyService:
    def __init__(self, db: Session):
        self.db = db
    
    def detect_anomalies(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        threshold: float = 3.0,
        labels: Optional[Dict[str, str]] = None
    ) -> AnomalyDetectionResponse:
        query = self.db.query(RawMetrics).filter(
            RawMetrics.metric_name == metric_name,
            RawMetrics.timestamp >= start_time,
            RawMetrics.timestamp <= end_time
        )
        
        if labels:
            for key, value in labels.items():
                query = query.filter(RawMetrics.labels.op("->>")(key) == value)
        
        results = query.order_by(RawMetrics.timestamp).all()
        
        if len(results) < 2:
            return AnomalyDetectionResponse(
                metric_name=metric_name,
                total_points=len(results),
                anomalies_found=0,
                mean=0.0,
                std_dev=0.0,
                threshold=threshold,
                points=[]
            )
        
        values = [r.value for r in results]
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
        
        anomalies_found = 0
        points = []
        
        for result in results:
            if std_dev > 0:
                z_score = (result.value - mean) / std_dev
            else:
                z_score = 0.0
            
            is_anomaly = abs(z_score) > threshold
            if is_anomaly:
                anomalies_found += 1
            
            points.append(AnomalyDataPoint(
                timestamp=result.timestamp,
                value=result.value,
                z_score=round(z_score, 2),
                is_anomaly=is_anomaly
            ))
        
        return AnomalyDetectionResponse(
            metric_name=metric_name,
            total_points=len(results),
            anomalies_found=anomalies_found,
            mean=round(mean, 2),
            std_dev=round(std_dev, 2),
            threshold=threshold,
            points=points
        )
