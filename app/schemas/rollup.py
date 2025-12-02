from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class RollupInfo(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    window: str = Field(..., description="Rollup window size (1m, 5m, 1h)")
    total_rollups: int = Field(..., description="Total number of rollup records")
    earliest_time: datetime = Field(..., description="Earliest rollup timestamp")
    latest_time: datetime = Field(..., description="Latest rollup timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "cpu_usage",
                "window": "5m",
                "total_rollups": 288,
                "earliest_time": "2024-01-01T00:00:00Z",
                "latest_time": "2024-01-02T00:00:00Z"
            }
        }

class RollupListResponse(BaseModel):
    rollups: List[RollupInfo] = Field(..., description="List of available rollups")
    total: int = Field(..., description="Total number of rollup entries")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rollups": [
                    {
                        "metric_name": "cpu_usage",
                        "window": "1m",
                        "total_rollups": 1440,
                        "earliest_time": "2024-01-01T00:00:00Z",
                        "latest_time": "2024-01-02T00:00:00Z"
                    }
                ],
                "total": 1
            }
        }
