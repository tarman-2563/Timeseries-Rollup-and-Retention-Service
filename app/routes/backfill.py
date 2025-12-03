from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.backfill_service import BackfillService
from app.schemas.backfill import BackfillRequest, BackfillResponse

backfillRouter = APIRouter(prefix="/backfill", tags=["backfill"])

@backfillRouter.post("/import", response_model=BackfillResponse, status_code=status.HTTP_200_OK)
async def import_historical_data(
    request: BackfillRequest,
    db: Session = Depends(get_db)
):
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
