from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.rollup_metrics import RollupMetrics
from app.schemas.rollup import RollupListResponse, RollupInfo
from typing import Optional

class RollupInfoService:
    def __init__(self, db: Session):
        self.db = db
    
    def list_rollups(self, metric_name: Optional[str] = None) -> RollupListResponse:
        
        query = self.db.query(
            RollupMetrics.metric_name,
            RollupMetrics.window,
            func.count(RollupMetrics.id).label('total_rollups'),
            func.min(RollupMetrics.start_time).label('earliest_time'),
            func.max(RollupMetrics.end_time).label('latest_time')
        )
        
        if metric_name:
            query = query.filter(RollupMetrics.metric_name == metric_name)
        
        results = query.group_by(
            RollupMetrics.metric_name,
            RollupMetrics.window
        ).order_by(
            RollupMetrics.metric_name,
            RollupMetrics.window
        ).all()
        
        rollups = [
            RollupInfo(
                metric_name=row.metric_name,
                window=row.window,
                total_rollups=row.total_rollups,
                earliest_time=row.earliest_time,
                latest_time=row.latest_time
            )
            for row in results
        ]
        
        return RollupListResponse(
            rollups=rollups,
            total=len(rollups)
        )
