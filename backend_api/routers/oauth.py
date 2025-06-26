"""
OAuth Router for TailorTalk API
Handles Google OAuth 2.0 authentication flow
"""

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
import os
import json
import secrets
import time
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

from models import (
    OAuthConfig, AuthURLResponse, TokenRequest, TokenResponse,
    TokenRefreshRequest, BaseResponse, ErrorResponse
)
from services.oauth_service import OAuthService
from services.token_service import TokenService

# Load environment variables
load_dotenv('../.env.local')

router = APIRouter()

# Initialize services
oauth_service = OAuthService()
token_service = TokenService()

@router.get("/config", response_model=OAuthConfig)
async def get_oauth_config():
    """Get OAuth configuration"""
    try:
        config = oauth_service.get_config()
        return OAuthConfig(
            client_id=config["client_id"],
            redirect_uri=config["redirect_uri"],
            scopes=config["scopes"],
            is_configured=oauth_service.is_configured()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get OAuth config: {str(e)}")

@router.get("/auth-url", response_model=AuthURLResponse)
async def generate_auth_url(request: Request):
    """Generate OAuth authorization URL"""
    try:
        if not oauth_service.is_configured():
            raise HTTPException(status_code=400, detail="OAuth not configured")
        
        auth_url, state = oauth_service.generate_auth_url()
        
        # Store state in session (you might want to use Redis or database in production)
        # For now, we'll use a simple in-memory store
        oauth_service.store_state(state)
        
        return AuthURLResponse(auth_url=auth_url, state=state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@router.post("/token", response_model=TokenResponse)
async def exchange_token(token_request: TokenRequest):
    """Exchange authorization code for access token"""
    try:
        if not oauth_service.is_configured():
            raise HTTPException(status_code=400, detail="OAuth not configured")
        
        # Verify state
        if not oauth_service.verify_state(token_request.state):
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Exchange code for tokens
        tokens = oauth_service.exchange_code_for_tokens(token_request.code, token_request.state)
        
        if not tokens:
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            expires_at=tokens.get("expires_at"),
            token_type=tokens.get("token_type", "Bearer"),
            user_info=tokens.get("user_info")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {str(e)}")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: TokenRefreshRequest):
    """Refresh access token using refresh token"""
    try:
        if not oauth_service.is_configured():
            raise HTTPException(status_code=400, detail="OAuth not configured")
        
        new_tokens = oauth_service.refresh_access_token(refresh_request.refresh_token)
        
        if not new_tokens:
            raise HTTPException(status_code=400, detail="Failed to refresh token")
        
        return TokenResponse(
            access_token=new_tokens["access_token"],
            refresh_token=new_tokens.get("refresh_token"),
            expires_at=new_tokens.get("expires_at"),
            token_type=new_tokens.get("token_type", "Bearer"),
            user_info=new_tokens.get("user_info")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")

@router.post("/revoke", response_model=BaseResponse)
async def revoke_token(token: str):
    """Revoke access token"""
    try:
        success = oauth_service.revoke_token(token)
        
        if success:
            return BaseResponse(success=True, message="Token revoked successfully")
        else:
            raise HTTPException(status_code=400, detail="Failed to revoke token")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token revocation failed: {str(e)}")

@router.get("/callback")
async def oauth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle OAuth callback from Google"""
    try:
        if error:
            # OAuth error occurred
            return RedirectResponse(
                url=f"{oauth_service.get_frontend_url()}?error={error}",
                status_code=302
            )
        
        if not code or not state:
            return RedirectResponse(
                url=f"{oauth_service.get_frontend_url()}?error=missing_parameters",
                status_code=302
            )
        
        # Verify state
        if not oauth_service.verify_state(state):
            return RedirectResponse(
                url=f"{oauth_service.get_frontend_url()}?error=invalid_state",
                status_code=302
            )
        
        # Exchange code for tokens
        tokens = oauth_service.exchange_code_for_tokens(code, state)

        if tokens:
            # Store tokens temporarily with a session ID
            import secrets
            session_id = secrets.token_urlsafe(32)
            token_service.store_tokens(session_id, tokens)

            # Redirect to frontend with session ID
            return RedirectResponse(
                url=f"{oauth_service.get_frontend_url()}?session_id={session_id}&success=true",
                status_code=302
            )
        else:
            return RedirectResponse(
                url=f"{oauth_service.get_frontend_url()}?error=token_exchange_failed",
                status_code=302
            )
    except Exception as e:
        return RedirectResponse(
            url=f"{oauth_service.get_frontend_url()}?error=callback_error",
            status_code=302
        )

@router.get("/tokens/{session_id}", response_model=TokenResponse)
async def get_tokens_by_session(session_id: str):
    """Retrieve tokens by session ID"""
    try:
        tokens = token_service.retrieve_tokens(session_id)
        if not tokens:
            raise HTTPException(status_code=404, detail="Session not found or expired")

        # Clean up the session after retrieval
        token_service.delete_tokens(session_id)

        return TokenResponse(
            access_token=tokens['access_token'],
            refresh_token=tokens.get('refresh_token'),
            expires_at=tokens.get('expires_at'),
            token_type=tokens.get('token_type', 'Bearer'),
            user_info=tokens.get('user_info', {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tokens: {str(e)}")

@router.get("/user-info")
async def get_user_info(access_token: str):
    """Get user information from Google"""
    try:
        user_info = oauth_service.get_user_info(access_token)
        
        if user_info:
            return user_info
        else:
            raise HTTPException(status_code=400, detail="Failed to get user info")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

@router.get("/status", response_model=BaseResponse)
async def oauth_status():
    """Get OAuth service status"""
    try:
        is_configured = oauth_service.is_configured()
        return BaseResponse(
            success=is_configured,
            message="OAuth configured" if is_configured else "OAuth not configured"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get OAuth status: {str(e)}")
