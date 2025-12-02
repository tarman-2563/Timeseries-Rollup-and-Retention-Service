from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.rollup_info_service import RollupInfoService
from app.schemas.rollup import RollupListResponse
from typing import Optional

rollupRouter = APIRouter(prefix="/rollups", tags=["rollups"])

@rollupRouter.get("", response_model=RollupListResponse, status_code=status.HTTP_200_OK)
async def list_rollups(
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
    db: Session = Depends(get_db)
):
    try:
        rollup_service = RollupInfoService(db)
        return rollup_service.list_rollups(metric_name=metric_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing rollups: {str(e)}"
        )
