from sqlalchemy.orm import Session
from app.schemas.query import QuerySchema, QueryResponseSchema,DataPointSchema,QueryFunction
from app.utils.label_utils import normalize_labels
from datetime import timedelta
from datetime import datetime
from typing import List, Dict
from app.models.raw_metrics import RawMetrics
from app.models.rollup_metrics import RollupMetrics

class QueryService:
    def __init__(self,db:Session):
        self.db=db
    
    async def query_metrics(self,query:QuerySchema)->QueryResponseSchema:
        normalized_labels=normalize_labels(query.labels) if query.labels else {}
        source=await self.select_optimal_source(query.start_time,query.end_time)
        if source=="raw":
            data_points=await self._query_raw_data(
                query.metric_name,
                query.start_time,
                query.end_time,
                normalized_labels
            )
        else:
            data_points=await self._query_rollup_data(
                query.metric_name,
                query.start_time,
                query.end_time,
                normalized_labels,
                source
            )

        aggregated_points=await self.apply_aggregation_function(
            data_points,
            query.function
        )

        return QueryResponseSchema(
            metric_name=query.metric_name,
            function=query.function.value,
            points=aggregated_points
        )
    
    async def select_optimal_source(self,start_time,end_time)->str:
        time_range=end_time - start_time
        if time_range<timedelta(hours=1):
            return "raw"
        elif time_range<timedelta(days=1):
            return "1m"
        elif time_range<timedelta(days=7):
            return "5m"
        else:
            return "1h"
        
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
                "count":r.count
            }
            for r in results
        ]
    
    def _filter_by_labels(self,query,labels:Dict[str,str],model):
        for key,value in labels.items():
            query = query.filter(model.labels.op("->>")(key) == value)
        return query
    
    async def apply_aggregation_function(
            self,
            data_points:List[Dict],
            function:QueryFunction
    )->List[DataPointSchema]:
        if not data_points:
            return []
        is_rollup="min" in data_points[0] if data_points else False

        if function==QueryFunction.RAW:
            return [
                DataPointSchema(timestamp=dp["timestamp"],value=dp.get("value",dp.get("avg")))
                for dp in data_points
            ]
        elif function==QueryFunction.SUM:
            if is_rollup:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=dp["sum"])
                    for dp in data_points
                ]
            else:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=dp["value"])
                    for dp in data_points
                ]
        elif function==QueryFunction.AVG:
            if is_rollup:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=dp["avg"])
                    for dp in data_points
                ]
            else:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=dp["value"])
                    for dp in data_points
                ]
        elif function==QueryFunction.MAX:
            if is_rollup:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=dp["max"])
                    for dp in data_points
                ]
            else:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=dp["value"])
                    for dp in data_points
                ]
        elif function==QueryFunction.MIN:
            if is_rollup:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=dp["min"])
                    for dp in data_points
                ]
            else:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=dp["value"])
                    for dp in data_points
                ]
        elif function==QueryFunction.COUNT:
            if is_rollup:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=dp["count"])
                    for dp in data_points
                ]
            else:
                return [
                    DataPointSchema(timestamp=dp["timestamp"],value=1)
                    for dp in data_points
                ]
        elif function==QueryFunction.RATE:
            results=[]
            for i in range(1,len(data_points)):
                prev=data_points[i-1]
                curr=data_points[i]
                prev_value=prev.get("value",prev.get("avg",0))
                curr_value=curr.get("value",curr.get("avg",0))
                time_diff=(curr["timestamp"]-prev["timestamp"]).total_seconds()
                if time_diff>0:
                    rate=(curr_value-prev_value)/time_diff
                    results.append(
                        DataPointSchema(timestamp=curr["timestamp"],value=rate)
                    )
            return results
        return []
    
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
                {"timestamp": dp["timestamp"], "value": dp["value"]}
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
                {
                    "timestamp": dp["timestamp"],
                    "min": dp["min"],
                    "max": dp["max"],
                    "avg": dp["avg"],
                    "sum": dp.get("sum", dp["avg"] * dp["count"]),
                    "count": dp["count"]
                }
                for dp in data_points
            ],
            "total_points": len(data_points)
        }
