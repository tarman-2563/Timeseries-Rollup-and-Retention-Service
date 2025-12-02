from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.metrics_service import MetricsService
from app.schemas.metrics import MetricListResponse, MetricInfo
from typing import Optional

metricsRouter = APIRouter(prefix="/metrics", tags=["metrics"])

@metricsRouter.get("/list", response_model=MetricListResponse, status_code=status.HTTP_200_OK)
async def list_metrics(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search metrics by name"),
    db: Session = Depends(get_db)
):
    try:
        metrics_service = MetricsService(db)
        return metrics_service.list_metrics(page=page, page_size=page_size, search=search)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing metrics: {str(e)}"
        )

@metricsRouter.get("/{metric_name}/info", response_model=MetricInfo, status_code=status.HTTP_200_OK)
async def get_metric_info(
    metric_name: str,
    db: Session = Depends(get_db)
):
    try:
        metrics_service = MetricsService(db)
        metric_info = metrics_service.get_metric_info(metric_name)
        
        if not metric_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metric '{metric_name}' not found"
            )
        
        return metric_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metric info: {str(e)}"
        )
