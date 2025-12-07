from fastapi import APIRouter, status, Query, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.controllers.query_controller import QueryController
from app.schemas.query import QueryResponseSchema, RawQueryResponse, RollupQueryResponse, QuerySchema
from datetime import datetime
from typing import Optional

queryRouter = APIRouter(tags=["query"])

@queryRouter.get("/metrics/names", status_code=status.HTTP_200_OK)
async def get_metric_names(db: Session = Depends(get_db)):
    """Get list of distinct metric names from raw_metrics table"""
    from app.models.raw_metrics import RawMetrics
    from sqlalchemy import distinct
    
    try:
        metric_names = db.query(distinct(RawMetrics.metric_name)).all()
        return {
            "metrics": [name[0] for name in metric_names if name[0]],
            "total": len(metric_names)
        }
    except Exception as e:
        return {"metrics": [], "total": 0, "error": str(e)}


@queryRouter.post("/query", response_model=QueryResponseSchema, status_code=status.HTTP_200_OK)
async def query_metrics(
    query: QuerySchema,
    fill_gaps: bool = Query(False, description="Fill missing data points with nulls"),
    interval_seconds: int = Query(60, description="Interval in seconds for gap filling"),
    db: Session = Depends(get_db)
):
    return await QueryController.query_metrics(query, fill_gaps, interval_seconds, db)


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
