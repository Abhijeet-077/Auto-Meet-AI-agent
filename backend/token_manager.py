import os
import json
import base64
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import streamlit as st

class TokenManager:
    """Secure token management for OAuth tokens"""
    
    def __init__(self):
        """Initialize token manager with encryption"""
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key) if self.encryption_key else None
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """Generate or retrieve encryption key"""
        try:
            # Try to get from Streamlit secrets
            if hasattr(st, 'secrets') and 'encryption_key' in st.secrets:
                key_string = st.secrets['encryption_key']
                return base64.urlsafe_b64decode(key_string.encode())
        except:
            pass
        
        # For development, use a derived key from session
        # In production, this should be a proper secret
        password = os.getenv('TOKEN_ENCRYPTION_PASSWORD', 'default-dev-password').encode()
        salt = b'tailortalk-salt'  # In production, use a random salt stored securely
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encrypt_tokens(self, tokens: Dict[str, Any]) -> Optional[str]:
        """Encrypt OAuth tokens for secure storage"""
        if not self.cipher:
            return None
        
        try:
            token_json = json.dumps(tokens)
            encrypted_data = self.cipher.encrypt(token_json.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            st.error(f"Error encrypting tokens: {str(e)}")
            return None
    
    def decrypt_tokens(self, encrypted_tokens: str) -> Optional[Dict[str, Any]]:
        """Decrypt OAuth tokens from secure storage"""
        if not self.cipher:
            return None
        
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_tokens.encode())
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            st.error(f"Error decrypting tokens: {str(e)}")
            return None
    
    def store_tokens_securely(self, tokens: Dict[str, Any]) -> bool:
        """Store tokens securely in session state"""
        encrypted_tokens = self.encrypt_tokens(tokens)
        if encrypted_tokens:
            st.session_state.encrypted_google_tokens = encrypted_tokens
            return True
        return False
    
    def retrieve_tokens_securely(self) -> Optional[Dict[str, Any]]:
        """Retrieve tokens securely from session state"""
        encrypted_tokens = st.session_state.get('encrypted_google_tokens')
        if encrypted_tokens:
            return self.decrypt_tokens(encrypted_tokens)
        return None
    
    def clear_tokens(self):
        """Clear all stored tokens"""
        if 'encrypted_google_tokens' in st.session_state:
            del st.session_state.encrypted_google_tokens
        if 'google_tokens' in st.session_state:
            del st.session_state.google_tokens
    
    def is_token_valid(self, tokens: Dict[str, Any]) -> bool:
        """Check if tokens are still valid"""
        if not tokens:
            return False
        
        # Check if access token exists
        if 'access_token' not in tokens:
            return False
        
        # Check expiration if available
        if 'expires_at' in tokens:
            import time
            return time.time() < tokens['expires_at']
        
        # If no expiration info, assume valid for now
        return True
    
    def refresh_tokens_if_needed(self, tokens: Dict[str, Any], oauth_handler) -> Optional[Dict[str, Any]]:
        """Refresh tokens if they're expired"""
        if not self.is_token_valid(tokens) and 'refresh_token' in tokens:
            # Try to refresh
            new_tokens = oauth_handler.refresh_access_token(tokens['refresh_token'])
            if new_tokens:
                # Merge with existing tokens (keep refresh_token and user_info)
                updated_tokens = tokens.copy()
                updated_tokens.update(new_tokens)
                
                # Store updated tokens
                self.store_tokens_securely(updated_tokens)
                return updated_tokens
        
        return tokens if self.is_token_valid(tokens) else None
