from fastapi import APIRouter, status, Query, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.controllers.query_controller import QueryController
from app.schemas.query import RawQueryResponse, RollupQueryResponse
from datetime import datetime
from typing import Optional
from app.models.raw_metrics import RawMetrics
from sqlalchemy import distinct

queryRouter = APIRouter(tags=["query"])

@queryRouter.get("/metrics/names", status_code=status.HTTP_200_OK)
async def get_metric_names(db: Session = Depends(get_db)):
    try:
        total_records = db.query(RawMetrics).count()
        metric_names = db.query(distinct(RawMetrics.metric_name)).all()
        metrics_list = [name[0] for name in metric_names if name[0]]
        
        return {
            "metrics": metrics_list,
            "total": len(metrics_list),
            "total_records": total_records
        }
    except Exception as e:
        import traceback
        return {
            "metrics": [], 
            "total": 0, 
            "total_records": 0,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@queryRouter.get("/debug/data-info", status_code=status.HTTP_200_OK)
async def get_data_info(db: Session = Depends(get_db)):
    """Debug endpoint to see what data actually exists"""
    try:
        from sqlalchemy import func
        
        # Get total count
        total_count = db.query(RawMetrics).count()
        
        # Get date range of actual data
        date_range = db.query(
            func.min(RawMetrics.timestamp).label('earliest'),
            func.max(RawMetrics.timestamp).label('latest')
        ).first()
        
        # Get sample data
        sample_data = db.query(RawMetrics).limit(5).all()
        
        return {
            "total_records": total_count,
            "date_range": {
                "earliest": date_range.earliest.isoformat() if date_range.earliest else None,
                "latest": date_range.latest.isoformat() if date_range.latest else None
            },
            "sample_data": [
                {
                    "metric_name": r.metric_name,
                    "timestamp": r.timestamp.isoformat(),
                    "value": r.value
                }
                for r in sample_data
            ]
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@queryRouter.get("/query/raw", response_model=RawQueryResponse, status_code=status.HTTP_200_OK)
async def query_raw_metrics(
    metric_name: str = Query(..., description="Name of the metric to query"),
    start_time: datetime = Query(..., description="Start time for the query range"),
    end_time: datetime = Query(..., description="End time for the query range"),
    labels: Optional[str] = Query(None, description="Labels as JSON string"),
    fill_gaps: bool = Query(False, description="Fill missing data points with nulls"),
    interval_seconds: int = Query(60, description="Interval in seconds for gap filling"),
    db: Session = Depends(get_db)
):
    return await QueryController.query_raw_metrics(
        metric_name, start_time, end_time, labels, fill_gaps, interval_seconds, db
    )


@queryRouter.get("/query/rollup", response_model=RollupQueryResponse, status_code=status.HTTP_200_OK)
async def query_rollup_metrics(
    metric_name: str = Query(..., description="Name of the metric to query"),
    start_time: datetime = Query(..., description="Start time for the query range"),
    end_time: datetime = Query(..., description="End time for the query range"),
    window: str = Query(..., description="Rollup window size: 1m, 5m, or 1h"),
    labels: Optional[str] = Query(None, description="Labels as JSON string"),
    db: Session = Depends(get_db)
):
    return await QueryController.query_rollup_metrics(
        metric_name, start_time, end_time, window, labels, db
    )
