from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.backfill_service import BackfillService
from app.schemas.backfill import BackfillRequest, BackfillResponse


class BackfillController:    
    
    @staticmethod
    async def import_historical_data(
        request: BackfillRequest,
        db: Session
    ) -> BackfillResponse:
        try:
            backfill_service = BackfillService(db)
            result = backfill_service.import_metrics(request)
            
            if result.status == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.message
                )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error importing data: {str(e)}"
            )
