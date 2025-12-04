from fastapi import APIRouter, status, Query
from app.schemas.query import QueryResponseSchema, RawQueryResponse, RollupQueryResponse
from app.schemas.query import QuerySchema
from app.services.query_service import QueryService
from fastapi import Depends, HTTPException
from app.db import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict

queryRouter=APIRouter(tags=["query"])

@queryRouter.post("/query",response_model=QueryResponseSchema,status_code=status.HTTP_200_OK)
async def query_metrics(
    query:QuerySchema,
    fill_gaps: bool = Query(False, description="Fill missing data points with nulls"),
    interval_seconds: int = Query(60, description="Interval in seconds for gap filling (default: 60)"),
    db:Session=Depends(get_db)
):
    try:
        query_service=QueryService(db)
        results=await query_service.query_metrics(query)
        if not results:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No metrics found for the given query")
        
        if fill_gaps and results.get("points"):
            filled_points = query_service.fill_gaps(
                data_points=results["points"],
                start_time=query.start_time,
                end_time=query.end_time,
                interval_seconds=interval_seconds
            )
            results["points"] = filled_points
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    

@queryRouter.get("/query/raw", response_model=RawQueryResponse, status_code=status.HTTP_200_OK)
async def query_raw_metrics(
    metric_name: str = Query(..., description="Name of the metric to query"),
    start_time: datetime = Query(..., description="Start time for the query range"),
    end_time: datetime = Query(..., description="End time for the query range"),
    labels: Optional[str] = Query(None, description="Labels as JSON string, e.g. {\"host\":\"server1\"}"),
    fill_gaps: bool = Query(False, description="Fill missing data points with nulls"),
    interval_seconds: int = Query(60, description="Interval in seconds for gap filling (default: 60)"),
    db: Session = Depends(get_db)
):
    try:
        import json
        parsed_labels = json.loads(labels) if labels else {}
        
        query_service = QueryService(db)
        result = await query_service.query_raw_data(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            labels=parsed_labels
        )
        
        if not result["points"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No raw data found for the given query"
            )
        
        if fill_gaps:
            filled_points = query_service.fill_gaps(
                data_points=result["points"],
                start_time=start_time,
                end_time=end_time,
                interval_seconds=interval_seconds
            )
            result["points"] = filled_points
            result["total_points"] = len(filled_points)
        
        return result
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid labels format. Must be valid JSON string."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying raw data: {str(e)}"
        )

@queryRouter.get("/query/rollup", response_model=RollupQueryResponse, status_code=status.HTTP_200_OK)
async def query_rollup_metrics(
    metric_name: str = Query(..., description="Name of the metric to query"),
    start_time: datetime = Query(..., description="Start time for the query range"),
    end_time: datetime = Query(..., description="End time for the query range"),
    window: str = Query(..., description="Rollup window size: 1m, 5m, or 1h"),
    labels: Optional[str] = Query(None, description="Labels as JSON string, e.g. {\"host\":\"server1\"}"),
    db: Session = Depends(get_db)
):
    try:
        import json
        parsed_labels = json.loads(labels) if labels else {}
        
        query_service = QueryService(db)
        result = await query_service.query_rollup_data(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            window=window,
            labels=parsed_labels
        )
        
        if not result["points"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No rollup data found for window '{window}'"
            )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid labels format. Must be valid JSON string."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying rollup data: {str(e)}"
        )
