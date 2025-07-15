# File: backend/app/services/forecast_service.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import text
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet

from ..database import get_connection
from ..models.schemas import Filter, ForecastRequest
from ..utils.logger import log


class ForecastService:
    """Service for sales forecasting."""
    
    @staticmethod
    def generate_sales_forecast(filters: Filter, request: ForecastRequest) -> List[Dict[str, Any]]:
        """Generate sales forecast."""
        conn = get_connection()
        
        try:
            # Get time series data for forecasting
            from .data_service import DataService
            time_series_data = DataService.get_sales_time_series(filters)
            
            # Use daily data for forecasting
            df = pd.DataFrame(time_series_data["daily"])
            
            if df.empty:
                return []
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Sort by date
            df = df.sort_values('date')
            
            # Use Prophet for forecasting
            forecast_data = ForecastService._forecast_with_prophet(df, request.periods)
            
            return forecast_data
        except Exception as e:
            log.error(f"Error generating sales forecast: {str(e)}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def _forecast_with_prophet(df: pd.DataFrame, periods: int) -> List[Dict[str, Any]]:
        """Forecast using Prophet."""
        try:
            # Prepare data for Prophet
            prophet_df = df[['date', 'sales']].rename(columns={'date': 'ds', 'sales': 'y'})
            
            # Create and fit model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative',
                interval_width=0.95
            )
            
            model.fit(prophet_df)
            
            # Generate future dataframe
            future = model.make_future_dataframe(periods=periods)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Format results
            result_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
            result_df = result_df.rename(columns={
                'ds': 'date',
                'yhat': 'forecast',
                'yhat_lower': 'lower_bound',
                'yhat_upper': 'upper_bound'
            })
            
            # Convert to list of dictionaries
            results = result_df.to_dict(orient="records")
            
            # Format dates and round numeric values
            for item in results:
                item['date'] = item['date'].strftime('%Y-%m-%d')
                item['forecast'] = round(item['forecast'], 2)
                item['lower_bound'] = round(item['lower_bound'], 2)
                item['upper_bound'] = round(item['upper_bound'], 2)
            
            return results
        except Exception as e:
            log.error(f"Error forecasting with Prophet: {str(e)}")
            
            # Fallback to statistical forecast
            return ForecastService._forecast_with_arima(df, periods)
    
    @staticmethod
    def _forecast_with_arima(df: pd.DataFrame, periods: int) -> List[Dict[str, Any]]:
        """Forecast using ARIMA as fallback."""
        try:
            # Prepare data for ARIMA
            ts_data = df.set_index('date')['sales']
            
            # Fit SARIMA model - simple configuration
            model = SARIMAX(
                ts_data,
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, 12),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
            model_fit = model.fit(disp=False)
            
            # Generate forecast
            forecast = model_fit.get_forecast(steps=periods)
            
            # Get forecast values and confidence intervals
            mean_forecast = forecast.predicted_mean
            confidence_intervals = forecast.conf_int()
            
            # Create result dataframe
            last_date = df['date'].max()
            dates = [last_date + timedelta(days=i+1) for i in range(periods)]
            
            result_df = pd.DataFrame({
                'date': dates,
                'forecast': mean_forecast.values,
                'lower_bound': confidence_intervals.iloc[:, 0].values,
                'upper_bound': confidence_intervals.iloc[:, 1].values
            })
            
            # Convert to list of dictionaries
            results = result_df.to_dict(orient="records")
            
            # Format dates and round numeric values
            for item in results:
                item['date'] = item['date'].strftime('%Y-%m-%d')
                item['forecast'] = round(item['forecast'], 2)
                item['lower_bound'] = round(item['lower_bound'], 2)
                item['upper_bound'] = round(item['upper_bound'], 2)
            
            return results
        except Exception as e:
            log.error(f"Error forecasting with ARIMA: {str(e)}")
            
            # Simplest fallback - linear regression
            return ForecastService._forecast_with_linear_regression(df, periods)
    
    @staticmethod
    def _forecast_with_linear_regression(df: pd.DataFrame, periods: int) -> List[Dict[str, Any]]:
        """Simple linear regression forecast as ultimate fallback."""
        try:
            # Convert dates to numeric (days since first date)
            first_date = df['date'].min()
            df['days'] = (df['date'] - first_date).dt.days
            
            # Fit linear regression
            X = df['days'].values.reshape(-1, 1)
            y = df['sales'].values
            model = sm.OLS(y, sm.add_constant(X)).fit()
            
            # Generate forecast dates
            last_date = df['date'].max()
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(periods)]
            
            # Generate X values for forecast
            last_day = df['days'].max()
            forecast_days = np.array([last_day + i + 1 for i in range(periods)]).reshape(-1, 1)
            
            # Generate forecast
            forecast_X = sm.add_constant(forecast_days)
            forecast_values = model.predict(forecast_X)
            
            # Calculate simple confidence intervals (standard error based)
            std_err = np.sqrt(model.mse_resid)
            lower_bound = forecast_values - 1.96 * std_err
            upper_bound = forecast_values + 1.96 * std_err
            
            # Create result list
            results = []
            for i in range(periods):
                results.append({
                    'date': forecast_dates[i].strftime('%Y-%m-%d'),
                    'forecast': round(float(forecast_values[i]), 2),
                    'lower_bound': round(float(lower_bound[i]), 2) if lower_bound[i] > 0 else 0,
                    'upper_bound': round(float(upper_bound[i]), 2)
                })
            
            return results
        except Exception as e:
            log.error(f"Error forecasting with linear regression: {str(e)}")
            raise
    
    @staticmethod
    def generate_category_forecasts(filters: Filter, request: ForecastRequest) -> Dict[str, List[Dict[str, Any]]]:
        """Generate forecasts for each category."""
        conn = get_connection()
        
        try:
            # Get categories
            from .data_service import DataService
            categories = DataService.get_sales_by_category(filters)
            
            # Generate forecast for each category
            category_forecasts = {}
            
            for category_data in categories:
                category_name = category_data['category']
                
                # Create filter for this category
                category_filter = Filter(
                    start_date=filters.start_date,
                    end_date=filters.end_date,
                    category=category_name,
                    region=filters.region,
                    date_range=filters.date_range
                )
                
                # Generate forecast
                forecast = ForecastService.generate_sales_forecast(category_filter, request)
                
                # Add to results
                category_forecasts[category_name] = forecast
            
            return category_forecasts
        except Exception as e:
            log.error(f"Error generating category forecasts: {str(e)}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def generate_region_forecasts(filters: Filter, request: ForecastRequest) -> Dict[str, List[Dict[str, Any]]]:
        """Generate forecasts for each region."""
        conn = get_connection()
        
        try:
            # Get regions
            from .data_service import DataService
            regions = DataService.get_sales_by_region(filters)
            
            # Generate forecast for each region
            region_forecasts = {}
            
            for region_data in regions:
                region_name = region_data['region']
                
                # Create filter for this region
                region_filter = Filter(
                    start_date=filters.start_date,
                    end_date=filters.end_date,
                    category=filters.category,
                    region=region_name,
                    date_range=filters.date_range
                )
                
                # Generate forecast
                forecast = ForecastService.generate_sales_forecast(region_filter, request)
                
                # Add to results
                region_forecasts[region_name] = forecast
            
            return region_forecasts
        except Exception as e:
            log.error(f"Error generating region forecasts: {str(e)}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def analyze_seasonality(filters: Filter) -> Dict[str, Dict[str, float]]:
        """Analyze sales seasonality."""
        conn = get_connection()
        
        try:
            # Get time series data
            from .data_service import DataService
            time_series_data = DataService.get_sales_time_series(filters)
            
            # Use daily data for analysis
            df = pd.DataFrame(time_series_data["daily"])
            
            if df.empty:
                return {
                    "daily": {},
                    "weekly": {},
                    "monthly": {},
                    "quarterly": {}
                }
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Daily seasonality (day of week)
            df['day_of_week'] = df['date'].dt.day_name()
            daily_seasonality = df.groupby('day_of_week')['sales'].mean().to_dict()
            
            # Weekly seasonality (week of month)
            df['week_of_month'] = (df['date'].dt.day - 1) // 7 + 1
            weekly_seasonality = df.groupby('week_of_month')['sales'].mean().to_dict()
            
            # Monthly seasonality
            df['month'] = df['date'].dt.month_name()
            monthly_seasonality = df.groupby('month')['sales'].mean().to_dict()
            
            # Quarterly seasonality
            df['quarter'] = 'Q' + df['date'].dt.quarter.astype(str)
            quarterly_seasonality = df.groupby('quarter')['sales'].mean().to_dict()
            
            # Round values
            for seasonality in [daily_seasonality, weekly_seasonality, monthly_seasonality, quarterly_seasonality]:
                for key in seasonality:
                    seasonality[key] = round(seasonality[key], 2)
            
            return {
                "daily": daily_seasonality,
                "weekly": weekly_seasonality,
                "monthly": monthly_seasonality,
                "quarterly": quarterly_seasonality
            }
        except Exception as e:
            log.error(f"Error analyzing seasonality: {str(e)}")
            raise
        finally:
            conn.close()