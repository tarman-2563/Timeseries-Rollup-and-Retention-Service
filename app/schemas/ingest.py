from pydantic import BaseModel,Field,field_validator
from datetime import datetime
from typing import Optional,Dict

class IngestRequest(BaseModel):
    metric_name:str=Field(...,min_length=1,max_length=100,description="Name of the metric")
    value:float=Field(...,description="Value of the metric")
    timestamp:datetime=Field(...,description="Timestamp of the metric in ISO 8601 format")
    labels:Optional[Dict[str,str]]=Field(default_factory=dict,description="Optional labels for the metric")
    tenant_id:Optional[str]=Field(None,description="Optional tenant identifier")

    @field_validator("metric_name")
    @classmethod
    def validate_metric_name(cls,v:str)->str:
        if not v or not v.strip():
            raise ValueError("Metric name must be a non-empty string")
        return v.strip()

    @field_validator("value")
    @classmethod
    def validate_value(cls,v:float)->float:
        if not isinstance(v,(int,float)):
            raise ValueError("Value must be a numeric type")
        return v

    class Config:
        schema_extra={
            "example":{
                "metric_name":"cpu_usage",
                "value":75.5,
                "timestamp":"2024-06-01T12:00:00Z",
                "labels":{"host":"server1","region":"us-west"},
                "tenant_id":"tenant_123"
            }
        }

class IngestResponse(BaseModel):
    status:str=Field(...,description="Status of the ingestion operation")
    message:str=Field(...,description="Detailed message about the ingestion result")
    metric_id:Optional[int]=Field(None,description="ID of the ingested metric record")

    class Config:
        schema_extra={
            "example":{
                "status":"success",
                "message":"Metric ingested successfully",
                "metric_id":42
            }
        }
