from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.controllers.ingest_controller import IngestController
from app.schemas.ingest import IngestRequest, IngestResponse

ingestRouter = APIRouter(prefix="/metrics", tags=["ingestion"])


@ingestRouter.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_200_OK)
async def ingest_metric(metric: IngestRequest, db: Session = Depends(get_db)):
    return await IngestController.ingest_metric(metric, db)
