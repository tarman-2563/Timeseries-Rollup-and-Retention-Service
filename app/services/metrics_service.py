from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.models.raw_metrics import RawMetrics
from app.schemas.metrics import MetricListResponse, MetricListItem, MetricInfo
from typing import Optional, List, Set
import json

class MetricsService:
    def __init__(self, db: Session):
        self.db = db
    
    def list_metrics(self, page: int = 1, page_size: int = 10, search: Optional[str] = None) -> MetricListResponse:
        
        query = self.db.query(
            RawMetrics.metric_name,
            func.count(RawMetrics.id).label('sample_count'),
            func.min(RawMetrics.timestamp).label('first_seen'),
            func.max(RawMetrics.timestamp).label('last_seen')
        ).group_by(RawMetrics.metric_name)
        
        if search:
            query = query.filter(RawMetrics.metric_name.ilike(f"%{search}%"))
        
        total = query.count()
        
        offset = (page - 1) * page_size
        results = query.order_by(RawMetrics.metric_name).offset(offset).limit(page_size).all()
        
        metrics = [
            MetricListItem(
                metric_name=row.metric_name,
                sample_count=row.sample_count,
                first_seen=row.first_seen,
                last_seen=row.last_seen
            )
            for row in results
        ]
        
        return MetricListResponse(
            metrics=metrics,
            total=total,
            page=page,
            page_size=page_size
        )
    
    def get_metric_info(self, metric_name: str) -> Optional[MetricInfo]:
       
        metric_exists = self.db.query(RawMetrics).filter(
            RawMetrics.metric_name == metric_name
        ).first()
        
        if not metric_exists:
            return None
        
        stats = self.db.query(
            func.count(RawMetrics.id).label('sample_count'),
            func.min(RawMetrics.timestamp).label('first_seen'),
            func.max(RawMetrics.timestamp).label('last_seen'),
            func.min(RawMetrics.value).label('min_value'),
            func.max(RawMetrics.value).label('max_value'),
            func.avg(RawMetrics.value).label('avg_value')
        ).filter(
            RawMetrics.metric_name == metric_name
        ).first()
        
        label_keys_set: Set[str] = set()
        labels_data = self.db.query(RawMetrics.labels).filter(
            RawMetrics.metric_name == metric_name,
            RawMetrics.labels.isnot(None)
        ).all()
        
        for row in labels_data:
            if row.labels:
                label_keys_set.update(row.labels.keys())
        
        unique_combinations = self.db.query(
            func.count(distinct(RawMetrics.labels))
        ).filter(
            RawMetrics.metric_name == metric_name
        ).scalar()
        
        return MetricInfo(
            metric_name=metric_name,
            sample_count=stats.sample_count or 0,
            first_seen=stats.first_seen,
            last_seen=stats.last_seen,
            label_keys=sorted(list(label_keys_set)),
            unique_label_combinations=unique_combinations or 0,
            min_value=float(stats.min_value) if stats.min_value is not None else None,
            max_value=float(stats.max_value) if stats.max_value is not None else None,
            avg_value=float(stats.avg_value) if stats.avg_value is not None else None
        )
