"""
OAuth Service for TailorTalk API
Migrated from backend/oauth_handler.py to work with FastAPI
"""

import os
import json
import secrets
import time
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env.local')

class OAuthService:
    """Handle Google OAuth 2.0 flow for FastAPI backend"""

    # Class-level state storage to persist across instances
    _global_state_store = {}

    def __init__(self):
        """Initialize OAuth service with configuration"""
        self.client_id = self._get_client_id()
        self.client_secret = self._get_client_secret()
        self.redirect_uri = self._get_redirect_uri()
        self.scopes = self._get_scopes()
        self.frontend_url = self._get_frontend_url()

        # Use class-level state storage
        self._state_store = OAuthService._global_state_store
        
    def _get_client_id(self) -> str:
        """Get Google OAuth Client ID from environment"""
        client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        if not client_id or client_id == 'your_google_client_id_here':
            return ''
        return client_id
    
    def _get_client_secret(self) -> str:
        """Get Google OAuth Client Secret from environment"""
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
        if not client_secret or client_secret == 'PLACEHOLDER_CLIENT_SECRET':
            return ''
        return client_secret
    
    def _get_redirect_uri(self) -> str:
        """Get OAuth redirect URI"""
        # For FastAPI backend, use the API callback endpoint
        base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        return f"{base_url}/api/v1/oauth/callback"
    
    def _get_scopes(self) -> list:
        """Get OAuth scopes"""
        scopes_str = os.getenv('OAUTH_SCOPES', 
            'https://www.googleapis.com/auth/calendar.readonly,'
            'https://www.googleapis.com/auth/calendar.events,'
            'https://www.googleapis.com/auth/userinfo.email,'
            'https://www.googleapis.com/auth/userinfo.profile'
        )
        return [scope.strip() for scope in scopes_str.split(',')]
    
    def _get_frontend_url(self) -> str:
        """Get frontend URL for redirects"""
        return os.getenv('FRONTEND_URL', 'http://localhost:8501')
    
    def is_configured(self) -> bool:
        """Check if OAuth is properly configured"""
        return bool(self.client_id and self.client_secret)
    
    def get_config(self) -> Dict[str, Any]:
        """Get OAuth configuration"""
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scopes": self.scopes,
            "is_configured": self.is_configured()
        }
    
    def get_frontend_url(self) -> str:
        """Get frontend URL"""
        return self.frontend_url
    
    def generate_auth_url(self) -> Tuple[str, str]:
        """Generate OAuth authorization URL"""
        if not self.is_configured():
            raise ValueError("OAuth not configured")
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
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
    
    def store_state(self, state: str):
        """Store OAuth state for verification"""
        state_data = {
            'timestamp': time.time(),
            'used': False
        }

        # Store in memory
        self._state_store[state] = state_data

        # Also store in file as backup
        try:
            import tempfile
            import json
            temp_dir = tempfile.gettempdir()
            state_file = os.path.join(temp_dir, f"oauth_state_{state[:16]}.json")
            with open(state_file, 'w') as f:
                json.dump({
                    'state': state,
                    'timestamp': state_data['timestamp'],
                    'used': state_data['used']
                }, f)
        except Exception:
            pass  # File backup is optional

        # Clean up old states (older than 1 hour)
        current_time = time.time()
        expired_states = [
            s for s, data in self._state_store.items()
            if current_time - data['timestamp'] > 3600
        ]
        for expired_state in expired_states:
            del self._state_store[expired_state]
    
    def verify_state(self, state: str) -> bool:
        """Verify OAuth state parameter"""
        state_data = None

        # First check in-memory store
        if state in self._state_store:
            state_data = self._state_store[state]
        else:
            # Try to recover from file backup
            try:
                import tempfile
                import json
                import glob
                temp_dir = tempfile.gettempdir()
                state_files = glob.glob(os.path.join(temp_dir, f"oauth_state_{state[:16]}.json"))

                for state_file in state_files:
                    try:
                        with open(state_file, 'r') as f:
                            file_data = json.load(f)
                            if file_data.get('state') == state:
                                state_data = {
                                    'timestamp': file_data.get('timestamp', 0),
                                    'used': file_data.get('used', False)
                                }
                                # Restore to memory
                                self._state_store[state] = state_data
                                break
                    except Exception:
                        continue
            except Exception:
                pass

        if not state_data:
            return False

        # Check if already used
        if state_data['used']:
            return False

        # Check if expired (1 hour)
        if time.time() - state_data['timestamp'] > 3600:
            if state in self._state_store:
                del self._state_store[state]
            return False

        # Mark as used
        state_data['used'] = True

        # Update file backup
        try:
            import tempfile
            import json
            temp_dir = tempfile.gettempdir()
            state_file = os.path.join(temp_dir, f"oauth_state_{state[:16]}.json")
            with open(state_file, 'w') as f:
                json.dump({
                    'state': state,
                    'timestamp': state_data['timestamp'],
                    'used': state_data['used']
                }, f)
        except Exception:
            pass

        return True
    
    def exchange_code_for_tokens(self, auth_code: str, state: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access tokens"""
        if not self.is_configured():
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
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                tokens = response.json()
                
                # Add expiration timestamp
                if 'expires_in' in tokens:
                    tokens['expires_at'] = int(time.time()) + tokens['expires_in']
                
                # Get user info
                if 'access_token' in tokens:
                    user_info = self.get_user_info(tokens['access_token'])
                    if user_info:
                        tokens['user_info'] = user_info
                
                return tokens
            else:
                return None
                
        except Exception:
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
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                tokens = response.json()
                
                # Add expiration timestamp
                if 'expires_in' in tokens:
                    tokens['expires_at'] = int(time.time()) + tokens['expires_in']
                
                return tokens
            else:
                return None
                
        except Exception:
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google"""
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception:
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke access token"""
        try:
            response = requests.post(
                f'https://oauth2.googleapis.com/revoke?token={token}',
                timeout=30
            )
            return response.status_code == 200
        except Exception:
            return False
