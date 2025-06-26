import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration management for TailorTalk"""
    
    @staticmethod
    def get_gemini_api_key() -> str:
        """Get Gemini API key from environment or Streamlit secrets"""
        # Try Streamlit secrets first (for cloud deployment)
        try:
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                return st.secrets['GEMINI_API_KEY']
        except:
            pass
        
        # Fall back to environment variable
        return os.getenv('GEMINI_API_KEY', '')
    
    @staticmethod
    def get_google_client_id() -> str:
        """Get Google Client ID from environment or Streamlit secrets"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth']['client_id']
        except:
            pass
        
        return os.getenv('GOOGLE_CLIENT_ID', '')
    
    @staticmethod
    def get_google_client_secret() -> str:
        """Get Google Client Secret from environment or Streamlit secrets"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth']['client_secret']
        except:
            pass
        
        return os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    @staticmethod
    def is_development() -> bool:
        """Check if running in development mode"""
        return os.getenv('ENVIRONMENT', 'development') == 'development'
    
    @staticmethod
    def get_redirect_uri() -> str:
        """Get OAuth redirect URI"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth'].get('redirect_uri', 'http://localhost:8501')
        except:
            pass
        
        return os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8501')
