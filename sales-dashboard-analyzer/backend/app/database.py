# File: backend/app/database.py
import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
import datetime

from .config import settings
from .utils.logger import log

# Create SQLAlchemy engine
engine = create_engine(settings.DB_PATH, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Define models
class Sales(Base):
    """Sales data model."""
    
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer, index=True)
    order_id = Column(String, index=True)
    order_date = Column(Date, index=True)
    ship_date = Column(Date)
    ship_mode = Column(String)
    customer_id = Column(String, index=True)
    customer_name = Column(String)
    segment = Column(String)
    country = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    region = Column(String, index=True)
    product_id = Column(String, index=True)
    category = Column(String, index=True)
    sub_category = Column(String, index=True)
    product_name = Column(String)
    sales = Column(Float)
    quantity = Column(Integer)
    discount = Column(Float)
    profit = Column(Float)


# Database utility functions
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with data from CSV."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if data already exists
    try:
        conn = sqlite3.connect(settings.DB_PATH.replace("sqlite:///", ""))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sales")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            log.info(f"Database already contains {count} records. Skipping initialization.")
            return
    except sqlite3.OperationalError:
        # Table doesn't exist yet, continue with initialization
        pass
    
    # Load data from CSV
    log.info(f"Initializing database from {settings.DATASET_FILE}")
    try:
        # Check if file exists
        if not os.path.exists(settings.DATASET_FILE):
            log.error(f"Dataset file not found: {settings.DATASET_FILE}")
            # Create a sample dataset for testing
            create_sample_dataset()
            return
        
        df = pd.read_csv(settings.DATASET_FILE)
        
        # Process data
        # Check if the expected columns exist, if not rename existing columns to match
        expected_columns = {
            'Row ID': 'row_id',
            'Order ID': 'order_id',
            'Order Date': 'order_date',
            'Ship Date': 'ship_date',
            'Ship Mode': 'ship_mode',
            'Customer ID': 'customer_id',
            'Customer Name': 'customer_name',
            'Segment': 'segment',
            'Country': 'country',
            'City': 'city',
            'State': 'state',
            'Postal Code': 'postal_code',
            'Region': 'region',
            'Product ID': 'product_id',
            'Category': 'category',
            'Sub-Category': 'sub_category',
            'Product Name': 'product_name',
            'Sales': 'sales',
            'Quantity': 'quantity',
            'Discount': 'discount',
            'Profit': 'profit'
        }
        
        # Map any existing columns to expected format
        df_columns = df.columns.tolist()
        column_mapping = {}
        for expected_col, db_col in expected_columns.items():
            if expected_col in df_columns:
                column_mapping[expected_col] = db_col
            elif expected_col.lower() in [col.lower() for col in df_columns]:
                # Case-insensitive matching
                actual_col = next(col for col in df_columns if col.lower() == expected_col.lower())
                column_mapping[actual_col] = db_col
        
        # Rename columns
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        # Convert date columns
        date_columns = ['order_date', 'ship_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Insert data into database
        conn = engine.connect()
        df.to_sql('sales', conn, if_exists='replace', index=False)
        conn.close()
        
        log.info(f"Successfully loaded {len(df)} records into database.")
    except Exception as e:
        log.error(f"Error initializing database: {str(e)}")
        raise


def create_sample_dataset():
    """Create a sample dataset for testing."""
    log.info("Creating sample dataset for testing")
    
    # Create a sample dataframe
    data = {
        'row_id': list(range(1, 101)),
        'order_id': [f'ORD-{i:05d}' for i in range(1, 101)],
        'order_date': [datetime.datetime.now() - datetime.timedelta(days=i % 30) for i in range(1, 101)],
        'ship_date': [datetime.datetime.now() - datetime.timedelta(days=(i % 30) - 2) for i in range(1, 101)],
        'ship_mode': ['Standard', 'Express', 'Priority', 'Same Day'],
        'customer_id': [f'CUS-{i:05d}' for i in range(1, 101)],
        'customer_name': [f'Customer {i}' for i in range(1, 101)],
        'segment': ['Consumer', 'Corporate', 'Home Office'],
        'country': ['United States'],
        'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
        'state': ['New York', 'California', 'Illinois', 'Texas', 'Arizona'],
        'postal_code': [f'{10000 + i}' for i in range(1, 101)],
        'region': ['East', 'West', 'Central', 'South'],
        'product_id': [f'PRD-{i:05d}' for i in range(1, 101)],
        'category': ['Furniture', 'Office Supplies', 'Technology'],
        'sub_category': ['Chairs', 'Tables', 'Phones', 'Binders', 'Storage', 'Appliances'],
        'product_name': [f'Product {i}' for i in range(1, 101)],
        'sales': [round(100 + i * 2.5, 2) for i in range(1, 101)],
        'quantity': [i % 10 + 1 for i in range(1, 101)],
        'discount': [round(i % 5 / 10, 2) for i in range(1, 101)],
        'profit': [round(50 + i * 1.2, 2) for i in range(1, 101)],
    }
    
    # Create a dataframe from the data
    df = pd.DataFrame()
    for col, values in data.items():
        df[col] = pd.Series(values).sample(100, replace=True).reset_index(drop=True)
    
    # Save to CSV
    os.makedirs(os.path.dirname(settings.DATASET_FILE), exist_ok=True)
    df.to_csv(settings.DATASET_FILE, index=False)
    
    # Insert into database
    conn = engine.connect()
    df.to_sql('sales', conn, if_exists='replace', index=False)
    conn.close()
    
    log.info(f"Successfully created and loaded 100 sample records into database.")


def get_connection():
    """Get database connection."""
    return engine.connect()