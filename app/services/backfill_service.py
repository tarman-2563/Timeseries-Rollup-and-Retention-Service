from sqlalchemy.orm import Session
from app.models.raw_metrics import RawMetrics
from app.schemas.backfill import BackfillRequest, BackfillResponse
from typing import List

class BackfillService:
    def __init__(self, db: Session):
        self.db = db
    
    def import_metrics(self, request: BackfillRequest) -> BackfillResponse:
        imported = 0
        failed = 0
        
        try:
            metric_records = []
            for metric in request.metrics:
                try:
                    metric_record = RawMetrics(
                        metric_name=metric.metric_name,
                        value=metric.value,
                        timestamp=metric.timestamp,
                        labels=metric.labels or {}
                    )
                    metric_records.append(metric_record)
                except Exception:
                    failed += 1
            
            if metric_records:
                self.db.bulk_save_objects(metric_records)
                self.db.commit()
                imported = len(metric_records)
            
            return BackfillResponse(
                status="success" if failed == 0 else "partial",
                message=f"Imported {imported} metrics" + (f", {failed} failed" if failed > 0 else ""),
                metrics_imported=imported,
                failed=failed
            )
        
        except Exception as e:
            self.db.rollback()
            return BackfillResponse(
                status="error",
                message=f"Backfill failed: {str(e)}",
                metrics_imported=imported,
                failed=len(request.metrics) - imported
            )
