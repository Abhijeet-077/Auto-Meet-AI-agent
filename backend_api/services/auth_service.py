"""
Authentication Service for TailorTalk API
Handles token validation and user authentication
"""

import os
from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, Header
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

class AuthService:
    """Authentication service for API requests"""
    
    def __init__(self):
        """Initialize auth service"""
        pass
    
    async def validate_access_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Validate Google access token and get user info"""
        try:
            # Validate token with Google
            response = requests.get(
                f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}',
                timeout=30
            )
            
            if response.status_code == 200:
                token_info = response.json()
                
                # Check if token is valid and has required scopes
                required_scopes = [
                    'https://www.googleapis.com/auth/calendar.readonly',
                    'https://www.googleapis.com/auth/calendar.events'
                ]
                
                token_scopes = token_info.get('scope', '').split()
                
                # Check if all required scopes are present
                has_required_scopes = all(scope in token_scopes for scope in required_scopes)
                
                if has_required_scopes:
                    return token_info
            
            return None
        except Exception:
            return None
    
    async def get_user_info_from_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from access token"""
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
        except Exception:
            return None

# Dependency functions
auth_service = AuthService()

async def get_current_user_tokens(authorization: Optional[str] = Header(None)) -> str:
    """Dependency to get and validate current user's access token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )
    
    access_token = authorization.split(" ")[1]
    
    # Validate token
    token_info = await auth_service.validate_access_token(access_token)
    if not token_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )
    
    return access_token

async def get_current_user_info(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Dependency to get current user information"""
    access_token = await get_current_user_tokens(authorization)
    
    user_info = await auth_service.get_user_info_from_token(access_token)
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Could not retrieve user information"
        )
    
    return user_info

async def optional_auth(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Optional authentication dependency"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    access_token = authorization.split(" ")[1]
    
    # Validate token
    token_info = await auth_service.validate_access_token(access_token)
    if not token_info:
        return None
    
    return access_token
