"""
Token Service for TailorTalk API
Migrated from backend/token_manager.py to work with FastAPI
"""

import os
import json
import base64
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env.local')

class TokenService:
    """Secure token management for OAuth tokens"""
    
    def __init__(self):
        """Initialize token service with encryption"""
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key) if self.encryption_key else None
        
        # In-memory token storage (use Redis/database in production)
        self._token_store = {}
    
    def _get_encryption_key(self) -> Optional[str]:
        """Get or generate encryption key"""
        key_str = os.getenv('ENCRYPTION_KEY', '')

        if not key_str or key_str == 'your_encryption_key_here':
            return None

        try:
            # If it's a base64 encoded key, return it as-is (Fernet expects base64 string)
            if len(key_str) == 44 and key_str.endswith('='):
                # Validate it's a proper base64 key by trying to decode it
                base64.urlsafe_b64decode(key_str.encode())
                return key_str

            # Otherwise, derive key from string
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'tailortalk_salt',
                iterations=100000,
            )
            derived_key = kdf.derive(key_str.encode())
            return base64.urlsafe_b64encode(derived_key).decode()
        except Exception as e:
            # If all else fails, generate a simple key from the string
            try:
                # Pad or truncate to 32 bytes
                key_bytes = key_str.encode('utf-8')
                if len(key_bytes) < 32:
                    key_bytes = key_bytes + b'0' * (32 - len(key_bytes))
                else:
                    key_bytes = key_bytes[:32]
                return base64.urlsafe_b64encode(key_bytes).decode()
            except:
                return None
    
    def encrypt_tokens(self, tokens: Dict[str, Any]) -> Optional[str]:
        """Encrypt OAuth tokens for secure storage"""
        if not self.cipher:
            return None
        
        try:
            token_json = json.dumps(tokens)
            encrypted_data = self.cipher.encrypt(token_json.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception:
            return None
    
    def decrypt_tokens(self, encrypted_tokens: str) -> Optional[Dict[str, Any]]:
        """Decrypt OAuth tokens from secure storage"""
        if not self.cipher:
            return None
        
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_tokens.encode())
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception:
            return None
    
    def store_tokens(self, user_id: str, tokens: Dict[str, Any]) -> bool:
        """Store tokens securely for a user"""
        encrypted_tokens = self.encrypt_tokens(tokens)
        if encrypted_tokens:
            self._token_store[user_id] = encrypted_tokens
            return True
        return False
    
    def retrieve_tokens(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve tokens securely for a user"""
        encrypted_tokens = self._token_store.get(user_id)
        if encrypted_tokens:
            return self.decrypt_tokens(encrypted_tokens)
        return None
    
    def clear_tokens(self, user_id: str):
        """Clear stored tokens for a user"""
        if user_id in self._token_store:
            del self._token_store[user_id]

    def delete_tokens(self, user_id: str):
        """Delete stored tokens for a user (alias for clear_tokens)"""
        self.clear_tokens(user_id)
    
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
    
    def refresh_tokens_if_needed(self, user_id: str, oauth_service) -> Optional[Dict[str, Any]]:
        """Refresh tokens if they're expired"""
        tokens = self.retrieve_tokens(user_id)
        
        if not tokens:
            return None
        
        if not self.is_token_valid(tokens) and 'refresh_token' in tokens:
            # Try to refresh
            new_tokens = oauth_service.refresh_access_token(tokens['refresh_token'])
            if new_tokens:
                # Merge with existing tokens (keep refresh_token and user_info)
                updated_tokens = tokens.copy()
                updated_tokens.update(new_tokens)
                
                # Store updated tokens
                self.store_tokens(user_id, updated_tokens)
                return updated_tokens
        
        return tokens if self.is_token_valid(tokens) else None
    
    def get_user_id_from_token(self, access_token: str) -> Optional[str]:
        """Get user ID from access token (for session management)"""
        # In a real implementation, you might decode the token or call Google API
        # For now, we'll use a simple hash of the token
        import hashlib
        return hashlib.md5(access_token.encode()).hexdigest()
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens from storage"""
        import time
        current_time = time.time()
        
        expired_users = []
        for user_id, encrypted_tokens in self._token_store.items():
            tokens = self.decrypt_tokens(encrypted_tokens)
            if tokens and 'expires_at' in tokens:
                if current_time > tokens['expires_at'] and 'refresh_token' not in tokens:
                    expired_users.append(user_id)
        
        for user_id in expired_users:
            del self._token_store[user_id]
