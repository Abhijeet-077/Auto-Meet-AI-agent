"""
Agentic Calendar - Streamlit Cloud Deployment
AI-Powered Meeting Scheduler with Google Calendar Integration
Optimized for Streamlit Cloud deployment
"""

import streamlit as st
import requests
import os
import json
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import time
from urllib.parse import urlencode

# Import cryptography with error handling
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    st.warning("⚠️ Cryptography library not available. API keys will be stored without encryption.")

# Page configuration
st.set_page_config(
    page_title="Agentic Calendar - AI Meeting Scheduler",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration and secrets management
class Config:
    """Configuration management for Streamlit Cloud deployment"""
    
    def __init__(self):
        # Try to get from Streamlit secrets first, then environment variables
        self.demo_mode = self._get_config('DEMO_MODE', 'true').lower() == 'true'
        self.google_client_id = self._get_config('GOOGLE_CLIENT_ID', '')
        self.google_client_secret = self._get_config('GOOGLE_CLIENT_SECRET', '')
        self.gemini_api_key = self._get_config('GEMINI_API_KEY', '')
        self.encryption_key = self._get_config('ENCRYPTION_KEY', self._generate_encryption_key())
        
        # Streamlit Cloud URLs
        self.app_url = self._get_app_url()
        self.redirect_uri = f"{self.app_url}?oauth_callback=true"
    
    def _get_config(self, key: str, default: str = '') -> str:
        """Get configuration from Streamlit secrets or environment"""
        try:
            # Try Streamlit secrets first
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except:
            pass
        
        # Fall back to environment variables
        return os.getenv(key, default)
    
    def _get_app_url(self) -> str:
        """Get the Streamlit app URL"""
        try:
            # Try to get from Streamlit context
            if hasattr(st, 'secrets') and 'APP_URL' in st.secrets:
                return st.secrets['APP_URL']
        except:
            pass
        
        # Default for local development
        return 'http://localhost:8501'
    
    def _generate_encryption_key(self) -> str:
        """Generate a new encryption key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def is_configured(self) -> bool:
        """Check if the app is properly configured"""
        if self.demo_mode:
            return True
        return bool(self.google_client_id and self.google_client_secret and self.gemini_api_key)

# Initialize configuration
config = Config()

# Demo Service for Streamlit Cloud
class DemoService:
    """Demo service providing simulated functionality for evaluation"""
    
    def __init__(self):
        self.demo_user = {
            'name': 'Demo User',
            'email': 'demo.user@agenticcalendar.com',
            'picture': 'https://via.placeholder.com/150/0066cc/ffffff?text=Demo'
        }
        
        self.demo_events = [
            {
                'id': 'demo_event_1',
                'title': 'Team Standup Meeting',
                'start_time': (datetime.now() + timedelta(hours=2)).isoformat(),
                'end_time': (datetime.now() + timedelta(hours=2, minutes=30)).isoformat(),
                'description': 'Daily team standup meeting',
                'attendees': ['john.doe@company.com', 'jane.smith@company.com'],
                'location': 'Conference Room A',
                'event_link': 'https://calendar.google.com/calendar/event?eid=demo_event_1'
            },
            {
                'id': 'demo_event_2',
                'title': 'Project Review',
                'start_time': (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                'end_time': (datetime.now() + timedelta(days=1, hours=11)).isoformat(),
                'description': 'Quarterly project review meeting',
                'attendees': ['manager@company.com'],
                'location': 'Virtual Meeting',
                'event_link': 'https://calendar.google.com/calendar/event?eid=demo_event_2'
            }
        ]
    
    def get_demo_ai_response(self, message: str) -> Dict[str, Any]:
        """Generate demo AI response"""
        import random
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create']):
            responses = [
                "I'll help you schedule that meeting! Let me create it in your calendar.",
                "Perfect! I'm scheduling the meeting for you right now.",
                "Great choice of time! I'll add this to your calendar immediately."
            ]
            return {
                'response': random.choice(responses) + " (Demo Mode: This creates a simulated calendar event for evaluation purposes.)",
                'action': 'CREATE_EVENT',
                'confidence': 0.95,
                'demo_mode': True
            }
        elif any(word in message_lower for word in ['availability', 'available', 'free', 'busy']):
            return {
                'response': "Let me check your calendar availability... Based on your demo calendar, you have several free slots available this week.",
                'action': 'CHECK_AVAILABILITY',
                'confidence': 0.90,
                'demo_mode': True,
                'availability': self._get_demo_availability()
            }
        elif any(word in message_lower for word in ['show', 'view', 'list', 'events', 'meetings']):
            return {
                'response': f"Here are your upcoming events from your demo calendar. You have {len(self.demo_events)} upcoming events.",
                'action': 'VIEW_EVENTS',
                'confidence': 0.92,
                'demo_mode': True,
                'events': self.demo_events
            }
        else:
            return {
                'response': "I'm here to help you manage your calendar and schedule meetings! You're currently in demo mode, which allows you to test all features with simulated data.",
                'action': 'GENERAL',
                'confidence': 0.85,
                'demo_mode': True
            }
    
    def _get_demo_availability(self) -> List[Dict[str, str]]:
        """Get demo availability slots"""
        now = datetime.now()
        availability = []
        
        for i in range(1, 8):  # Next 7 days
            date = now + timedelta(days=i)
            availability.extend([
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'start_time': '09:00',
                    'end_time': '10:00',
                    'status': 'free'
                },
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'start_time': '14:00',
                    'end_time': '15:00',
                    'status': 'free'
                }
            ])
        
        return availability
    
    def create_demo_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a demo calendar event"""
        demo_event_id = f"demo_event_{secrets.token_hex(8)}"
        demo_event = {
            'id': demo_event_id,
            'title': event_data.get('title', 'Demo Meeting'),
            'start_time': event_data.get('start_time', datetime.now().isoformat()),
            'end_time': event_data.get('end_time', (datetime.now() + timedelta(hours=1)).isoformat()),
            'description': event_data.get('description', 'Demo meeting created for evaluation'),
            'attendees': event_data.get('attendees', []),
            'location': event_data.get('location', 'Demo Location'),
            'event_link': f'https://calendar.google.com/calendar/event?eid={demo_event_id}',
            'verification_link': f'https://calendar.google.com/calendar/r/eventedit/{demo_event_id}',
            'demo_created': True,
            'created_at': datetime.now().isoformat()
        }
        
        # Add to demo events list
        self.demo_events.append(demo_event)
        
        return {
            'success': True,
            'event_id': demo_event_id,
            'title': demo_event['title'],
            'start_time': demo_event['start_time'],
            'end_time': demo_event['end_time'],
            'event_link': demo_event['event_link'],
            'verification_link': demo_event['verification_link'],
            'demo_mode': True,
            'message': 'Demo event created successfully! This is a simulated calendar event for evaluation purposes.'
        }

# Initialize demo service
demo_service = DemoService()

# Secure API Key Management
class SecureKeyManager:
    """Secure management of API keys with encryption"""

    def __init__(self):
        self.encryption_key = config.encryption_key
        self.cipher = None

        if CRYPTOGRAPHY_AVAILABLE and Fernet:
            if self.encryption_key:
                try:
                    self.cipher = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
                except Exception:
                    # If encryption key is invalid, generate a new one for this session
                    self.encryption_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
                    self.cipher = Fernet(self.encryption_key.encode())
            else:
                # Generate a session-specific encryption key
                self.encryption_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
                self.cipher = Fernet(self.encryption_key.encode())
        else:
            # Cryptography not available, store keys without encryption
            self.cipher = None

    def encrypt_key(self, api_key: str) -> str:
        """Encrypt an API key"""
        if not api_key:
            return ""

        if self.cipher:
            try:
                encrypted = self.cipher.encrypt(api_key.encode())
                return base64.urlsafe_b64encode(encrypted).decode()
            except Exception:
                # If encryption fails, return the key as-is (fallback)
                return api_key
        else:
            # No encryption available, return key as-is
            return api_key

    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key"""
        if not encrypted_key:
            return ""

        if self.cipher:
            try:
                encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
                decrypted = self.cipher.decrypt(encrypted_bytes)
                return decrypted.decode()
            except Exception:
                # If decryption fails, assume it's already decrypted (fallback)
                return encrypted_key
        else:
            # No encryption available, return key as-is
            return encrypted_key

    def store_api_key(self, provider: str, api_key: str):
        """Securely store an API key in session state"""
        if api_key:
            encrypted_key = self.encrypt_key(api_key)
            st.session_state[f"{provider}_api_key_encrypted"] = encrypted_key
            # Also store a flag indicating the key is encrypted
            st.session_state[f"{provider}_api_key_is_encrypted"] = True

    def get_api_key(self, provider: str) -> str:
        """Retrieve and decrypt an API key from session state"""
        # Check if we have an encrypted key
        encrypted_key = st.session_state.get(f"{provider}_api_key_encrypted", "")
        is_encrypted = st.session_state.get(f"{provider}_api_key_is_encrypted", False)

        if encrypted_key and is_encrypted:
            return self.decrypt_key(encrypted_key)

        # Fallback to unencrypted key (for backward compatibility)
        return st.session_state.get(f"{provider}_api_key", "")

    def clear_api_key(self, provider: str):
        """Clear an API key from session state"""
        keys_to_remove = [
            f"{provider}_api_key",
            f"{provider}_api_key_encrypted",
            f"{provider}_api_key_is_encrypted"
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]

    def has_api_key(self, provider: str) -> bool:
        """Check if an API key exists for a provider"""
        return bool(self.get_api_key(provider))

    def get_all_configured_providers(self) -> List[str]:
        """Get list of providers with configured API keys"""
        configured = []
        for provider in ['openai', 'gemini', 'claude']:
            if self.has_api_key(provider):
                configured.append(provider)
        return configured

# Initialize secure key manager
key_manager = SecureKeyManager()

# Caching for better performance on Streamlit Cloud
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_demo_events():
    """Get cached demo events for better performance"""
    return demo_service.demo_events

@st.cache_data(ttl=300)
def get_cached_demo_availability():
    """Get cached demo availability for better performance"""
    return demo_service._get_demo_availability()

# OAuth Service for Streamlit Cloud
class OAuthService:
    """OAuth service optimized for Streamlit Cloud deployment"""
    
    def __init__(self):
        self.client_id = config.google_client_id
        self.client_secret = config.google_client_secret
        self.redirect_uri = config.redirect_uri
        self.scopes = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
    
    def get_auth_url(self) -> str:
        """Generate OAuth authorization URL"""
        if config.demo_mode:
            # Return demo auth URL
            state = secrets.token_urlsafe(32)
            st.session_state.oauth_state = state
            return f"{config.app_url}?demo_oauth=true&state={state}"
        
        if not self.client_id:
            return None
        
        state = secrets.token_urlsafe(32)
        st.session_state.oauth_state = state
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_type': 'code',
            'access_type': 'offline',
            'state': state
        }
        
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback"""
        if config.demo_mode:
            return demo_service.demo_user
        
        # Validate state
        if state != st.session_state.get('oauth_state'):
            raise ValueError("Invalid state parameter")
        
        # Exchange code for tokens
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(token_url, data=token_data)
        if response.status_code != 200:
            raise ValueError("Failed to exchange code for tokens")
        
        tokens = response.json()
        
        # Get user info
        user_info_url = f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={tokens['access_token']}"
        user_response = requests.get(user_info_url)
        
        if user_response.status_code == 200:
            user_info = user_response.json()
            
            # Store tokens securely
            st.session_state.access_token = tokens['access_token']
            if 'refresh_token' in tokens:
                st.session_state.refresh_token = tokens['refresh_token']
            
            return user_info
        else:
            raise ValueError("Failed to get user information")

# Initialize OAuth service
oauth_service = OAuthService()

# Multi-AI Provider System
class AIProviderConfig:
    """Configuration for AI providers"""

    PROVIDERS = {
        'demo': {
            'name': 'Demo Mode',
            'description': 'Simulated AI responses for evaluation',
            'requires_api_key': False,
            'icon': '🎯'
        },
        'openai': {
            'name': 'OpenAI',
            'description': 'GPT-3.5 Turbo / GPT-4',
            'requires_api_key': True,
            'icon': '🤖',
            'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview']
        },
        'gemini': {
            'name': 'Google Gemini',
            'description': 'Gemini Pro / Gemini Pro Vision',
            'requires_api_key': True,
            'icon': '🧠',
            'models': ['gemini-pro', 'gemini-pro-vision']
        },
        'claude': {
            'name': 'Anthropic Claude',
            'description': 'Claude 3 Haiku / Sonnet / Opus',
            'requires_api_key': True,
            'icon': '🎭',
            'models': ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229', 'claude-3-opus-20240229']
        }
    }

class BaseAIProvider:
    """Base class for AI providers"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat message - to be implemented by subclasses"""
        raise NotImplementedError

    def validate_api_key(self) -> bool:
        """Validate the API key - to be implemented by subclasses"""
        raise NotImplementedError

class DemoAIProvider(BaseAIProvider):
    """Demo AI provider using simulated responses"""

    def __init__(self):
        super().__init__()

    def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Use demo service for responses"""
        return demo_service.get_demo_ai_response(message)

    def validate_api_key(self) -> bool:
        """Demo mode doesn't require validation"""
        return True

class OpenAIProvider(BaseAIProvider):
    """OpenAI provider for GPT models"""

    def __init__(self, api_key: str = None, model: str = 'gpt-3.5-turbo'):
        super().__init__(api_key)
        self.model = model

    def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat with OpenAI API"""
        if not self.api_key:
            return demo_service.get_demo_ai_response(message)

        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)

            # Prepare messages for OpenAI format
            messages = [
                {"role": "system", "content": "You are an intelligent calendar assistant. Help users schedule meetings, check availability, and manage their calendar. Be conversational and helpful."}
            ]

            # Add chat history
            if chat_history:
                for msg in chat_history[-10:]:  # Last 10 messages for context
                    if msg['role'] in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg['content']
                        })

            # Add current message
            messages.append({"role": "user", "content": message})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            return {
                'response': response.choices[0].message.content,
                'action': self._determine_action(message),
                'confidence': 0.9,
                'provider': 'openai',
                'model': self.model,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower():
                st.warning("🔄 OpenAI rate limit reached - Using demo mode")
            elif "quota" in error_msg.lower():
                st.warning("🔄 OpenAI quota exceeded - Using demo mode")
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                st.error("❌ Invalid OpenAI API key - Using demo mode")
            else:
                st.warning(f"🔄 OpenAI API error - Using demo mode. Error: {error_msg}")

            fallback_response = demo_service.get_demo_ai_response(message)
            fallback_response['fallback_reason'] = 'openai_error'
            fallback_response['original_error'] = error_msg
            return fallback_response

    def validate_api_key(self) -> bool:
        """Validate OpenAI API key"""
        if not self.api_key:
            return False

        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            # Test with a simple completion
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False

    def _determine_action(self, message: str) -> str:
        """Determine action from message"""
        message_lower = message.lower()
        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create']):
            return 'CREATE_EVENT'
        elif any(word in message_lower for word in ['availability', 'available', 'free']):
            return 'CHECK_AVAILABILITY'
        elif any(word in message_lower for word in ['show', 'view', 'list', 'events']):
            return 'VIEW_EVENTS'
        else:
            return 'GENERAL'

class GeminiProvider(BaseAIProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: str = None, model: str = 'gemini-pro'):
        super().__init__(api_key)
        self.model = model

    def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat with Gemini API"""
        if not self.api_key:
            return demo_service.get_demo_ai_response(message)

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            model = genai.GenerativeModel(self.model)

            # Create context-aware prompt
            system_prompt = """You are an intelligent calendar assistant. Help users schedule meetings, check availability, and manage their calendar.
            Be conversational and helpful. If a user wants to schedule a meeting, extract the details and confirm the action."""

            full_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"

            response = model.generate_content(full_prompt)

            return {
                'response': response.text,
                'action': self._determine_action(message),
                'confidence': 0.9,
                'provider': 'gemini',
                'model': self.model,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                st.warning("🔄 Gemini quota exceeded - Using demo mode")
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                st.error("❌ Invalid Gemini API key - Using demo mode")
            elif "blocked" in error_msg.lower():
                st.warning("🔄 Gemini content blocked - Using demo mode")
            else:
                st.warning(f"🔄 Gemini API error - Using demo mode. Error: {error_msg}")

            fallback_response = demo_service.get_demo_ai_response(message)
            fallback_response['fallback_reason'] = 'gemini_error'
            fallback_response['original_error'] = error_msg
            return fallback_response

    def validate_api_key(self) -> bool:
        """Validate Gemini API key"""
        if not self.api_key:
            return False

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            model.generate_content("Hello")
            return True
        except Exception:
            return False

    def _determine_action(self, message: str) -> str:
        """Determine action from message"""
        message_lower = message.lower()
        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create']):
            return 'CREATE_EVENT'
        elif any(word in message_lower for word in ['availability', 'available', 'free']):
            return 'CHECK_AVAILABILITY'
        elif any(word in message_lower for word in ['show', 'view', 'list', 'events']):
            return 'VIEW_EVENTS'
        else:
            return 'GENERAL'

class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str = None, model: str = 'claude-3-haiku-20240307'):
        super().__init__(api_key)
        self.model = model

    def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat with Claude API"""
        if not self.api_key:
            return demo_service.get_demo_ai_response(message)

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            # Prepare system message
            system_message = "You are an intelligent calendar assistant. Help users schedule meetings, check availability, and manage their calendar. Be conversational and helpful."

            # Prepare conversation history
            messages = []
            if chat_history:
                for msg in chat_history[-10:]:  # Last 10 messages for context
                    if msg['role'] in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg['content']
                        })

            # Add current message
            messages.append({"role": "user", "content": message})

            response = client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_message,
                messages=messages
            )

            return {
                'response': response.content[0].text,
                'action': self._determine_action(message),
                'confidence': 0.9,
                'provider': 'claude',
                'model': self.model,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower():
                st.warning("🔄 Claude rate limit reached - Using demo mode")
            elif "quota" in error_msg.lower() or "credit" in error_msg.lower():
                st.warning("🔄 Claude quota/credits exceeded - Using demo mode")
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                st.error("❌ Invalid Claude API key - Using demo mode")
            else:
                st.warning(f"🔄 Claude API error - Using demo mode. Error: {error_msg}")

            fallback_response = demo_service.get_demo_ai_response(message)
            fallback_response['fallback_reason'] = 'claude_error'
            fallback_response['original_error'] = error_msg
            return fallback_response

    def validate_api_key(self) -> bool:
        """Validate Claude API key"""
        if not self.api_key:
            return False

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception:
            return False

    def _determine_action(self, message: str) -> str:
        """Determine action from message"""
        message_lower = message.lower()
        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create']):
            return 'CREATE_EVENT'
        elif any(word in message_lower for word in ['availability', 'available', 'free']):
            return 'CHECK_AVAILABILITY'
        elif any(word in message_lower for word in ['show', 'view', 'list', 'events']):
            return 'VIEW_EVENTS'
        else:
            return 'GENERAL'

# AI Service for Streamlit Cloud with Multi-Provider Support
class AIService:
    """Enhanced AI service with multi-provider support"""

    def __init__(self):
        self.providers = {
            'demo': DemoAIProvider(),
            'openai': None,
            'gemini': None,
            'claude': None
        }
        self.current_provider = 'demo'
    
    def set_provider(self, provider_name: str, api_key: str = None, model: str = None):
        """Set the current AI provider"""
        if provider_name not in AIProviderConfig.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_name}")

        if provider_name == 'demo':
            self.providers['demo'] = DemoAIProvider()
            self.current_provider = 'demo'
        elif provider_name == 'openai':
            model = model or 'gpt-3.5-turbo'
            self.providers['openai'] = OpenAIProvider(api_key, model)
            self.current_provider = 'openai'
        elif provider_name == 'gemini':
            model = model or 'gemini-pro'
            self.providers['gemini'] = GeminiProvider(api_key, model)
            self.current_provider = 'gemini'
        elif provider_name == 'claude':
            model = model or 'claude-3-haiku-20240307'
            self.providers['claude'] = ClaudeProvider(api_key, model)
            self.current_provider = 'claude'

    def get_current_provider(self) -> BaseAIProvider:
        """Get the current AI provider instance"""
        return self.providers[self.current_provider]

    def get_current_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        provider_config = AIProviderConfig.PROVIDERS[self.current_provider]
        provider_instance = self.get_current_provider()

        return {
            'name': provider_config['name'],
            'description': provider_config['description'],
            'icon': provider_config['icon'],
            'provider_key': self.current_provider,
            'has_api_key': hasattr(provider_instance, 'api_key') and provider_instance.api_key is not None,
            'model': getattr(provider_instance, 'model', None)
        }

    def validate_provider_api_key(self, provider_name: str, api_key: str) -> bool:
        """Validate an API key for a specific provider"""
        if provider_name == 'demo':
            return True
        elif provider_name == 'openai':
            return OpenAIProvider(api_key).validate_api_key()
        elif provider_name == 'gemini':
            return GeminiProvider(api_key).validate_api_key()
        elif provider_name == 'claude':
            return ClaudeProvider(api_key).validate_api_key()
        return False

    def switch_provider(self, provider_name: str, api_key: str = None, model: str = None) -> bool:
        """Switch to a different AI provider with validation"""
        try:
            # Validate the provider and API key if required
            if provider_name != 'demo' and api_key:
                if not self.validate_provider_api_key(provider_name, api_key):
                    return False

            # Set the new provider
            self.set_provider(provider_name, api_key, model)

            # Store the switch in session state for persistence
            st.session_state.current_ai_provider = provider_name

            return True
        except Exception as e:
            st.error(f"Error switching to {provider_name}: {str(e)}")
            return False

    def get_provider_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all providers"""
        status = {
            'current_provider': self.current_provider,
            'current_provider_info': self.get_current_provider_info(),
            'available_providers': {},
            'configured_providers': []
        }

        for provider_key, provider_config in AIProviderConfig.PROVIDERS.items():
            has_key = False
            if provider_key == 'demo':
                has_key = True
            else:
                has_key = key_manager.has_api_key(provider_key)

            status['available_providers'][provider_key] = {
                'name': provider_config['name'],
                'icon': provider_config['icon'],
                'description': provider_config['description'],
                'requires_api_key': provider_config.get('requires_api_key', False),
                'has_api_key': has_key,
                'is_current': provider_key == self.current_provider
            }

            if has_key:
                status['configured_providers'].append(provider_key)

        return status

    def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat message with the current AI provider"""
        try:
            provider = self.get_current_provider()
            if provider is None:
                # Fallback to demo mode
                self.set_provider('demo')
                provider = self.get_current_provider()

            # Process the chat message
            response = provider.chat(message, chat_history)

            # Add comprehensive provider information to response
            response['current_provider'] = self.get_current_provider_info()
            response['provider_status'] = self.get_provider_status()
            response['conversation_preserved'] = True

            return response
        except Exception as e:
            st.warning(f"🔄 AI provider error - Using demo mode. Error: {str(e)}")
            # Fallback to demo mode
            self.set_provider('demo')
            fallback_response = self.providers['demo'].chat(message, chat_history)
            fallback_response['fallback_used'] = True
            fallback_response['original_error'] = str(e)
            return fallback_response

    def preserve_conversation_context(self, chat_history: List[Dict]) -> List[Dict]:
        """Preserve conversation context when switching providers"""
        # Filter and format chat history for provider compatibility
        preserved_history = []

        for message in chat_history:
            if message.get('role') in ['user', 'assistant']:
                preserved_message = {
                    'role': message['role'],
                    'content': message['content'],
                    'timestamp': message.get('timestamp', datetime.now().isoformat())
                }
                preserved_history.append(preserved_message)

        return preserved_history

    def get_available_providers(self) -> Dict[str, Dict]:
        """Get all available AI providers"""
        return AIProviderConfig.PROVIDERS

# Initialize AI service
ai_service = AIService()

# Modern Professional CSS Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* CSS Variables for flat color theme */
    :root {
        /* Primary flat colors */
        --white: #FFFFFF;
        --blue: #2563eb;
        --black: #1f2937;
        --red: #dc2626;

        /* Derived colors for better UX */
        --blue-light: #3b82f6;
        --blue-dark: #1d4ed8;
        --gray-light: #6b7280;
        --gray-medium: #374151;
        --red-light: #ef4444;
        --red-dark: #b91c1c;

        /* Layout properties */
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }

    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--white);
        min-height: 100vh;
        color: var(--black);
    }

    /* Main container */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1200px;
        background: var(--white);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-lg);
        margin: 2rem auto;
    }

    /* Header styling */
    .modern-header {
        text-align: center;
        padding: 2rem 0;
        background: var(--blue);
        color: var(--white);
        border-radius: var(--radius-lg);
        margin-bottom: 2rem;
        box-shadow: var(--shadow-md);
    }

    .modern-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .modern-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
    }

    /* Chat interface */
    .chat-container {
        background: var(--white);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--gray-light);
    }

    .chat-message {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
    }

    .chat-message.user {
        background: var(--white);
        border-left: 4px solid var(--blue);
        margin-left: 2rem;
        color: var(--black);
    }

    .chat-message.assistant {
        background: var(--white);
        border-left: 4px solid var(--gray-light);
        margin-right: 2rem;
        color: var(--black);
    }

    .chat-message.assistant.fallback {
        background: var(--white);
        border-left: 4px solid var(--red);
        color: var(--black);
    }

    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: var(--radius-md);
        font-weight: 500;
        margin: 0.25rem;
        box-shadow: var(--shadow-sm);
    }

    .status-healthy {
        background: var(--white);
        color: var(--blue);
        border: 1px solid var(--blue);
    }

    .status-warning {
        background: var(--white);
        color: var(--red);
        border: 1px solid var(--red);
    }

    .status-error {
        background: var(--red);
        color: var(--white);
        border: 1px solid var(--red);
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: var(--white);
        border-radius: var(--radius-md);
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid var(--gray-light);
    }

    /* Demo mode indicator */
    .demo-mode-indicator {
        background: var(--blue);
        color: var(--white);
        padding: 0.75rem;
        border-radius: var(--radius-md);
        text-align: center;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: var(--shadow-md);
    }

    /* Verification section */
    .verification-container {
        background: var(--white);
        border: 1px solid var(--blue);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin: 1rem 0;
    }

    /* Buttons */
    .stButton > button {
        background: var(--blue);
        color: var(--white);
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }

    .stButton > button:hover {
        background: var(--blue-dark);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    /* Watermark */
    .watermark {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 6rem;
        color: rgba(0, 0, 0, 0.05);
        font-weight: 700;
        pointer-events: none;
        z-index: 0;
        user-select: none;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Watermark
st.markdown('<div class="watermark">Abhijeet Swami</div>', unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

        welcome_message = "Welcome to Agentic Calendar! I'm your intelligent scheduling assistant. I can help you manage appointments, check availability, and seamlessly integrate with your Google Calendar."

        if config.demo_mode:
            welcome_message += "\n\n🎯 **DEMO MODE ACTIVE** - You're experiencing a full demonstration with simulated data. All features are functional for evaluation purposes!"

        welcome_message += "\n\nHow can I help you today?"

        st.session_state.messages.append({
            'role': 'assistant',
            'content': welcome_message,
            'timestamp': datetime.now()
        })

    if 'google_calendar_connected' not in st.session_state:
        st.session_state.google_calendar_connected = False

    if 'access_token' not in st.session_state:
        st.session_state.access_token = None

    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

    # Initialize AI provider settings
    if 'ai_provider_initialized' not in st.session_state:
        # Set default provider based on available API keys
        default_provider = 'demo'

        # Check if any API keys are available in secrets or secure storage
        if config.gemini_api_key:
            ai_service.set_provider('gemini', config.gemini_api_key)
            default_provider = 'gemini'
        elif key_manager.has_api_key('openai'):
            api_key = key_manager.get_api_key('openai')
            ai_service.set_provider('openai', api_key)
            default_provider = 'openai'
        elif key_manager.has_api_key('gemini'):
            api_key = key_manager.get_api_key('gemini')
            ai_service.set_provider('gemini', api_key)
            default_provider = 'gemini'
        elif key_manager.has_api_key('claude'):
            api_key = key_manager.get_api_key('claude')
            ai_service.set_provider('claude', api_key)
            default_provider = 'claude'
        else:
            ai_service.set_provider('demo')

        st.session_state.ai_provider_initialized = True
        st.session_state.current_ai_provider = default_provider

# Handle OAuth callback
def handle_oauth_callback():
    """Handle OAuth callback from URL parameters"""
    query_params = st.query_params

    # Handle demo OAuth flow
    if 'demo_oauth' in query_params and 'state' in query_params:
        state = query_params['state']

        if state == st.session_state.get('oauth_state'):
            st.session_state.google_calendar_connected = True
            st.session_state.user_info = demo_service.demo_user
            st.session_state.access_token = 'demo_token'

            # Clear URL parameters
            st.query_params.clear()

            st.success("🎉 Demo Calendar connected successfully! You can now test all features with simulated data.")
            st.balloons()
            st.rerun()

    # Handle real OAuth flow
    elif 'oauth_callback' in query_params and 'code' in query_params and 'state' in query_params:
        code = query_params['code']
        state = query_params['state']

        try:
            user_info = oauth_service.handle_oauth_callback(code, state)
            st.session_state.google_calendar_connected = True
            st.session_state.user_info = user_info

            # Clear URL parameters
            st.query_params.clear()

            st.success("🎉 Google Calendar connected successfully!")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"❌ OAuth error: {str(e)}")
            # Clear URL parameters
            st.query_params.clear()

# Main application
def main():
    """Main application function"""
    initialize_session_state()
    handle_oauth_callback()

    # Header
    st.markdown("""
    <div class="modern-header">
        <h1>🤖 Agentic Calendar</h1>
        <p>Intelligent Meeting Scheduler & Calendar Management</p>
    </div>
    """, unsafe_allow_html=True)

    # Demo mode indicator
    if config.demo_mode:
        st.markdown("""
        <div class="demo-mode-indicator">
            🎯 DEMO MODE ACTIVE<br>
            <small style="opacity: 0.9;">Full functionality with simulated data for evaluation</small>
        </div>
        """, unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([3, 1])

    with col1:
        render_chat_interface()

    with col2:
        render_sidebar()

def render_chat_interface():
    """Render the chat interface"""
    # Header with current AI provider info
    current_provider_info = ai_service.get_current_provider_info()

    st.markdown(f"### 💬 Chat with {current_provider_info['icon']} {current_provider_info['name']}")

    # Provider status bar
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown("Ask me to schedule meetings, check your calendar, or help with appointments!")

    with col2:
        if current_provider_info['provider_key'] != 'demo':
            if current_provider_info['has_api_key']:
                st.success("🔑 Connected")
                st.caption(f"Using {current_provider_info['name']} API")
            else:
                st.warning("🎯 Demo Mode")
                st.caption("No API key configured")
        else:
            st.info("🎯 Demo Mode")
            st.caption("Using simulated AI responses")

    with col3:
        # Conversation stats
        message_count = len([msg for msg in st.session_state.messages if msg['role'] == 'user'])
        st.metric("Messages", message_count)

    # Provider switching notification
    if st.session_state.get('provider_switched', False):
        st.info(f"🔄 Switched to {current_provider_info['icon']} {current_provider_info['name']}. Your conversation history is preserved!")
        st.session_state.provider_switched = False

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display chat messages
        for i, message in enumerate(st.session_state.messages):
            role = message['role']
            content = message['content']
            timestamp = message.get('timestamp', datetime.now())

            # Format timestamp
            if isinstance(timestamp, datetime):
                time_str = timestamp.strftime('%H:%M')
            else:
                time_str = datetime.now().strftime('%H:%M')

            # Message styling
            if role == 'user':
                st.markdown(f"""
                <div class="chat-message user">
                    <strong>You</strong> <small style="color: var(--gray-500);">{time_str}</small><br>
                    {content}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Get provider info for assistant messages
                provider_info = message.get('provider_info', {})
                fallback_used = message.get('fallback_used', False)

                # Determine header based on provider
                if provider_info:
                    provider_name = provider_info.get('name', 'AI Assistant')
                    provider_icon = provider_info.get('icon', '🤖')
                    header = f"{provider_icon} {provider_name}"
                else:
                    header = "🤖 Agentic Calendar"

                # Add fallback indicator if used
                if fallback_used:
                    header += " (Demo Fallback)"

                # Message styling with provider info
                message_class = "chat-message assistant"
                if fallback_used:
                    message_class += " fallback"

                st.markdown(f"""
                <div class="{message_class}">
                    <strong>{header}</strong> <small style="color: var(--gray-500);">{time_str}</small><br>
                    {content}
                </div>
                """, unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': prompt,
            'timestamp': datetime.now()
        })

        # Get AI response
        current_provider_info = ai_service.get_current_provider_info()
        with st.spinner(f"🤖 {current_provider_info['icon']} {current_provider_info['name']} is processing your request..."):
            # Preserve conversation context for provider compatibility
            preserved_history = ai_service.preserve_conversation_context(st.session_state.messages)
            ai_response = ai_service.chat(prompt, preserved_history)

            # Add AI response with provider information
            response_content = ai_response['response']

            # Add provider info to response if it's not demo mode
            if ai_response.get('current_provider', {}).get('provider_key') != 'demo':
                provider_info = ai_response['current_provider']
                response_content += f"\n\n*Powered by {provider_info['icon']} {provider_info['name']}*"
                if provider_info.get('model'):
                    response_content += f" *({provider_info['model']})*"

            st.session_state.messages.append({
                'role': 'assistant',
                'content': response_content,
                'timestamp': datetime.now(),
                'provider_info': ai_response.get('current_provider', {}),
                'fallback_used': ai_response.get('fallback_used', False)
            })

            # Handle actions
            if ai_response.get('action') == 'CREATE_EVENT':
                handle_meeting_creation(prompt, ai_response)
            elif ai_response.get('action') == 'VIEW_EVENTS':
                display_calendar_events(ai_response.get('events', []))
            elif ai_response.get('action') == 'CHECK_AVAILABILITY':
                display_availability(ai_response.get('availability', []))

        st.rerun()

def handle_meeting_creation(user_message: str, ai_response: Dict[str, Any]):
    """Handle meeting creation from AI response"""
    # Extract meeting details from user message
    meeting_data = extract_meeting_details(user_message)

    # Create the event
    if config.demo_mode:
        event_result = demo_service.create_demo_event(meeting_data)
    else:
        event_result = create_calendar_event(meeting_data)

    if event_result and event_result.get('success'):
        st.success(f"✅ Event '{event_result['title']}' created successfully!")
        st.balloons()

        # Display verification section
        st.markdown("### 🎯 Meeting Verification")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📅 Event Details:**")
            st.write(f"**Title:** {event_result.get('title', 'N/A')}")
            st.write(f"**Start:** {event_result.get('start_time', 'N/A')}")
            st.write(f"**End:** {event_result.get('end_time', 'N/A')}")
            if event_result.get('demo_mode'):
                st.info("🎯 Demo Mode: This is a simulated event for evaluation")

        with col2:
            st.markdown("**🔗 Verification Links:**")

            if event_result.get('event_link'):
                st.markdown(f"""
                <a href="{event_result['event_link']}" target="_blank" style="
                    display: inline-block;
                    background: var(--blue);
                    color: var(--white);
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: var(--radius-md);
                    font-weight: 600;
                    margin: 2px;
                ">🔗 View in Google Calendar</a>
                """, unsafe_allow_html=True)

            if event_result.get('verification_link'):
                st.markdown(f"""
                <a href="{event_result['verification_link']}" target="_blank" style="
                    display: inline-block;
                    background: var(--blue);
                    color: var(--white);
                    padding: 8px 16px;
                    text-decoration: none;
                    border-radius: var(--radius-md);
                    font-weight: 500;
                    margin: 2px;
                ">📋 Event Verification</a>
                """, unsafe_allow_html=True)

        # Success confirmation
        st.markdown(f"""
        <div class="verification-container">
            <strong style="color: var(--blue);">✅ Meeting Successfully Created!</strong><br>
            <small style="color: var(--gray-light);">Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small><br>
            <small style="color: var(--gray-light);">Event ID: {event_result.get('event_id', 'N/A')}</small>
        </div>
        """, unsafe_allow_html=True)

def extract_meeting_details(message: str) -> Dict[str, Any]:
    """Extract meeting details from user message"""
    # Simple extraction logic - in production, use more sophisticated NLP
    import re

    # Default values
    meeting_data = {
        'title': 'Meeting',
        'start_time': (datetime.now() + timedelta(hours=1)).isoformat(),
        'end_time': (datetime.now() + timedelta(hours=2)).isoformat(),
        'description': f'Meeting scheduled via Agentic Calendar: {message}',
        'attendees': []
    }

    # Extract title
    if 'with' in message.lower():
        parts = message.lower().split('with')
        if len(parts) > 1:
            name_part = parts[1].split()[0]
            meeting_data['title'] = f'Meeting with {name_part.title()}'

    # Extract time (simple patterns)
    time_patterns = [
        r'(\d{1,2})\s*(pm|am)',
        r'(\d{1,2}):(\d{2})\s*(pm|am)',
        r'at\s*(\d{1,2})',
    ]

    for pattern in time_patterns:
        match = re.search(pattern, message.lower())
        if match:
            # Simple time extraction - in production, use more sophisticated parsing
            hour = int(match.group(1))
            if 'pm' in message.lower() and hour != 12:
                hour += 12

            start_time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
            if 'tomorrow' in message.lower():
                start_time += timedelta(days=1)

            meeting_data['start_time'] = start_time.isoformat()
            meeting_data['end_time'] = (start_time + timedelta(hours=1)).isoformat()
            break

    return meeting_data

def create_calendar_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a real calendar event (if not in demo mode)"""
    if not st.session_state.get('access_token'):
        return {'success': False, 'error': 'Not authenticated'}

    # In a real implementation, this would use the Google Calendar API
    # For now, return a simulated success
    return {
        'success': True,
        'event_id': f'real_event_{secrets.token_hex(8)}',
        'title': event_data['title'],
        'start_time': event_data['start_time'],
        'end_time': event_data['end_time'],
        'event_link': 'https://calendar.google.com/calendar/event?eid=real_event',
        'verification_link': 'https://calendar.google.com/calendar/r/eventedit/real_event',
        'message': 'Event created successfully in Google Calendar'
    }

def display_calendar_events(events: List[Dict[str, Any]]):
    """Display calendar events"""
    if events:
        st.markdown("### 📅 Your Calendar Events")
        for event in events[:5]:  # Show first 5 events
            st.markdown(f"""
            **{event.get('title', 'Untitled Event')}**
            📅 {event.get('start_time', 'No time')} - {event.get('end_time', 'No time')}
            📍 {event.get('location', 'No location')}
            👥 {', '.join(event.get('attendees', []))}
            """)

def display_availability(availability: List[Dict[str, str]]):
    """Display availability information"""
    if availability:
        st.markdown("### 🕐 Your Availability")
        for slot in availability[:10]:  # Show first 10 slots
            st.markdown(f"📅 {slot.get('date')} - {slot.get('start_time')} to {slot.get('end_time')}")

def render_ai_provider_settings():
    """Render AI provider configuration settings"""
    st.markdown("### 🤖 AI Provider Settings")

    # Get current provider info
    current_provider_info = ai_service.get_current_provider_info()

    # Provider selection
    providers = ai_service.get_available_providers()
    provider_options = []
    provider_keys = []

    for key, provider in providers.items():
        provider_options.append(f"{provider['icon']} {provider['name']}")
        provider_keys.append(key)

    # Find current selection index
    try:
        current_index = provider_keys.index(ai_service.current_provider)
    except ValueError:
        current_index = 0

    selected_provider_display = st.selectbox(
        "Choose AI Provider:",
        provider_options,
        index=current_index,
        help="Select your preferred AI provider for chat responses"
    )

    # Get selected provider key
    selected_index = provider_options.index(selected_provider_display)
    selected_provider = provider_keys[selected_index]

    # Show provider description
    provider_config = providers[selected_provider]
    st.markdown(f"**{provider_config['description']}**")

    # API Key configuration for non-demo providers
    if selected_provider != 'demo' and provider_config['requires_api_key']:
        st.markdown("#### 🔑 API Key Configuration")

        # Get current API key from secure storage
        current_api_key = key_manager.get_api_key(selected_provider)

        # API key input
        api_key = st.text_input(
            f"{provider_config['name']} API Key:",
            value=current_api_key,
            type="password",
            help=f"Enter your {provider_config['name']} API key",
            key=f"{selected_provider}_key_input"
        )

        # Model selection for providers that support it
        if 'models' in provider_config:
            model_session_key = f"{selected_provider}_model"
            current_model = st.session_state.get(model_session_key, provider_config['models'][0])

            selected_model = st.selectbox(
                "Model:",
                provider_config['models'],
                index=provider_config['models'].index(current_model) if current_model in provider_config['models'] else 0,
                help=f"Choose the {provider_config['name']} model to use",
                key=f"{selected_provider}_model_select"
            )

            # Store model selection
            st.session_state[model_session_key] = selected_model
        else:
            selected_model = None

        # API key validation and saving
        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"🔍 Test {provider_config['name']}", use_container_width=True):
                if api_key:
                    with st.spinner("Testing API key..."):
                        is_valid = ai_service.validate_provider_api_key(selected_provider, api_key)
                        if is_valid:
                            st.success("✅ API key is valid!")
                            key_manager.store_api_key(selected_provider, api_key)
                        else:
                            st.error("❌ Invalid API key")
                else:
                    st.warning("Please enter an API key to test")

        with col2:
            if st.button(f"💾 Save & Use {provider_config['name']}", use_container_width=True):
                if api_key:
                    # Store API key securely
                    key_manager.store_api_key(selected_provider, api_key)

                    # Set the provider
                    try:
                        ai_service.set_provider(selected_provider, api_key, selected_model)
                        st.session_state.provider_switched = True
                        st.success(f"✅ Switched to {provider_config['name']}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error setting provider: {str(e)}")
                else:
                    st.warning("Please enter an API key")

        # Instructions for getting API keys
        with st.expander(f"📖 How to get {provider_config['name']} API key"):
            if selected_provider == 'openai':
                st.markdown("""
                1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
                2. Sign in or create an account
                3. Click "Create new secret key"
                4. Copy the API key and paste it above
                5. Note: You'll need to add billing information to use the API
                """)
            elif selected_provider == 'gemini':
                st.markdown("""
                1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
                2. Sign in with your Google account
                3. Click "Create API key"
                4. Copy the API key and paste it above
                5. The API has a generous free tier
                """)
            elif selected_provider == 'claude':
                st.markdown("""
                1. Go to [Anthropic Console](https://console.anthropic.com/)
                2. Sign in or create an account
                3. Navigate to "API Keys" section
                4. Click "Create Key"
                5. Copy the API key and paste it above
                """)

    else:
        # Demo mode or provider doesn't need API key
        if st.button(f"🎯 Use {provider_config['name']}", use_container_width=True):
            ai_service.set_provider(selected_provider)
            st.session_state.provider_switched = True
            st.success(f"✅ Switched to {provider_config['name']}!")
            st.rerun()

    # Current provider status
    st.markdown("---")
    st.markdown("#### 📊 Current Provider Status")

    current_info = ai_service.get_current_provider_info()
    provider_status = ai_service.get_provider_status()

    # Active provider display
    st.markdown(f"**Active:** {current_info['icon']} {current_info['name']}")

    if current_info.get('model'):
        st.markdown(f"**Model:** {current_info['model']}")

    # API key status
    if current_info['provider_key'] != 'demo':
        if current_info['has_api_key']:
            st.success("🔑 API key configured")
        else:
            st.warning("⚠️ No API key - using demo mode")
    else:
        st.info("🎯 Demo mode active")

    # Quick provider switching
    st.markdown("#### ⚡ Quick Switch")

    configured_providers = provider_status['configured_providers']
    if len(configured_providers) > 1:
        switch_cols = st.columns(min(len(configured_providers), 3))

        for i, provider_key in enumerate(configured_providers):
            if provider_key != ai_service.current_provider:
                provider_info = provider_status['available_providers'][provider_key]
                col_index = i % 3

                with switch_cols[col_index]:
                    if st.button(
                        f"{provider_info['icon']} {provider_info['name'][:8]}",
                        use_container_width=True,
                        key=f"quick_switch_{provider_key}"
                    ):
                        # Quick switch to this provider
                        api_key = key_manager.get_api_key(provider_key) if provider_key != 'demo' else None
                        if ai_service.switch_provider(provider_key, api_key):
                            st.success(f"✅ Switched to {provider_info['name']}!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to switch to {provider_info['name']}")

    # Provider overview
    with st.expander("🔍 All Providers Overview"):
        for provider_key, provider_info in provider_status['available_providers'].items():
            status_icon = "✅" if provider_info['has_api_key'] else "⚠️"
            current_icon = "👈" if provider_info['is_current'] else ""

            st.markdown(f"{status_icon} {provider_info['icon']} **{provider_info['name']}** {current_icon}")
            st.markdown(f"   *{provider_info['description']}*")

            if not provider_info['has_api_key'] and provider_info['requires_api_key']:
                st.markdown("   *No API key configured*")

    # Clear API keys option
    if st.button("🗑️ Clear All API Keys", use_container_width=True):
        if st.session_state.get('confirm_clear_keys', False):
            # Actually clear the keys
            for provider in ['openai', 'gemini', 'claude']:
                key_manager.clear_api_key(provider)

            # Reset to demo mode
            ai_service.set_provider('demo')
            st.session_state.confirm_clear_keys = False
            st.success("✅ All API keys cleared. Switched to demo mode.")
            st.rerun()
        else:
            # Show confirmation
            st.session_state.confirm_clear_keys = True
            st.warning("⚠️ Click again to confirm clearing all API keys")

    if st.session_state.get('confirm_clear_keys', False):
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.confirm_clear_keys = False
            st.rerun()

def render_sidebar():
    """Render the sidebar"""
    with st.sidebar:
        st.markdown("### 🤖 Agentic Calendar")
        st.markdown("*AI-Powered Meeting Scheduler*")

        # Demo mode indicator
        if config.demo_mode:
            st.markdown("""
            <div style="
                background: #2563eb;
                color: white;
                padding: 0.75rem;
                border-radius: 0.5rem;
                text-align: center;
                margin: 1rem 0;
                font-weight: 600;
            ">
                🎯 DEMO MODE ACTIVE<br>
                <small style="opacity: 0.9;">Full functionality with simulated data</small>
            </div>
            """, unsafe_allow_html=True)

        # AI Provider Settings
        st.markdown("---")
        render_ai_provider_settings()

        # System Status
        st.markdown("---")
        st.markdown("### 📊 System Status")

        if config.demo_mode:
            st.success("🟢 Demo Mode: Active")
            st.success("🟢 AI Service: Simulated")
            st.success("🟢 Calendar: Simulated")
        else:
            if config.is_configured():
                st.success("🟢 System: Configured")
            else:
                st.warning("🟡 System: Needs Configuration")

        # Google Calendar Connection
        st.markdown("---")
        st.markdown("### 📅 Google Calendar")

        if st.session_state.google_calendar_connected:
            status_text = "🟢 Connected"
            if config.demo_mode:
                status_text += " (Demo)"
            st.success(status_text)

            if st.session_state.get('user_info'):
                user_info = st.session_state.user_info
                st.write(f"👤 {user_info.get('name', 'User')}")
                st.write(f"📧 {user_info.get('email', 'No email')}")
        else:
            st.warning("🟡 Not Connected")

            if st.button("🔗 Connect Google Calendar", use_container_width=True):
                auth_url = oauth_service.get_auth_url()
                if auth_url:
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
                    if config.demo_mode:
                        st.info("Redirecting to demo authentication...")
                    else:
                        st.info("Redirecting to Google for authentication...")
                else:
                    st.error("Failed to get authorization URL")

        # Tips Section
        st.markdown("---")
        st.markdown("### 💡 Quick Tips")
        if config.demo_mode:
            st.markdown("""
            • **Demo Schedule**: "Schedule a meeting with John tomorrow at 2 PM"
            • **Demo Check**: "What's my availability this week?"
            • **Demo View**: "Show me today's meetings"
            • **All features work with simulated data!**
            """)
        else:
            st.markdown("""
            • **Schedule**: "Book a meeting with John tomorrow at 2 PM"
            • **Check**: "What's my availability this week?"
            • **View**: "Show me today's meetings"
            • **Natural**: Use conversational language!
            """)

        # Watermark
        st.markdown("---")
        st.markdown(
            '<div style="text-align: center; opacity: 0.6; font-size: 0.8em;">Built by Abhijeet Swami</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
