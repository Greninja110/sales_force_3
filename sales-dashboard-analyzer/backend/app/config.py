# File: backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_NAME: str = "Sales Dashboard Analyzer"
    APP_DESCRIPTION: str = "Sales data visualization and forecasting"
    APP_VERSION: str = "1.0.0"
    
    # API settings
    API_PREFIX: str = "/api"
    
    # CORS settings - using Optional[str] and handling the parsing in __init__
    CORS_ORIGINS_STR: Optional[str] = None
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database settings
    DB_PATH: str = "sqlite:///./data/sales.db"
    
    # Data settings
    DATA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    DATASET_FILE: str = os.path.join(DATA_PATH, "superstore.csv")
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOG_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    
    # Make sure paths exist
    def __init__(self, **data):
        super().__init__(**data)
        
        # Process CORS_ORIGINS from string if provided
        if self.CORS_ORIGINS_STR:
            self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
        
        # Create directories if they don't exist
        Path(self.DATA_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.LOG_PATH).mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()