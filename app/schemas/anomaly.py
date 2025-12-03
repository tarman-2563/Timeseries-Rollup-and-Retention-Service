from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AnomalyDataPoint(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp of the data point")
    value: float = Field(..., description="Actual value")
    z_score: float = Field(..., description="Z-score (standard deviations from mean)")
    is_anomaly: bool = Field(..., description="Whether this point is an anomaly")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-12-03T12:00:00Z",
                "value": 95.5,
                "z_score": 3.2,
                "is_anomaly": True
            }
        }

class AnomalyDetectionResponse(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    total_points: int = Field(..., description="Total data points analyzed")
    anomalies_found: int = Field(..., description="Number of anomalies detected")
    mean: float = Field(..., description="Mean value of the dataset")
    std_dev: float = Field(..., description="Standard deviation")
    threshold: float = Field(..., description="Z-score threshold used")
    points: List[AnomalyDataPoint] = Field(..., description="Data points with anomaly flags")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "cpu_usage",
                "total_points": 100,
                "anomalies_found": 3,
                "mean": 65.5,
                "std_dev": 10.2,
                "threshold": 3.0,
                "points": [
                    {
                        "timestamp": "2025-12-03T12:00:00Z",
                        "value": 95.5,
                        "z_score": 3.2,
                        "is_anomaly": True
                    }
                ]
            }
        }
