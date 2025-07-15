# File: backend/app/utils/logger.py
import sys
import os
import time
from pathlib import Path
from loguru import logger as log
from fastapi import Request

from ..config import settings

# Configure logger
log_file_path = os.path.join(settings.LOG_PATH, f"app_{time.strftime('%Y%m%d')}.log")

# Remove default logger
log.remove()

# Add console logger
log.add(
    sys.stderr,
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL,
    colorize=True,
)

# Add file logger
log.add(
    log_file_path,
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL,
    rotation="12:00",  # New file at noon
    compression="zip",
    retention="30 days",
)

# Utility function for logging API requests
def log_api_request(request: Request, process_time: float) -> None:
    """Log API request details."""
    log.info(
        f"Request: {request.method} {request.url.path} "
        f"| Client: {request.client.host if request.client else 'Unknown'} "
        f"| Time: {process_time:.4f}s"
    )

# Add utility functions to log object
log.log_api_request = log_api_request

# Export configured logger
__all__ = ["log"]