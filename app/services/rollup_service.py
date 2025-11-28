from datetime import datetime
from typing import List
from app.models.raw_metrics import RawMetrics
from app.models.rollup_metrics import RollupMetrics
from sqlalchemy.orm import Session
from typing import Dict
from app.utils.label_utils import hash_labels
from app.utils.time_utils import generate_time_buckets,round_to_window,parse_window


class RollupService:
    windows=["1m","5m","1h"]

    def __init__(self,db:Session):
        self.db=db

    async def perform_rollups(self,since:datetime)->Dict[str,int]:
        stats={
            "raw_metrics_processed":0,
            "rollup_metrics_created":0,
            "windows_processed":self.windows
        }
        raw_metrics=self.db.query(RawMetrics).filter(RawMetrics.timestamp>=since).order_by(RawMetrics.timestamp).all()

        stats["raw_metrics_processed"]=len(raw_metrics)

        if not raw_metrics:
            return stats
        
        min_timestamp=min(rm.timestamp for rm in raw_metrics)
        max_timestamp=max(rm.timestamp for rm in raw_metrics)

        for window in self.windows:
            rollups=await self.compute_window_aggregation(raw_metrics,window,min_timestamp,max_timestamp)

            if rolllups:
                self.db.bulk_save_objects(rollups)
                self.db.commit()
                stats["rollup_metrics_created"]+=len(rollups)

        return stats
    
    async def compute_window_aggregation(
            self,
            raw_metrics:List[RawMetrics],
            window:str,
            min_timestamp:datetime,
            max_timestamp:datetime
    )->List[RollupMetrics]:
        buckets=generate_time_buckets(start_time,end_time,window)
        grouped_metrics={}

        for metric in raw_metrics:
            metric_bucket=round_to_window(metric.timestamp,window)
            labels_hash=hash_labels(metric.labels)
            key=(metric.metric_name,labels_hash,metric.labels)
            grouped_metrics[key].append(metric)

        rollups=[]
        window_delta=parse_window(window)

        for (metric_name,labels_hash,bucket_start,labels),group_metrics in grouped_metrics.items():
            values=[m.value for m in group_metrics]

            rollup=RollupMetrics(
                metric_name=metric_name,
                window=window,
                start_time=bucket_start,
                end_time=bucket_start+window_delta,
                min=min(values),
                max=max(values),
                sum=sum(values),
                avg=sum(values)/len(values),
                count=len(values),
                labels=labels
            )
            rollups.append(rollup)

        return rollups
        