from sqlalchemy.orm import Session
from app.schemas.query import DataPointSchema
from app.utils.label_utils import normalize_labels
from datetime import timedelta
from datetime import datetime
from typing import List, Dict
from app.models.raw_metrics import RawMetrics
from app.models.rollup_metrics import RollupMetrics
from app.schemas.query import RollupDataPoint

class QueryService:
    def __init__(self,db:Session):
        self.db=db
        
    async def _query_raw_data(
            self,
            metric_name:str,
            start_time:datetime,
            end_time:datetime,
            labels:Dict[str,str]
    )->List[Dict]:
        query=self.db.query(RawMetrics).filter(
            RawMetrics.metric_name==metric_name,
            RawMetrics.timestamp >= start_time,
            RawMetrics.timestamp <= end_time
        )
        if labels:
            query=self._filter_by_labels(query,labels,RawMetrics)
        results=query.order_by(RawMetrics.timestamp).all()

        return [{"timestamp":r.timestamp,"value":r.value} for r in results]
    
    async def _query_rollup_data(
            self,
            metric_name:str,
            start_time:datetime,
            end_time:datetime,
            labels:Dict[str,str],
            window:str
    )->List[Dict]:
        query=self.db.query(RollupMetrics).filter(
            RollupMetrics.metric_name==metric_name,
            RollupMetrics.start_time >= start_time,
            RollupMetrics.end_time <= end_time,
            RollupMetrics.window==window
        )
        if labels:
            query=self._filter_by_labels(query,labels,RollupMetrics)
        
        results=query.order_by(RollupMetrics.start_time).all()

        return [
            {
                "timestamp":r.start_time,
                "min":r.min,
                "max":r.max,
                "avg":r.avg,
                "sum":r.sum,
                "count":r.count
            }
            for r in results
        ]
    
    def _filter_by_labels(self,query,labels:Dict[str,str],model):
        for key,value in labels.items():
            query = query.filter(model.labels.op("->>")(key) == value)
        return query
    
    async def query_raw_data(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        labels: Dict[str, str] = None
    ) -> Dict:
        normalized_labels = normalize_labels(labels) if labels else {}
        
        data_points = await self._query_raw_data(
            metric_name,
            start_time,
            end_time,
            normalized_labels
        )
        
        return {
            "metric_name": metric_name,
            "points": [
                DataPointSchema(timestamp=dp["timestamp"], value=dp["value"])
                for dp in data_points
            ],
            "total_points": len(data_points)
        }
    
    async def query_rollup_data(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        window: str,
        labels: Dict[str, str] = None
    ) -> Dict:
        valid_windows = ["1m", "5m", "1h"]
        if window not in valid_windows:
            raise ValueError(f"Invalid window '{window}'. Must be one of: {valid_windows}")
        
        normalized_labels = normalize_labels(labels) if labels else {}
        
        data_points = await self._query_rollup_data(
            metric_name,
            start_time,
            end_time,
            normalized_labels,
            window
        )
        
        return {
            "metric_name": metric_name,
            "window": window,
            "points": [
                RollupDataPoint(
                    timestamp=dp["timestamp"],
                    min=dp["min"],
                    max=dp["max"],
                    avg=dp["avg"],
                    sum=dp["sum"],
                    count=dp["count"]
                )
                for dp in data_points
            ],
            "total_points": len(data_points)
        }

    def fill_gaps(
        self,
        data_points: List[DataPointSchema],
        start_time: datetime,
        end_time: datetime,
        interval_seconds: int = 60
    ) -> List[DataPointSchema]:
        if not data_points:
            return []
        
        filled_points = []
        current_time = start_time
        data_index = 0
        
        while current_time <= end_time:
            if data_index < len(data_points):
                point = data_points[data_index]
                point_time = point.timestamp
                
                time_diff = abs((point_time - current_time).total_seconds())
                
                if time_diff < interval_seconds / 2:
                    filled_points.append(point)
                    data_index += 1
                else:
                    filled_points.append(DataPointSchema(
                        timestamp=current_time,
                        value=None
                    ))
            else:
                filled_points.append(DataPointSchema(
                    timestamp=current_time,
                    value=None
                ))
            
            current_time += timedelta(seconds=interval_seconds)
        
        return filled_points
