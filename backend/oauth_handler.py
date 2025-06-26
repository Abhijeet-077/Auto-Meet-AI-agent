import os
import json
import base64
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode, parse_qs
import streamlit as st
import requests
from dotenv import load_dotenv
from .token_manager import TokenManager

# Load environment variables
load_dotenv('.env.local')

class GoogleOAuthHandler:
    """Handle Google OAuth 2.0 flow for Streamlit applications"""
    
    def __init__(self):
        """Initialize OAuth handler with configuration"""
        self.client_id = self._get_client_id()
        self.client_secret = self._get_client_secret()
        self.redirect_uri = self._get_redirect_uri()
        self.token_manager = TokenManager()
        self.scopes = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        
    def _get_client_id(self) -> str:
        """Get Google OAuth Client ID"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth']['client_id']
        except:
            pass
        return os.getenv('GOOGLE_CLIENT_ID', '')
    
    def _get_client_secret(self) -> str:
        """Get Google OAuth Client Secret"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth']['client_secret']
        except:
            pass
        return os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    def _get_redirect_uri(self) -> str:
        """Get OAuth redirect URI"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth'].get('redirect_uri', 'http://localhost:8501')
        except:
            pass
        return os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8501')
    
    def is_configured(self) -> bool:
        """Check if OAuth is properly configured"""
        return bool(self.client_id and self.client_secret)
    
    def generate_auth_url(self) -> Tuple[str, str]:
        """Generate OAuth authorization URL and state"""
        if not self.is_configured():
            raise ValueError("OAuth not configured. Missing client_id or client_secret.")
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state in session
        st.session_state.oauth_state = state
        
        # OAuth parameters
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return auth_url, state
    
    def exchange_code_for_tokens(self, auth_code: str, state: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access tokens"""
        if not self.is_configured():
            return None
        
        # Verify state to prevent CSRF attacks
        if state != st.session_state.get('oauth_state'):
            st.error("Invalid state parameter. Possible CSRF attack.")
            return None
        
        # Token exchange parameters
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            # Exchange code for tokens
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                tokens = response.json()
                
                # Get user info
                user_info = self._get_user_info(tokens['access_token'])
                if user_info:
                    tokens['user_info'] = user_info
                
                return tokens
            else:
                st.error(f"Token exchange failed: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error during token exchange: {str(e)}")
            return None
    
    def _get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information using access token"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            st.error(f"Error getting user info: {str(e)}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
        if not self.is_configured():
            return None
        
        refresh_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data=refresh_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            st.error(f"Error refreshing token: {str(e)}")
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke access token"""
        try:
            response = requests.post(
                f'https://oauth2.googleapis.com/revoke?token={token}'
            )
            return response.status_code == 200
        except:
            return False
    
    def handle_oauth_callback(self) -> bool:
        """Handle OAuth callback from URL parameters"""
        # Check for authorization code in URL parameters
        try:
            query_params = st.query_params

            if 'code' in query_params and 'state' in query_params:
                auth_code = query_params['code']
                state = query_params['state']

                # Exchange code for tokens
                tokens = self.exchange_code_for_tokens(auth_code, state)

                if tokens:
                    # Store tokens securely using token manager
                    self.token_manager.store_tokens_securely(tokens)
                    st.session_state.google_tokens = tokens
                    st.session_state.google_calendar_connected = True
                    st.session_state.google_user_info = tokens.get('user_info', {})

                    # Clear URL parameters
                    st.query_params.clear()

                    return True
        except Exception as e:
            st.error(f"Error handling OAuth callback: {str(e)}")

        return False
