"""
Simplified FastAPI Backend for TailorTalk Application
Minimal working version for demonstration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv('../.env.local')

# Create FastAPI app
app = FastAPI(
    title="TailorTalk API",
    description="Backend API for TailorTalk AI Calendar Assistant",
    version="1.0.0",
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

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "TailorTalk API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/health")
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
    
    return {
        "status": status,
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "services": services
    }

@app.get("/api/v1/oauth/config")
async def get_oauth_config():
    """Get OAuth configuration"""
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    redirect_uri = f"{os.getenv('API_BASE_URL', 'http://localhost:8000')}/api/v1/oauth/callback"
    scopes = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    is_configured = bool(client_id and client_id != 'your_google_client_id_here')
    
    return {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scopes": scopes,
        "is_configured": is_configured
    }

@app.get("/api/v1/oauth/auth-url")
async def generate_auth_url():
    """Generate OAuth authorization URL"""
    import secrets
    from urllib.parse import urlencode
    
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    if not client_id or client_id == 'your_google_client_id_here':
        raise HTTPException(status_code=400, detail="OAuth not configured")
    
    redirect_uri = f"{os.getenv('API_BASE_URL', 'http://localhost:8000')}/api/v1/oauth/callback"
    scopes = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    state = secrets.token_urlsafe(32)
    
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'response_type': 'code',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    return {
        "auth_url": auth_url,
        "state": state
    }

@app.get("/api/v1/oauth/status")
async def oauth_status():
    """Get OAuth service status"""
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    is_configured = bool(
        client_id and client_id != 'your_google_client_id_here' and
        client_secret and client_secret != 'PLACEHOLDER_CLIENT_SECRET'
    )
    
    return {
        "success": is_configured,
        "message": "OAuth configured" if is_configured else "OAuth not configured"
    }

@app.get("/api/v1/ai/status")
async def ai_status():
    """Get AI service status"""
    api_key = os.getenv('GEMINI_API_KEY', '')
    is_configured = bool(api_key and api_key != 'your_gemini_api_key_here')
    
    return {
        "success": is_configured,
        "message": "AI service configured" if is_configured else "AI service not configured"
    }

@app.post("/api/v1/ai/chat")
async def chat():
    """Process AI chat request (placeholder)"""
    return {
        "response": "Hello! This is a placeholder response from the FastAPI backend. The full AI integration is being implemented.",
        "action": None,
        "meeting_info": None
    }

@app.get("/api/v1/calendar/status")
async def calendar_status():
    """Get calendar service status"""
    return {
        "success": True,
        "message": "Calendar service available (placeholder)"
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.now()}

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "127.0.0.1")
    debug = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    uvicorn.run(
        "main_simple:app",
        host=host,
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )
