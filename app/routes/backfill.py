from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.controllers.backfill_controller import BackfillController
from app.schemas.backfill import BackfillRequest, BackfillResponse

backfillRouter = APIRouter(prefix="/backfill", tags=["backfill"])

@backfillRouter.post("/import", response_model=BackfillResponse, status_code=status.HTTP_200_OK)
async def import_historical_data(request: BackfillRequest, db: Session = Depends(get_db)):
    return await BackfillController.import_historical_data(request, db)
