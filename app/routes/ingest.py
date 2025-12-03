from fastapi import APIRouter,Depends,HTTPException,status
from app.models.raw_metrics import RawMetrics
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.ingest import IngestRequest,IngestResponse
from app.utils.label_utils import check_cardinality as check_cardinality_limit

ingestRouter=APIRouter(prefix="/metrics", tags=["ingestion"])

class CardinalityExceededException(Exception):
    pass

def check_cardinality(
    db:Session,
    metric_name:str,
    labels:dict,
    limit:int=None
) -> None:
    if limit is None:
        limit=100
    if not check_cardinality_limit(db,metric_name,labels,limit):
        raise CardinalityExceededException(f"Cardinality limit of {limit} exceeded for metric '{metric_name}'")

@ingestRouter.post("/ingest",response_model=IngestResponse,status_code=200)

async def ingest_metric(metric:IngestRequest,db:Session=Depends(get_db)):
    try:
        check_cardinality(db,metric.metric_name,metric.labels,limit=100)
    except CardinalityExceededException as e:
        raise HTTPException(status_code=400,detail=str(e))
    
    try:
        metric_record=RawMetrics(
            metric_name=metric.metric_name,
            value=metric.value,
            timestamp=metric.timestamp,
            labels=metric.labels
        )
        db.add(metric_record)
        db.commit()
        db.refresh(metric_record)

        return IngestResponse(status="success",message="Metric ingested successfully",metric_id=metric_record.id)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Error ingesting metric: {str(e)}")

    


    