from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DataPointSchema(BaseModel):
    timestamp:datetime=Field(...,description="Timestamp of the data point")
    value: Optional[float] = Field(..., description="Value (can be null for gap-filled points)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-01-01T10:10:00Z",
                "value": 78.2
            }
        }

class RawQueryResponse(BaseModel):
    metric_name:str=Field(...,description="Name of the queried metric")
    points:List[DataPointSchema]=Field(...,description="List of raw data points")
    total_points:int=Field(...,description="Total number of data points returned")
    
    class Config:
        json_schema_extra={
            "example":{
                "metric_name":"cpu_usage",
                "points":[
                    {"timestamp":"2024-01-01T12:00:00Z","value":75.5},
                    {"timestamp":"2024-01-01T12:01:00Z","value":76.2}
                ],
                "total_points":2
            }
        }

class RollupDataPoint(BaseModel):
    timestamp:datetime=Field(...,description="Start time of the rollup window")
    min:float=Field(...,description="Minimum value in the window")
    max:float=Field(...,description="Maximum value in the window")
    avg:float=Field(...,description="Average value in the window")
    sum:float=Field(...,description="Sum of values in the window")
    count:int=Field(...,description="Number of data points in the window")
    
    class Config:
        json_schema_extra={
            "example":{
                "timestamp":"2024-01-01T12:00:00Z",
                "min":70.0,
                "max":80.0,
                "avg":75.5,
                "sum":755.0,
                "count":10
            }
        }

class RollupQueryResponse(BaseModel):
    metric_name:str=Field(...,description="Name of the queried metric")
    window:str=Field(...,description="Rollup window size (1m, 5m, 1h)")
    points:List[RollupDataPoint]=Field(...,description="List of rollup data points")
    total_points:int=Field(...,description="Total number of rollup windows returned")
    
    class Config:
        json_schema_extra={
            "example":{
                "metric_name":"cpu_usage",
                "window":"5m",
                "points":[
                    {
                        "timestamp":"2024-01-01T12:00:00Z",
                        "min":70.0,
                        "max":80.0,
                        "avg":75.5,
                        "sum":755.0,
                        "count":10
                    }
                ],
                "total_points":1
            }
        }

