from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum

class QueryFunction(str,Enum):
    SUM="sum"
    AVG="avg"
    MIN="min"
    MAX="max"
    COUNT="count"
    RATE="rate"
    RAW="raw"

class QuerySchema(BaseModel):
    metric_name:str=Field(...,description="Name of the metric to query")
    start_time:datetime=Field(...,description="Start time for the query range")
    end_time:datetime=Field(...,description="End time for the query range")
    labels:Optional[Dict[str,str]]=Field(default_factory=dict,description="Optional labels to filter the metrics")
    function:QueryFunction=Field(QueryFunction.AVG,description="Aggregation function to apply")

    class Config:
        schema_extra={
            "example":{
                "metric_name":"cpu_usage",
                "start_time":"2024-01-01T00:00:00Z",
                "end_time":"2024-01-02T00:00:00Z",
                "labels":{
                    "host":"server1",
                    "region":"us-west"
                },
                "function":"avg"
            }
        }

class QueryResponseSchema(BaseModel):
    metric_name:str=Field(...,description="Name of the queried metric")
    function:str=Field(...,description="Aggregation function applied")
    timestamp:datetime=Field(...,description="Timestamp of the aggregated data point")
    value:float=Field(...,description="Aggregated value")

    class Config:
        schema_extra={
            "example":{
                "metric_name":"cpu_usage",
                "function":"avg",
                "timestamp":"2024-01-01T12:00:00Z",
                "value":57.3
            }
        }

