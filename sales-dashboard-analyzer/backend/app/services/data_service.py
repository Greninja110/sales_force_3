# File: backend/app/services/data_service.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import text
from typing import Dict, List, Optional, Tuple, Any

from ..database import get_connection
from ..models.schemas import Filter, SalesSummary
from ..utils.logger import log


class DataService:
    """Service for data processing and analysis."""
    
    @staticmethod
    def process_date_range(date_range: Optional[str], start_date: Optional[str], end_date: Optional[str]) -> Tuple[str, str]:
        """Process date range filters."""
        today = datetime.now().date()
        
        # If specific dates are provided, use them
        if start_date and end_date:
            return start_date, end_date
        
        # Otherwise, use date range
        if date_range:
            if date_range == "last_7_days":
                start_date = (today - timedelta(days=7)).isoformat()
                end_date = today.isoformat()
            elif date_range == "last_30_days":
                start_date = (today - timedelta(days=30)).isoformat()
                end_date = today.isoformat()
            elif date_range == "last_90_days":
                start_date = (today - timedelta(days=90)).isoformat()
                end_date = today.isoformat()
            elif date_range == "last_365_days":
                start_date = (today - timedelta(days=365)).isoformat()
                end_date = today.isoformat()
            elif date_range == "this_month":
                start_date = datetime(today.year, today.month, 1).date().isoformat()
                end_date = today.isoformat()
            elif date_range == "this_quarter":
                quarter_start_month = ((today.month - 1) // 3) * 3 + 1
                start_date = datetime(today.year, quarter_start_month, 1).date().isoformat()
                end_date = today.isoformat()
            elif date_range == "this_year":
                start_date = datetime(today.year, 1, 1).date().isoformat()
                end_date = today.isoformat()
            elif date_range == "all":
                start_date = "1900-01-01"
                end_date = "2100-12-31"
        
        # Default to last 30 days if no filter is provided
        if not start_date or not end_date:
            start_date = (today - timedelta(days=30)).isoformat()
            end_date = today.isoformat()
        
        return start_date, end_date
    
    @staticmethod
    def build_filter_query(filters: Filter) -> Tuple[str, Dict[str, Any]]:
        """Build SQL query based on filters."""
        query = "SELECT * FROM sales WHERE 1=1"
        params = {}
        
        # Process date range
        if filters.date_range or filters.start_date or filters.end_date:
            start_date, end_date = DataService.process_date_range(
                filters.date_range, 
                filters.start_date.isoformat() if filters.start_date else None,
                filters.end_date.isoformat() if filters.end_date else None
            )
            query += " AND order_date BETWEEN :start_date AND :end_date"
            params["start_date"] = start_date
            params["end_date"] = end_date
        
        # Add category filter
        if filters.category:
            query += " AND category = :category"
            params["category"] = filters.category
        
        # Add sub-category filter
        if filters.sub_category:
            query += " AND sub_category = :sub_category"
            params["sub_category"] = filters.sub_category
        
        # Add region filter
        if filters.region:
            query += " AND region = :region"
            params["region"] = filters.region
        
        return query, params

    @staticmethod
    def get_sales_summary(filters: Filter) -> SalesSummary:
        """Get sales summary."""
        conn = get_connection()
        
        try:
            # Build query with filters
            query, params = DataService.build_filter_query(filters)
            
            # Execute query
            df = pd.read_sql(text(query), conn, params=params)
            
            # Calculate summary metrics
            total_sales = df['sales'].sum()
            total_profit = df['profit'].sum()
            profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
            total_orders = df['order_id'].nunique()
            total_customers = df['customer_id'].nunique()
            avg_order_value = total_sales / total_orders if total_orders > 0 else 0
            
            # Create response
            summary = SalesSummary(
                total_sales=round(total_sales, 2),
                total_profit=round(total_profit, 2),
                profit_margin=round(profit_margin, 2),
                avg_order_value=round(avg_order_value, 2),
                total_orders=total_orders,
                total_customers=total_customers
            )
            
            return summary
        except Exception as e:
            log.error(f"Error getting sales summary: {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_sales_by_category(filters: Filter) -> List[Dict[str, Any]]:
        """Get sales breakdown by category."""
        conn = get_connection()
        
        try:
            # Build query with filters
            base_query, params = DataService.build_filter_query(filters)
            
            # Create aggregation query
            query = f"""
            SELECT 
                category,
                SUM(sales) as sales,
                SUM(profit) as profit,
                COUNT(DISTINCT order_id) as order_count
            FROM 
                ({base_query})
            GROUP BY 
                category
            ORDER BY 
                sales DESC
            """
            
            # Execute query
            df = pd.read_sql(text(query), conn, params=params)
            
            # Calculate profit margin
            df['profit_margin'] = np.where(df['sales'] > 0, (df['profit'] / df['sales']) * 100, 0)
            
            # Convert to list of dictionaries
            results = df.to_dict(orient="records")
            
            # Round numeric values
            for result in results:
                result['sales'] = round(result['sales'], 2)
                result['profit'] = round(result['profit'], 2)
                result['profit_margin'] = round(result['profit_margin'], 2)
            
            return results
        except Exception as e:
            log.error(f"Error getting sales by category: {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_sales_by_subcategory(filters: Filter) -> List[Dict[str, Any]]:
        """Get sales breakdown by subcategory."""
        conn = get_connection()
        
        try:
            # Build query with filters
            base_query, params = DataService.build_filter_query(filters)
            
            # Create aggregation query
            query = f"""
            SELECT 
                category,
                sub_category,
                SUM(sales) as sales,
                SUM(profit) as profit,
                COUNT(DISTINCT order_id) as order_count
            FROM 
                ({base_query})
            GROUP BY 
                category, sub_category
            ORDER BY 
                sales DESC
            """
            
            # Execute query
            df = pd.read_sql(text(query), conn, params=params)
            
            # Calculate profit margin
            df['profit_margin'] = np.where(df['sales'] > 0, (df['profit'] / df['sales']) * 100, 0)
            
            # Convert to list of dictionaries
            results = df.to_dict(orient="records")
            
            # Round numeric values
            for result in results:
                result['sales'] = round(result['sales'], 2)
                result['profit'] = round(result['profit'], 2)
                result['profit_margin'] = round(result['profit_margin'], 2)
            
            return results
        except Exception as e:
            log.error(f"Error getting sales by subcategory: {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_sales_by_region(filters: Filter) -> List[Dict[str, Any]]:
        """Get sales breakdown by region."""
        conn = get_connection()
        
        try:
            # Build query with filters
            base_query, params = DataService.build_filter_query(filters)
            
            # Create aggregation query
            query = f"""
            SELECT 
                region,
                SUM(sales) as sales,
                SUM(profit) as profit,
                COUNT(DISTINCT order_id) as order_count
            FROM 
                ({base_query})
            GROUP BY 
                region
            ORDER BY 
                sales DESC
            """
            
            # Execute query
            df = pd.read_sql(text(query), conn, params=params)
            
            # Calculate profit margin
            df['profit_margin'] = np.where(df['sales'] > 0, (df['profit'] / df['sales']) * 100, 0)
            
            # Convert to list of dictionaries
            results = df.to_dict(orient="records")
            
            # Round numeric values
            for result in results:
                result['sales'] = round(result['sales'], 2)
                result['profit'] = round(result['profit'], 2)
                result['profit_margin'] = round(result['profit_margin'], 2)
            
            return results
        except Exception as e:
            log.error(f"Error getting sales by region: {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_top_products(filters: Filter, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top products by sales."""
        conn = get_connection()
        
        try:
            # Build query with filters
            base_query, params = DataService.build_filter_query(filters)
            
            # Create aggregation query
            query = f"""
            SELECT 
                product_id,
                product_name,
                category,
                sub_category,
                SUM(sales) as sales,
                SUM(profit) as profit,
                SUM(quantity) as quantity
            FROM 
                ({base_query})
            GROUP BY 
                product_id, product_name, category, sub_category
            ORDER BY 
                sales DESC
            LIMIT 
                {limit}
            """
            
            # Execute query
            df = pd.read_sql(text(query), conn, params=params)
            
            # Calculate profit margin
            df['profit_margin'] = np.where(df['sales'] > 0, (df['profit'] / df['sales']) * 100, 0)
            
            # Convert to list of dictionaries
            results = df.to_dict(orient="records")
            
            # Round numeric values
            for result in results:
                result['sales'] = round(result['sales'], 2)
                result['profit'] = round(result['profit'], 2)
                result['profit_margin'] = round(result['profit_margin'], 2)
            
            return results
        except Exception as e:
            log.error(f"Error getting top products: {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_sales_time_series(filters: Filter) -> Dict[str, List[Dict[str, Any]]]:
        """Get sales time series data."""
        conn = get_connection()
        
        try:
            # Build query with filters
            base_query, params = DataService.build_filter_query(filters)
            
            # Create daily aggregation query
            daily_query = f"""
            SELECT 
                order_date as date,
                SUM(sales) as sales,
                SUM(profit) as profit,
                COUNT(DISTINCT order_id) as order_count
            FROM 
                ({base_query})
            GROUP BY 
                order_date
            ORDER BY 
                order_date
            """
            
            # Execute daily query
            daily_df = pd.read_sql(text(daily_query), conn, params=params)
            
            # Process daily data
            if not daily_df.empty:
                daily_df['date'] = pd.to_datetime(daily_df['date'])
                
                # Create weekly data
                weekly_df = daily_df.set_index('date').resample('W').sum().reset_index()
                
                # Create monthly data
                monthly_df = daily_df.set_index('date').resample('M').sum().reset_index()
                
                # Convert to list of dictionaries
                daily_data = daily_df.to_dict(orient="records")
                weekly_data = weekly_df.to_dict(orient="records")
                monthly_data = monthly_df.to_dict(orient="records")
                
                # Format dates and round numeric values
                for data_list in [daily_data, weekly_data, monthly_data]:
                    for item in data_list:
                        item['date'] = item['date'].strftime('%Y-%m-%d')
                        item['sales'] = round(item['sales'], 2)
                        item['profit'] = round(item['profit'], 2)
                
                return {
                    "daily": daily_data,
                    "weekly": weekly_data,
                    "monthly": monthly_data
                }
            else:
                return {
                    "daily": [],
                    "weekly": [],
                    "monthly": []
                }
        except Exception as e:
            log.error(f"Error getting sales time series: {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_dashboard_data(filters: Filter) -> Dict[str, Any]:
        """Get complete dashboard data."""
        try:
            # Get sales summary
            summary = DataService.get_sales_summary(filters)
            
            # Get sales by category
            categories = DataService.get_sales_by_category(filters)
            
            # Get sales by region
            regions = DataService.get_sales_by_region(filters)
            
            # Get time series data
            time_series = DataService.get_sales_time_series(filters)
            
            # Get top products
            top_products = DataService.get_top_products(filters)
            
            # Create response
            dashboard_data = {
                "summary": summary,
                "categories": categories,
                "regions": regions,
                "time_series": time_series,
                "top_products": top_products
            }
            
            return dashboard_data
        except Exception as e:
            log.error(f"Error getting dashboard data: {str(e)}")
            raise