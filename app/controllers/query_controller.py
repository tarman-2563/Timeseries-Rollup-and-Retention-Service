from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.query_service import QueryService
from app.schemas.query import RawQueryResponse, RollupQueryResponse
from datetime import datetime
from typing import Optional, Dict
import json


class QueryController:
    
    @staticmethod
    async def query_raw_metrics(
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        labels: Optional[str],
        fill_gaps: bool,
        interval_seconds: int,
        db: Session
    ) -> RawQueryResponse:
        try:
            parsed_labels = QueryController._parse_labels(labels)
            query_service = QueryService(db)
            result = await query_service.query_raw_data(
                metric_name=metric_name,
                start_time=start_time,
                end_time=end_time,
                labels=parsed_labels
            )
            
            # Return empty result instead of 404 error
            if not result["points"]:
                return {
                    "metric_name": metric_name,
                    "points": [],
                    "total_points": 0
                }
            
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
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error querying raw data: {str(e)}"
            )
    
    @staticmethod
    async def query_rollup_metrics(
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        window: str,
        labels: Optional[str],
        db: Session
    ) -> RollupQueryResponse:
        try:
            parsed_labels = QueryController._parse_labels(labels)
            query_service = QueryService(db)
            result = await query_service.query_rollup_data(
                metric_name=metric_name,
                start_time=start_time,
                end_time=end_time,
                window=window,
                labels=parsed_labels
            )
            
            # Return empty result instead of 404 error
            if not result["points"]:
                return {
                    "metric_name": metric_name,
                    "window": window,
                    "points": [],
                    "total_points": 0
                }
            
            return result
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error querying rollup data: {str(e)}"
            )
    
    @staticmethod
    def _parse_labels(labels_json: Optional[str]) -> Dict[str, str]:
        if not labels_json:
            return {}
        
        try:
            return json.loads(labels_json)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid labels format. Must be valid JSON string."
            )
