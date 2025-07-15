# File: backend/app/main.py
import os
import time
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from .config import settings
from .database import init_db
from .routers import sales, forecasts
from .utils.logger import log

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sales.router)
app.include_router(forecasts.router)

# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log API requests and response time."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log the request
    log.log_api_request(request, process_time)
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    log.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"Welcome to {settings.APP_NAME}", "version": settings.APP_VERSION}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}

# Initialize database endpoint
@app.post("/api/init-db", tags=["admin"])
async def initialize_database():
    """Initialize database with data."""
    try:
        init_db()
        return {"status": "success", "message": "Database initialized successfully"}
    except Exception as e:
        log.error(f"Error initializing database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing database: {str(e)}"
        )

# Startup event handler
@app.on_event("startup")
async def startup_event():
    """Event handler for application startup."""
    log.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Initialize database on startup
        init_db()
        log.info("Database initialized successfully")
    except Exception as e:
        log.error(f"Error initializing database on startup: {str(e)}")

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """Event handler for application shutdown."""
    log.info(f"Shutting down {settings.APP_NAME}")


# Run the application
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)