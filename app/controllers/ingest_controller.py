from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.raw_metrics import RawMetrics
from app.schemas.ingest import IngestRequest, IngestResponse
from app.utils.label_utils import check_cardinality as check_cardinality_limit


class CardinalityExceededException(Exception):
    pass


class IngestController:

    @staticmethod
    async def ingest_metric(metric: IngestRequest, db: Session) -> IngestResponse:
        try:
            IngestController._check_cardinality(db, metric.metric_name, metric.labels)
            
            metric_record = RawMetrics(
                metric_name=metric.metric_name,
                value=metric.value,
                timestamp=metric.timestamp,
                labels=metric.labels
            )
            
            db.add(metric_record)
            db.commit()
            db.refresh(metric_record)
            
            return IngestResponse(
                status="success",
                message="Metric ingested successfully",
                metric_id=metric_record.id
            )
            
        except CardinalityExceededException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error ingesting metric: {str(e)}"
            )
    
    @staticmethod
    def _check_cardinality(db: Session, metric_name: str, labels: dict, limit: int = 100) -> None:
        if not check_cardinality_limit(db, metric_name, labels, limit):
            raise CardinalityExceededException(
                f"Cardinality limit of {limit} exceeded for metric '{metric_name}'"
            )
