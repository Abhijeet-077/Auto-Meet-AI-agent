import os
import json
import base64
import hashlib
import secrets
import time
import glob
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode, parse_qs
import streamlit as st
import requests
from dotenv import load_dotenv
try:
    from .token_manager import TokenManager
except ImportError:
    from backend.token_manager import TokenManager

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
        self.scopes = self._get_scopes()
        
    def _get_client_id(self) -> str:
        """Get Google OAuth Client ID from environment or Streamlit secrets"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth']['client_id']
        except:
            pass
        client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        if not client_id or client_id == 'your_google_client_id_here':
            return ''
        return client_id

    def _get_client_secret(self) -> str:
        """Get Google OAuth Client Secret from environment or Streamlit secrets"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth']['client_secret']
        except:
            pass
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
        if not client_secret or client_secret in ['PLACEHOLDER_CLIENT_SECRET', 'your_google_client_secret_here']:
            return ''
        return client_secret

    def _get_redirect_uri(self) -> str:
        """Get OAuth redirect URI"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth'].get('redirect_uri', 'http://localhost:8501')
        except:
            pass
        # Check both OAUTH_REDIRECT_URI and GOOGLE_REDIRECT_URI for compatibility
        return os.getenv('OAUTH_REDIRECT_URI', os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8501'))

    def _get_scopes(self) -> list:
        """Get OAuth scopes from environment or use defaults"""
        try:
            scopes_str = os.getenv('OAUTH_SCOPES', '')
            if scopes_str:
                return [scope.strip() for scope in scopes_str.split(',')]
        except:
            pass
        return [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]

    def is_configured(self) -> bool:
        """Check if OAuth is properly configured"""
        return bool(self.client_id and self.client_secret)

    def get_configuration_status(self) -> Dict[str, Any]:
        """Get detailed configuration status for debugging"""
        return {
            'client_id_configured': bool(self.client_id),
            'client_secret_configured': bool(self.client_secret),
            'redirect_uri': self.redirect_uri,
            'scopes': self.scopes,
            'is_configured': self.is_configured(),
            'client_id_preview': f"{self.client_id[:20]}..." if self.client_id else "Not set"
        }
    
    def generate_auth_url(self) -> Tuple[str, str]:
        """Generate OAuth authorization URL and state"""
        if not self.is_configured():
            config_status = self.get_configuration_status()
            error_msg = f"OAuth not configured properly. Status: {config_status}"
            st.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Generate state for CSRF protection
            state = secrets.token_urlsafe(32)

            # Store state in session and also in a more persistent way
            st.session_state.oauth_state = state

            # Also store in a temporary file as backup (for session refresh issues)
            try:
                import tempfile
                import json
                temp_dir = tempfile.gettempdir()
                state_file = os.path.join(temp_dir, f"tailortalk_oauth_state_{state[:16]}.json")
                with open(state_file, 'w') as f:
                    json.dump({'state': state, 'timestamp': time.time()}, f)
            except Exception:
                pass  # Fallback to session state only

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

            # Debug logging in development
            if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                st.info(f"Generated auth URL with redirect_uri: {self.redirect_uri}")

            return auth_url, state

        except Exception as e:
            error_msg = f"Error generating auth URL: {str(e)}"
            st.error(error_msg)
            raise ValueError(error_msg)
    
    def exchange_code_for_tokens(self, auth_code: str, state: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access tokens"""
        if not self.is_configured():
            st.error("OAuth not configured for token exchange")
            return None

        # Verify state to prevent CSRF attacks
        stored_state = st.session_state.get('oauth_state')

        # If session state doesn't have the state, try to find it in temp files
        if not stored_state:
            try:
                import tempfile
                import glob
                temp_dir = tempfile.gettempdir()
                state_files = glob.glob(os.path.join(temp_dir, f"tailortalk_oauth_state_{state[:16]}.json"))

                for state_file in state_files:
                    try:
                        with open(state_file, 'r') as f:
                            state_data = json.load(f)
                            if state_data.get('state') == state:
                                # Check if state is not too old (max 10 minutes)
                                if time.time() - state_data.get('timestamp', 0) < 600:
                                    stored_state = state
                                    st.info("State recovered from temporary storage")
                                    # Clean up the temp file
                                    os.remove(state_file)
                                    break
                    except Exception:
                        continue
            except Exception:
                pass

        # Handle session state issues
        if state != stored_state:
            if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                st.warning(f"State mismatch - Expected: {stored_state}, Received: {state}")
                st.info("Proceeding with token exchange in debug mode...")
            else:
                st.error("Invalid state parameter. Possible CSRF attack or session expired.")
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

                # Add expiration timestamp if not present
                if 'expires_in' in tokens and 'expires_at' not in tokens:
                    import time
                    tokens['expires_at'] = time.time() + tokens['expires_in']

                # Get user info
                user_info = self._get_user_info(tokens['access_token'])
                if user_info:
                    tokens['user_info'] = user_info
                else:
                    st.warning("Could not retrieve user information")

                return tokens
            else:
                error_details = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                st.error(f"Token exchange failed (HTTP {response.status_code}): {error_details}")
                return None

        except requests.exceptions.Timeout:
            st.error("Token exchange timed out. Please try again.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Network error during token exchange: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error during token exchange: {str(e)}")
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

                if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                    st.info(f"Processing OAuth callback with state: {state}")

                # Exchange code for tokens
                tokens = self.exchange_code_for_tokens(auth_code, state)

                if tokens:
                    # Store tokens securely using token manager
                    success = self.token_manager.store_tokens_securely(tokens)
                    if success:
                        st.session_state.google_tokens = tokens
                        st.session_state.google_calendar_connected = True
                        st.session_state.google_user_info = tokens.get('user_info', {})

                        # Clear URL parameters
                        st.query_params.clear()

                        return True
                    else:
                        st.error("Failed to store tokens securely")
                        return False
                else:
                    st.error("Failed to exchange authorization code for tokens")
                    return False
        except Exception as e:
            st.error(f"Error handling OAuth callback: {str(e)}")

        return False
