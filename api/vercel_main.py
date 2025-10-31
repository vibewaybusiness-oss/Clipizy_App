#!/usr/bin/env python3
"""
Vercel-optimized FastAPI Main Application
Lightweight version without heavy ML dependencies
"""
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.config.settings import settings
from api.services.database import create_tables

# Import only essential routers for Vercel
from api.routers import (
    auth_router,
    automation_router,
    export_router,
    job_router,
    payment_router,
    project_router,
    prompt_router,
    social_media_router,
    stats_router,
    track_router,
)
from api.routers.business.credits import router as credits_router

# Import services for initialization
from api.services.utils.vercel_compatibility import check_ml_availability


class LargeBodyMiddleware(BaseHTTPMiddleware):
    """Middleware to handle large request bodies"""

    def __init__(self, app, max_body_size: int = 10 * 1024 * 1024):  # 10MB for Vercel
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        # Check content length if available
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return JSONResponse(status_code=413, content={"error": "Payload Too Large", "max_size": self.max_body_size})

        # Read the body to prevent uvicorn's default 1MB limit
        try:
            body = await request.body()
            if len(body) > self.max_body_size:
                return JSONResponse(
                    status_code=413, content={"error": "Payload Too Large", "max_size": self.max_body_size}
                )
            # Store the body for later use
            request._body = body
        except Exception as e:
            return JSONResponse(status_code=413, content={"error": "Failed to read request body", "detail": str(e)})

        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting clipizy API (Vercel optimized)...")

    # Check ML availability
    ml_status = check_ml_availability()
    print(f"📊 ML Libraries Status: {ml_status}")

    # Create database tables
    try:
        from api.services.database import create_tables

        create_tables()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"⚠️ Database table creation failed: {e}")

    yield

    # Shutdown
    print("🛑 Shutting down clipizy API...")


# Create FastAPI app
app = FastAPI(
    title="clipizy API (Vercel)",
    description="AI-powered music video generation platform - Vercel optimized",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware for large request bodies (10MB limit for Vercel)
app.add_middleware(LargeBodyMiddleware, max_body_size=10 * 1024 * 1024)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only essential routers for Vercel
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(project_router, prefix="/projects", tags=["projects"])
app.include_router(track_router, prefix="/tracks", tags=["tracks"])
app.include_router(export_router, prefix="/exports", tags=["exports"])
app.include_router(stats_router, prefix="/stats", tags=["stats"])
app.include_router(prompt_router, prefix="/prompts", tags=["prompts"])
app.include_router(credits_router, prefix="/api", tags=["credits"])
app.include_router(payment_router, prefix="/api", tags=["payments"])
app.include_router(social_media_router, tags=["social-media"])
app.include_router(automation_router, tags=["automation"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    ml_status = check_ml_availability()
    return {
        "message": "clipizy API (Vercel optimized)",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "ml_libraries": ml_status,
        "environment": "vercel",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ml_status = check_ml_availability()
    return {
        "status": "healthy",
        "service": "clipizy API (Vercel)",
        "version": "1.0.0",
        "ml_libraries": ml_status,
        "environment": "vercel",
    }


# ML status endpoint
@app.get("/ml-status")
async def ml_status():
    """Check ML library availability"""
    return {
        "ml_libraries": check_ml_availability(),
        "environment": "vercel",
        "message": "Some ML features may be limited in Vercel environment",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An error occurred",
            "environment": "vercel",
        },
    )


if __name__ == "__main__":
    uvicorn.run("api.vercel_main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
