# File: backend/app/routers/forecasts.py
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from typing import Dict, List, Optional, Any

from ..services.forecast_service import ForecastService
from ..models.schemas import Filter, ForecastRequest, ApiResponse

router = APIRouter(
    prefix="/api/forecasts",
    tags=["forecasts"],
    responses={404: {"description": "Not found"}},
)


@router.get("/sales", response_model=ApiResponse)
async def generate_sales_forecast(
    periods: int = Query(30, description="Number of days to forecast"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_90_days", description="Date range filter (e.g., last_90_days, all)")
):
    """Generate a sales forecast."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            region=region,
            date_range=date_range
        )
        
        request = ForecastRequest(periods=periods)
        
        forecast = ForecastService.generate_sales_forecast(filters, request)
        
        return ApiResponse(
            status="success",
            message="Sales forecast generated successfully",
            data=forecast
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating sales forecast: {str(e)}"
        )


@router.get("/by-category", response_model=ApiResponse)
async def generate_category_forecasts(
    periods: int = Query(30, description="Number of days to forecast"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_90_days", description="Date range filter (e.g., last_90_days, all)")
):
    """Generate forecasts for each product category."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            region=region,
            date_range=date_range
        )
        
        request = ForecastRequest(periods=periods)
        
        forecasts = ForecastService.generate_category_forecasts(filters, request)
        
        return ApiResponse(
            status="success",
            message="Category forecasts generated successfully",
            data=forecasts
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating category forecasts: {str(e)}"
        )


@router.get("/by-region", response_model=ApiResponse)
async def generate_region_forecasts(
    periods: int = Query(30, description="Number of days to forecast"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    date_range: Optional[str] = Query("last_90_days", description="Date range filter (e.g., last_90_days, all)")
):
    """Generate forecasts for each region."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            date_range=date_range
        )
        
        request = ForecastRequest(periods=periods)
        
        forecasts = ForecastService.generate_region_forecasts(filters, request)
        
        return ApiResponse(
            status="success",
            message="Region forecasts generated successfully",
            data=forecasts
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating region forecasts: {str(e)}"
        )


@router.get("/seasonality", response_model=ApiResponse)
async def analyze_seasonality(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_365_days", description="Date range filter (e.g., last_365_days, all)")
):
    """Analyze sales seasonality."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            region=region,
            date_range=date_range
        )
        
        seasonality = ForecastService.analyze_seasonality(filters)
        
        return ApiResponse(
            status="success",
            message="Seasonality analysis completed successfully",
            data=seasonality
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing seasonality: {str(e)}"
        )


@router.post("/custom", response_model=ApiResponse)
async def generate_custom_forecast(
    request: ForecastRequest = Body(...),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_90_days", description="Date range filter (e.g., last_90_days, all)")
):
    """Generate a custom sales forecast."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            region=region,
            date_range=date_range
        )
        
        forecast = ForecastService.generate_sales_forecast(filters, request)
        
        return ApiResponse(
            status="success",
            message="Custom forecast generated successfully",
            data=forecast
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating custom forecast: {str(e)}"
        )