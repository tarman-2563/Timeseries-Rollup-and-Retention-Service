from sqlalchemy import Column,Integer,String,Float,BigInteger,DateTime
from sqlalchemy.sql import func
from app.db import Base

class RawMetrics(Base):
    __tablename__="raw_metrics"
    id=Column(Integer,primary_key=True,index=True)
    metric_name=Column(String,nullable=False)
    metric_value=Column(Float,nullable=False)
    timestamp=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    