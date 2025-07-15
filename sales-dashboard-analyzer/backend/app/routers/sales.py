# File: backend/app/routers/sales.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, List, Optional, Any

from ..services.data_service import DataService
from ..models.schemas import Filter, SalesSummary, ApiResponse

router = APIRouter(
    prefix="/api/sales",
    tags=["sales"],
    responses={404: {"description": "Not found"}},
)


@router.get("/dashboard", response_model=ApiResponse)
async def get_dashboard_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_30_days", description="Date range filter (e.g., last_30_days, all)")
):
    """Get complete dashboard data."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            region=region,
            date_range=date_range
        )
        
        data = DataService.get_dashboard_data(filters)
        
        return ApiResponse(
            status="success",
            message="Dashboard data retrieved successfully",
            data=data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving dashboard data: {str(e)}"
        )


@router.get("/summary", response_model=ApiResponse)
async def get_sales_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_30_days", description="Date range filter (e.g., last_30_days, all)")
):
    """Get sales summary."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            region=region,
            date_range=date_range
        )
        
        summary = DataService.get_sales_summary(filters)
        
        return ApiResponse(
            status="success",
            message="Sales summary retrieved successfully",
            data=summary
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sales summary: {str(e)}"
        )


@router.get("/by-category", response_model=ApiResponse)
async def get_sales_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_30_days", description="Date range filter (e.g., last_30_days, all)")
):
    """Get sales breakdown by category."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            region=region,
            date_range=date_range
        )
        
        categories = DataService.get_sales_by_category(filters)
        
        return ApiResponse(
            status="success",
            message="Sales by category retrieved successfully",
            data=categories
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sales by category: {str(e)}"
        )


@router.get("/by-subcategory", response_model=ApiResponse)
async def get_sales_by_subcategory(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_30_days", description="Date range filter (e.g., last_30_days, all)")
):
    """Get sales breakdown by subcategory."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            sub_category=sub_category,
            region=region,
            date_range=date_range
        )
        
        subcategories = DataService.get_sales_by_subcategory(filters)
        
        return ApiResponse(
            status="success",
            message="Sales by subcategory retrieved successfully",
            data=subcategories
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sales by subcategory: {str(e)}"
        )


@router.get("/by-region", response_model=ApiResponse)
async def get_sales_by_region(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_30_days", description="Date range filter (e.g., last_30_days, all)")
):
    """Get sales breakdown by region."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            region=region,
            date_range=date_range
        )
        
        regions = DataService.get_sales_by_region(filters)
        
        return ApiResponse(
            status="success",
            message="Sales by region retrieved successfully",
            data=regions
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sales by region: {str(e)}"
        )


@router.get("/time-series", response_model=ApiResponse)
async def get_sales_time_series(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_30_days", description="Date range filter (e.g., last_30_days, all)")
):
    """Get sales time series data."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            region=region,
            date_range=date_range
        )
        
        time_series = DataService.get_sales_time_series(filters)
        
        return ApiResponse(
            status="success",
            message="Sales time series retrieved successfully",
            data=time_series
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sales time series: {str(e)}"
        )


@router.get("/top-products", response_model=ApiResponse)
async def get_top_products(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    date_range: Optional[str] = Query("last_30_days", description="Date range filter (e.g., last_30_days, all)"),
    limit: int = Query(10, description="Number of products to return")
):
    """Get top products by sales."""
    try:
        filters = Filter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            region=region,
            date_range=date_range
        )
        
        products = DataService.get_top_products(filters, limit)
        
        return ApiResponse(
            status="success",
            message="Top products retrieved successfully",
            data=products
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving top products: {str(e)}"
        )