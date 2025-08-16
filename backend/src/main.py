"""
LeadGen Makeover Agent API - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.core import settings, validate_environment
from src.middleware.rate_limit_middleware import YelpFusionRateLimitMiddleware
from src.api.v1 import (
    authentication,
    business_search,
    website_scoring,
    rate_limit_monitoring,
    leadgen_chat,
    leadgen_agent,
    website_generation,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logging.info("Starting LeadGen Makeover Agent API...")

    # Validate environment configuration
    if not validate_environment():
        logging.error("Environment validation failed during startup")
        raise RuntimeError("Environment configuration validation failed")

    logging.info("Environment validation successful")
    logging.info("LeadGen Makeover Agent API started successfully")

    yield

    # Shutdown
    logging.info("Shutting down LeadGen Makeover Agent API...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="API for LeadGen Makeover Agent - Business Discovery and Website Scoring",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Yelp Fusion rate limiting middleware
app.add_middleware(YelpFusionRateLimitMiddleware)

# Include API routers
app.include_router(authentication.router, prefix=settings.API_V1_STR)
app.include_router(business_search.router, prefix="/api/v1")
app.include_router(website_scoring.router, prefix="/api/v1")
app.include_router(rate_limit_monitoring.router, prefix="/api/v1")
app.include_router(leadgen_chat.router, prefix="/api/v1")
app.include_router(leadgen_agent.router, prefix="/api/v1")
app.include_router(website_generation.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to LeadGen Makeover Agent API",
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def root_health():
    """Root health check endpoint."""
    return {
        "status": "healthy",
        "service": "LeadGen Makeover Agent API",
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
