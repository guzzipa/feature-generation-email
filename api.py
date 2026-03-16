#!/usr/bin/env python3
"""
Email Intelligence REST API (v3.5)

Fast, async REST API service for email enrichment.
Provides HTTP endpoints for single and batch email enrichment.

Features:
- Async/await for high performance
- Automatic API documentation (Swagger/OpenAPI)
- Redis caching integration
- Rate limiting (optional)
- API key authentication (optional)
- Health checks and monitoring

Usage:
    # Development
    uvicorn api:app --reload --port 8000

    # Production
    uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

Version: 3.5.0
"""

from fastapi import FastAPI, HTTPException, Query, Body, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Import our enrichment pipeline
from full_enrichment import FullEnrichmentPipeline
from cache_manager import get_cache_manager

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Email Intelligence API",
    description="Extract 291+ features from email addresses using OSINT, commercial APIs, and behavioral analysis",
    version="3.5.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance (initialized on startup)
pipeline: Optional[FullEnrichmentPipeline] = None
cache_manager = None

# Configuration
API_KEY = os.getenv("API_KEY", None)  # Optional API key authentication
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"


# ============================================================================
# Pydantic Models (Request/Response schemas)
# ============================================================================

class EnrichmentRequest(BaseModel):
    """Request model for email enrichment"""
    email: EmailStr = Field(..., description="Email address to enrich")
    ip_address: Optional[str] = Field(None, description="Optional IP address for geolocation")
    skip_commercial: bool = Field(False, description="Skip commercial APIs (Hunter, EmailRep, Clearbit)")
    skip_additional: bool = Field(False, description="Skip additional sources (WHOIS, IPQS, etc)")
    force_refresh: bool = Field(False, description="Force refresh (bypass cache)")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "ip_address": "181.45.123.45",
                "skip_commercial": False,
                "skip_additional": False,
                "force_refresh": False
            }
        }


class BatchEnrichmentRequest(BaseModel):
    """Request model for batch enrichment"""
    emails: List[EmailStr] = Field(..., description="List of email addresses to enrich", max_items=100)
    ip_address: Optional[str] = Field(None, description="Optional IP address for all emails")
    skip_commercial: bool = Field(False, description="Skip commercial APIs")
    skip_additional: bool = Field(False, description="Skip additional sources")
    force_refresh: bool = Field(False, description="Force refresh (bypass cache)")

    @validator('emails')
    def validate_emails_count(cls, v):
        if len(v) > 100:
            raise ValueError('Maximum 100 emails per batch request')
        if len(v) == 0:
            raise ValueError('At least 1 email required')
        return v

    class Config:
        schema_extra = {
            "example": {
                "emails": ["user1@example.com", "user2@example.com"],
                "skip_commercial": False
            }
        }


class EnrichmentResponse(BaseModel):
    """Response model for enrichment"""
    email: str
    pipeline_version: str
    enrichment_timestamp: str
    data_sources: Dict[str, Any]
    features: Dict[str, Any]
    summary: Dict[str, Any]
    cached: bool = Field(False, description="Whether result was retrieved from cache")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str
    cache_enabled: bool
    cache_connected: bool
    features_available: int = 291


class StatsResponse(BaseModel):
    """API statistics response"""
    cache_stats: Dict[str, Any]
    uptime: str


# ============================================================================
# Dependency: API Key Authentication (Optional)
# ============================================================================

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key if authentication is enabled"""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return x_api_key


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup"""
    global pipeline, cache_manager

    logger.info("🚀 Starting Email Intelligence API v3.5")

    # Initialize pipeline
    pipeline = FullEnrichmentPipeline(
        output_dir="results",
        enable_cache=ENABLE_CACHE
    )

    # Initialize cache manager
    cache_manager = get_cache_manager(enabled=ENABLE_CACHE)

    logger.info(f"✅ Pipeline initialized (cache: {ENABLE_CACHE})")
    logger.info(f"🔐 API Key authentication: {'Enabled' if API_KEY else 'Disabled'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down Email Intelligence API")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """API root endpoint"""
    return {
        "name": "Email Intelligence API",
        "version": "3.5.0",
        "description": "Extract 291+ features from email addresses",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    cache_stats = cache_manager.get_stats() if cache_manager else {}

    return HealthResponse(
        status="healthy",
        version="3.5.0",
        timestamp=datetime.now().isoformat(),
        cache_enabled=ENABLE_CACHE,
        cache_connected=cache_stats.get('connected', False)
    )


@app.get("/stats", response_model=StatsResponse, tags=["General"], dependencies=[Depends(verify_api_key)])
async def get_stats():
    """Get API statistics (requires API key if enabled)"""
    cache_stats = cache_manager.get_stats() if cache_manager else {}

    return StatsResponse(
        cache_stats=cache_stats,
        uptime="N/A"  # Could implement uptime tracking
    )


@app.post("/enrich", response_model=EnrichmentResponse, tags=["Enrichment"], dependencies=[Depends(verify_api_key)])
async def enrich_email(request: EnrichmentRequest):
    """
    Enrich a single email address

    Extracts 291+ features including:
    - OSINT data (GitHub, Gravatar, HIBP)
    - Email patterns and validation
    - IP intelligence and geolocation
    - Commercial APIs (optional)
    - Derived scores and metrics

    Returns comprehensive enrichment data and ML-ready features.
    """
    try:
        logger.info(f"Enriching: {request.email}")

        # Check cache first
        cached = False
        if ENABLE_CACHE and not request.force_refresh:
            cached_result = cache_manager.get(request.email, 'full_enrichment')
            if cached_result:
                cached_result['cached'] = True
                logger.info(f"⚡ Cache hit for {request.email}")
                return EnrichmentResponse(**cached_result)

        # Create pipeline instance for this request
        req_pipeline = FullEnrichmentPipeline(
            output_dir="results",
            skip_commercial=request.skip_commercial,
            skip_additional=request.skip_additional,
            ip_address=request.ip_address,
            enable_cache=ENABLE_CACHE and not request.force_refresh,
            force_refresh=request.force_refresh
        )

        # Run enrichment
        result = await asyncio.to_thread(
            req_pipeline.enrich_email,
            request.email
        )

        result['cached'] = False

        # Cache result
        if ENABLE_CACHE:
            cache_manager.set(request.email, 'full_enrichment', result)

        logger.info(f"✅ Enriched: {request.email}")

        return EnrichmentResponse(**result)

    except Exception as e:
        logger.error(f"Enrichment error for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enrichment failed: {str(e)}"
        )


@app.get("/enrich/{email}", response_model=EnrichmentResponse, tags=["Enrichment"], dependencies=[Depends(verify_api_key)])
async def enrich_email_get(
    email: str,
    ip_address: Optional[str] = Query(None, description="IP address for geolocation"),
    skip_commercial: bool = Query(False, description="Skip commercial APIs"),
    skip_additional: bool = Query(False, description="Skip additional sources"),
    force_refresh: bool = Query(False, description="Force cache refresh")
):
    """
    Enrich email via GET request (alternative to POST)

    Example: GET /enrich/user@example.com?ip_address=181.45.123.45
    """
    request = EnrichmentRequest(
        email=email,
        ip_address=ip_address,
        skip_commercial=skip_commercial,
        skip_additional=skip_additional,
        force_refresh=force_refresh
    )

    return await enrich_email(request)


@app.post("/enrich/batch", tags=["Enrichment"], dependencies=[Depends(verify_api_key)])
async def enrich_batch(request: BatchEnrichmentRequest):
    """
    Enrich multiple emails in batch

    Maximum 100 emails per request.
    Processes emails concurrently for better performance.
    Returns array of enrichment results.
    """
    try:
        logger.info(f"Batch enrichment: {len(request.emails)} emails")

        # Process emails concurrently
        tasks = []
        for email in request.emails:
            req = EnrichmentRequest(
                email=email,
                ip_address=request.ip_address,
                skip_commercial=request.skip_commercial,
                skip_additional=request.skip_additional,
                force_refresh=request.force_refresh
            )
            tasks.append(enrich_email(req))

        # Wait for all enrichments to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results (handle any errors)
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "email": request.emails[i],
                    "error": str(result),
                    "success": False
                })
            else:
                processed_results.append({
                    **result.dict(),
                    "success": True
                })

        success_count = sum(1 for r in processed_results if r.get('success', False))

        return {
            "total": len(request.emails),
            "success": success_count,
            "failed": len(request.emails) - success_count,
            "results": processed_results
        }

    except Exception as e:
        logger.error(f"Batch enrichment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch enrichment failed: {str(e)}"
        )


@app.delete("/cache/{email}", tags=["Cache"], dependencies=[Depends(verify_api_key)])
async def invalidate_cache(email: str):
    """Invalidate cache for specific email"""
    if not cache_manager:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cache not enabled"
        )

    deleted = cache_manager.invalidate(email)

    return {
        "email": email,
        "deleted_keys": deleted,
        "message": f"Cache invalidated for {email}"
    }


@app.delete("/cache", tags=["Cache"], dependencies=[Depends(verify_api_key)])
async def flush_cache(confirm: bool = Query(False, description="Confirm cache flush")):
    """Flush all cache (dangerous - requires confirmation)"""
    if not cache_manager:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cache not enabled"
        )

    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must set confirm=true to flush cache"
        )

    success = cache_manager.flush_all(confirm=True)

    return {
        "message": "Cache flushed" if success else "Cache flush failed",
        "success": success
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# Main (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
