from sqlalchemy import Column,Integer,String,Float,BigInteger,DateTime,JSON,Index
from sqlalchemy.sql import func
from app.db import Base

class RawMetrics(Base):
    __tablename__="raw_metrics"
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    metric_name=Column(String,nullable=False,index=True)
    value=Column(Float,nullable=False)
    timestamp=Column(DateTime,nullable=False,index=True)
    labels=Column(JSON,nullable=True,default={})
    tenant_id=Column(String,nullable=True,index=True)
    created_at=Column(DateTime,nullable=False,default=func.now())
    table_args=(
        Index("index_metric_timestamp","metric_name","timestamp")
    )

def represent_raw_metric(self):
    return f"<RawMetric(id={self.id},metric_name='{self.metric_name}',value={self.value},timestamp={self.timestamp})>"    


    