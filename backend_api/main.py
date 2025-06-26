"""
Agentic Calendar - FastAPI Backend
Professional REST API for AI-powered meeting scheduling and Google Calendar integration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv('../.env.local')

from routers import oauth, calendar, ai, health, demo

app = FastAPI(
    title="Agentic Calendar API",
    description="Professional backend API for AI-powered meeting scheduling with Google Calendar integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit default
        "http://localhost:3000",  # React dev server
        "https://*.streamlit.app",  # Streamlit Cloud
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["oauth"])
app.include_router(calendar.router, prefix="/api/v1/calendar", tags=["calendar"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(demo.router, prefix="/api/v1/demo", tags=["demo"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "TailorTalk API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1")
async def api_info():
    """API version information"""
    return {
        "api_version": "1.0.0",
        "endpoints": {
            "oauth": "/api/v1/oauth",
            "calendar": "/api/v1/calendar", 
            "ai": "/api/v1/ai",
            "health": "/api/v1/health"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    return {
        "error": "Internal server error",
        "detail": str(exc) if os.getenv("DEBUG_MODE", "false").lower() == "true" else "An unexpected error occurred",
        "path": str(request.url)
    }

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "127.0.0.1")
    debug = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )
