from fastapi import APIRouter, status
from app.schemas.query import QueryResponseSchema
from app.schemas.query import QuerySchema
from app.services.query_service import QueryService
from fastapi import Depends, HTTPException
from app.db import get_db
from sqlalchemy.orm import Session

queryRouter=APIRouter()

@queryRouter.post("/query",response_model=QueryResponseSchema,status_code=status.HTTP_200_OK)

async def query_metrics(query:QuerySchema,db:Session=Depends(get_db)):
    try:
        query_service=QueryService(db)
        results=await query_service.execute_query(query)
        if not results:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No metrics found for the given query")
        return results
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    