from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime

class BackfillMetric(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    value: float = Field(..., description="Value of the metric")
    timestamp: datetime = Field(..., description="Timestamp in ISO 8601 format")
    labels: Optional[Dict[str, str]] = Field(default_factory=dict, description="Optional labels")
    
    @field_validator("metric_name")
    @classmethod
    def validate_metric_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Metric name must be a non-empty string")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "cpu_usage",
                "value": 75.5,
                "timestamp": "2025-12-01T12:00:00Z",
                "labels": {"host": "server1"}
            }
        }

class BackfillRequest(BaseModel):
    metrics: List[BackfillMetric] = Field(..., description="List of metrics to backfill")
    
    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, v: List[BackfillMetric]) -> List[BackfillMetric]:
        if not v:
            raise ValueError("Metrics list cannot be empty")
        if len(v) > 10000:
            raise ValueError("Cannot backfill more than 10000 metrics at once")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "metrics": [
                    {
                        "metric_name": "cpu_usage",
                        "value": 75.5,
                        "timestamp": "2025-12-01T12:00:00Z",
                        "labels": {"host": "server1"}
                    },
                    {
                        "metric_name": "cpu_usage",
                        "value": 76.2,
                        "timestamp": "2025-12-01T12:01:00Z",
                        "labels": {"host": "server1"}
                    }
                ]
            }
        }

class BackfillResponse(BaseModel):
    status: str = Field(..., description="Status of the backfill operation")
    message: str = Field(..., description="Detailed message")
    metrics_imported: int = Field(..., description="Number of metrics successfully imported")
    failed: int = Field(0, description="Number of failed imports")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Backfill completed successfully",
                "metrics_imported": 100,
                "failed": 0
            }
        }
