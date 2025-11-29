from sqlalchemy import Column,Integer,String,Float,DateTime,JSON,Index,UniqueConstraint
from sqlalchemy.sql import func
from app.db import Base

class RollupMetrics(Base):
    __tablename__="rollup_metrics"
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    metric_name=Column(String,nullable=False,index=True)
    window=Column(String,nullable=False,index=True)
    start_time=Column(DateTime,nullable=False,index=True)
    end_time=Column(DateTime,nullable=False,index=True)
    min=Column(Float,nullable=False)
    max=Column(Float,nullable=False)
    sum=Column(Float,nullable=False)
    avg=Column(Float,nullable=False)
    count=Column(Integer,nullable=False)
    labels=Column(JSON,nullable=True,default={})
    created_at=Column(DateTime,nullable=False,default=func.now())
    __table_args__=(
        UniqueConstraint("metric_name","window","start_time",name='uix_rollup_metric'),
        Index("index_rollup_metric_time","metric_name","start_time")
    )

def represent_rollup_metric(self):
    return f"<RollupMetric(id={self.id},metric_name='{self.metric_name}',window='{self.window}',start_time={self.start_time},end_time={self.end_time})>"