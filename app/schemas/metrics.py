from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class MetricListItem(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    sample_count: int = Field(..., description="Total number of data points")
    first_seen: Optional[datetime] = Field(None, description="Timestamp of first data point")
    last_seen: Optional[datetime] = Field(None, description="Timestamp of last data point")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "cpu_usage",
                "sample_count": 1500,
                "first_seen": "2024-01-01T00:00:00Z",
                "last_seen": "2024-01-02T00:00:00Z"
            }
        }

class MetricListResponse(BaseModel):
    metrics: List[MetricListItem] = Field(..., description="List of metrics")
    total: int = Field(..., description="Total number of metrics")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metrics": [
                    {
                        "metric_name": "cpu_usage",
                        "sample_count": 1500,
                        "first_seen": "2024-01-01T00:00:00Z",
                        "last_seen": "2024-01-02T00:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10
            }
        }

class MetricInfo(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    sample_count: int = Field(..., description="Total number of data points")
    first_seen: Optional[datetime] = Field(None, description="Timestamp of first data point")
    last_seen: Optional[datetime] = Field(None, description="Timestamp of last data point")
    label_keys: List[str] = Field(..., description="All unique label keys used")
    unique_label_combinations: int = Field(..., description="Number of unique label combinations (cardinality)")
    min_value: Optional[float] = Field(None, description="Minimum value recorded")
    max_value: Optional[float] = Field(None, description="Maximum value recorded")
    avg_value: Optional[float] = Field(None, description="Average value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "cpu_usage",
                "sample_count": 1500,
                "first_seen": "2024-01-01T00:00:00Z",
                "last_seen": "2024-01-02T00:00:00Z",
                "label_keys": ["host", "region"],
                "unique_label_combinations": 5,
                "min_value": 10.5,
                "max_value": 95.2,
                "avg_value": 65.3
            }
        }
