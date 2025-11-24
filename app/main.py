"""
Finnish NLP Toolkit API
Main FastAPI application entry point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from typing import Dict
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Finnish NLP Toolkit API",
    description="Backend service for Finnish text lemmatization, complexity analysis, and profanity detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify API is running
    """
    return {
        "status": "healthy",
        "service": "Finnish NLP Toolkit API"
    }

# Version endpoint
@app.get("/version", tags=["System"])
async def get_version() -> Dict[str, str]:
    """
    Get API version information
    """
    return {
        "version": "1.0.0",
        "api": "Finnish NLP Toolkit",
        "python_version": sys.version
    }

# Root endpoint
@app.get("/", tags=["System"])
async def root() -> Dict[str, str]:
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to Finnish NLP Toolkit API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Import and include routers
from app.routers import lemmatizer, complexity, profanity, batch_processing

app.include_router(lemmatizer.router, prefix="/api", tags=["Lemmatization"])
app.include_router(complexity.router, prefix="/api", tags=["Complexity"])
app.include_router(profanity.router, prefix="/api", tags=["Profanity"])
app.include_router(batch_processing.router, prefix="/api", tags=["Batch Processing"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
