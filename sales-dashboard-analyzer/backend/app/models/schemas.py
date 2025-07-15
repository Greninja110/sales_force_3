# File: backend/app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any
from datetime import date, datetime


# Base schemas
class SaleBase(BaseModel):
    """Base sales data model."""
    
    order_id: str
    order_date: date
    ship_date: date
    ship_mode: str
    customer_id: str
    customer_name: str
    segment: str
    country: str
    city: str
    state: str
    postal_code: str
    region: str
    product_id: str
    category: str
    sub_category: str
    product_name: str
    sales: float
    quantity: int
    discount: float
    profit: float


class SaleCreate(SaleBase):
    """Create sales data model."""
    
    row_id: int


class Sale(SaleBase):
    """Sales data model."""
    
    id: int
    row_id: int
    
    class Config:
        orm_mode = True


# Response schemas
class SalesSummary(BaseModel):
    """Sales summary response model."""
    
    total_sales: float
    total_profit: float
    profit_margin: float
    avg_order_value: float
    total_orders: int
    total_customers: int


class CategorySales(BaseModel):
    """Category sales response model."""
    
    category: str
    sales: float
    profit: float
    profit_margin: float
    order_count: int


class SubCategorySales(BaseModel):
    """Sub-category sales response model."""
    
    category: str
    sub_category: str
    sales: float
    profit: float
    profit_margin: float
    order_count: int


class RegionSales(BaseModel):
    """Region sales response model."""
    
    region: str
    sales: float
    profit: float
    profit_margin: float
    order_count: int


class TimeSeries(BaseModel):
    """Time series response model."""
    
    date: Union[str, date, datetime]
    sales: float
    profit: float
    order_count: int


class TimeSeriesResponse(BaseModel):
    """Time series data response model."""
    
    daily: List[TimeSeries]
    weekly: List[TimeSeries]
    monthly: List[TimeSeries]


class TopProduct(BaseModel):
    """Top product response model."""
    
    product_id: str
    product_name: str
    category: str
    sub_category: str
    sales: float
    profit: float
    profit_margin: float
    quantity: int


class Forecast(BaseModel):
    """Forecast response model."""
    
    date: Union[str, date, datetime]
    forecast: float
    lower_bound: float
    upper_bound: float


class ForecastRequest(BaseModel):
    """Forecast request model."""
    
    periods: int = Field(30, description="Number of days to forecast")
    category: Optional[str] = None
    region: Optional[str] = None


class Filter(BaseModel):
    """Filter request model."""
    
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    region: Optional[str] = None
    date_range: Optional[str] = None  # e.g. "last_30_days", "last_90_days", "all"


# Dashboard response schemas
class DashboardStats(BaseModel):
    """Dashboard statistics response model."""
    
    summary: SalesSummary
    categories: List[CategorySales]
    regions: List[RegionSales]
    time_series: TimeSeriesResponse
    top_products: List[TopProduct]


class SeasonalityAnalysis(BaseModel):
    """Seasonality analysis response model."""
    
    daily: Dict[str, float]
    weekly: Dict[str, float]
    monthly: Dict[str, float]
    quarterly: Dict[str, float]


# Generic responses
class ApiResponse(BaseModel):
    """Generic API response model."""
    
    status: str
    message: str
    data: Optional[Any] = None