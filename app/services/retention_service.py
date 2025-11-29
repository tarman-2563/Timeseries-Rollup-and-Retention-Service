from datetime import datetime,timedelta
from typing import Dict
from sqlalchemy.orm import Session
from app.models.raw_metrics import RawMetrics
from app.models.rollup_metrics import RollupMetrics


class RetentionService:
    def __init__(self,db:Session):
        self.db=db

    async def apply_retention_policies(self)->Dict[str,int]:
        results={}

        raw_cutoff=datetime.now()-timedelta(days=3)
        results["raw"]=await self.delete_old_raw_metrics(raw_cutoff)

        rollup_1m_cutoff=datetime.now()-timedelta(days=7)
        results["1m"]=await self.delete_old_rollup_metrics("1m",rollup_1m_cutoff)

        rollup_5m_cutoff=datetime.now()-timedelta(days=30)
        results["5m"]=await self.delete_old_rollup_metrics("5m",rollup_5m_cutoff)

        rollup_1h_cutoff=datetime.now()-timedelta(days=90)
        results["1h"]=await self.delete_old_rollup_metrics("1h",rollup_1h_cutoff)

        return results
    
    async def delete_old_raw_metrics(self,cutoff:datetime)->int:
        try:
            deleted_count=self.db.query(RawMetrics).filter(RawMetrics.timestamp < cutoff).delete(synchronize_session=False)
            self.db.commit()
            return deleted_count
        
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting old raw metrics: {e}")
    
    async def delete_old_rollup_metrics(self,window:str,cutoff:datetime)->int:
        try:
            deleted_count=self.db.query(RollupMetrics).filter(
                RollupMetrics.window==window,
                RollupMetrics.timestamp < cutoff
            ).delete(synchronize_session=False)
            self.db.commit()
            return deleted_count
        
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting old rollup metrics for window {window}: {e}")