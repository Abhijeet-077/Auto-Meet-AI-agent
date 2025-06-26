"""
Health Router for TailorTalk API
Provides health check and status endpoints
"""

from fastapi import APIRouter
from datetime import datetime
import os

from models import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Check service statuses
    services = {}
    
    # Check OAuth configuration
    oauth_configured = bool(
        os.getenv('GOOGLE_CLIENT_ID') and 
        os.getenv('GOOGLE_CLIENT_SECRET') and
        os.getenv('GOOGLE_CLIENT_ID') != 'your_google_client_id_here'
    )
    services["oauth"] = "configured" if oauth_configured else "not_configured"
    
    # Check Gemini AI configuration
    gemini_configured = bool(
        os.getenv('GEMINI_API_KEY') and
        os.getenv('GEMINI_API_KEY') not in ['your_gemini_api_key_here']
    )
    services["gemini"] = "configured" if gemini_configured else "not_configured"
    
    # Check encryption key
    encryption_configured = bool(
        os.getenv('ENCRYPTION_KEY') and 
        os.getenv('ENCRYPTION_KEY') != 'your_encryption_key_here'
    )
    services["encryption"] = "configured" if encryption_configured else "not_configured"
    
    # Overall status
    all_configured = oauth_configured and gemini_configured and encryption_configured
    status = "healthy" if all_configured else "degraded"
    
    return HealthResponse(
        status=status,
        timestamp=datetime.now(),
        version="1.0.0",
        services=services
    )

@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.now()}

@router.get("/version")
async def version():
    """API version information"""
    return {
        "version": "1.0.0",
        "api_name": "TailorTalk API",
        "description": "Backend API for TailorTalk AI Calendar Assistant"
    }
