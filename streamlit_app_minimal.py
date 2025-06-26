import streamlit as st
import os
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any, Optional
import json
import secrets
from urllib.parse import urlencode
import requests

# Page configuration
st.set_page_config(
    page_title="TailorTalk - AI Calendar Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Try to import Google libraries
try:
    import google.generativeai as genai
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_LIBS_AVAILABLE = True
except ImportError as e:
    st.error(f"Google libraries not available: {e}")
    GOOGLE_LIBS_AVAILABLE = False

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .ai-message {
        background-color: #f1f3f4;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
    }
    
    .calendar-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Simple Gemini Service
class SimpleGeminiService:
    def __init__(self):
        self.api_key = self._get_api_key()
        self.model = None
        if self.api_key and GOOGLE_LIBS_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                st.error(f"Error initializing Gemini: {e}")
    
    def _get_api_key(self) -> str:
        # Try Streamlit secrets first
        try:
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                return st.secrets['GEMINI_API_KEY']
        except:
            pass
        
        # Fall back to environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'PLACEHOLDER_API_KEY':
            return api_key
        return None
    
    def is_configured(self) -> bool:
        return self.model is not None
    
    def get_response(self, user_message: str, chat_history: List[Dict], calendar_connected: bool = False) -> str:
        if not self.model:
            return "I apologize, but I'm not properly configured. Please ensure the GEMINI_API_KEY is set correctly."
        
        try:
            system_prompt = """You are TailorTalk, a friendly AI assistant specialized in scheduling appointments using Google Calendar. 
            
            Key capabilities:
            1. Natural Conversation: Engage in clear, polite dialogue.
            2. Intent Understanding: Determine if a user wants to schedule, modify, or cancel appointments.
            3. Google Calendar Integration: Help users with calendar-related tasks.
            
            Be helpful, concise, and friendly. If the user asks about calendar operations, guide them appropriately."""
            
            if calendar_connected:
                system_prompt += "\n\nThe user has connected their Google Calendar and you can help them with scheduling."
            else:
                system_prompt += "\n\nThe user has NOT connected their Google Calendar yet. If they want to schedule something, ask them to connect their calendar first."
            
            # Create conversation context
            conversation = f"{system_prompt}\n\nUser: {user_message}\nTailorTalk:"
            
            response = self.model.generate_content(conversation)
            
            if response.text:
                return response.text.strip()
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        'role': 'assistant',
        'content': "Hello! I'm TailorTalk. I can help you schedule appointments on your Google Calendar. How can I assist you today?",
        'timestamp': datetime.now()
    })

if 'google_calendar_connected' not in st.session_state:
    st.session_state.google_calendar_connected = False

if 'google_user_info' not in st.session_state:
    st.session_state.google_user_info = None

if 'gemini_service' not in st.session_state:
    st.session_state.gemini_service = SimpleGeminiService()

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📅 TailorTalk</h1>
        <p>Your AI-powered Calendar Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Service status indicators
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        if st.session_state.gemini_service and st.session_state.gemini_service.is_configured():
            st.success("🤖 Gemini AI: Ready")
        else:
            st.error("🤖 Gemini AI: Not Configured")
    
    with col_status2:
        if st.session_state.google_calendar_connected:
            st.success("📅 Calendar: Connected (Demo)")
        else:
            st.warning("📅 Calendar: Not Connected")
    
    # Sidebar for Google Calendar connection
    with st.sidebar:
        st.header("🔗 Google Calendar")
        
        if st.session_state.google_calendar_connected:
            st.markdown(f"""
            <div class="calendar-status connected">
                ✅ Connected as {st.session_state.google_user_info.get('name', 'Demo User')}
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔓 Disconnect Calendar", type="secondary"):
                st.session_state.google_calendar_connected = False
                st.session_state.google_user_info = None
                st.rerun()
        else:
            st.markdown("""
            <div class="calendar-status disconnected">
                ❌ Not Connected
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔗 Connect Google Calendar", type="primary"):
                # Demo connection for now
                st.session_state.google_calendar_connected = True
                st.session_state.google_user_info = {
                    'name': 'Demo User',
                    'email': 'demo@example.com'
                }
                st.success("✅ Calendar connected successfully! (Demo Mode)")
                st.info("💡 This is a demo connection. Full OAuth integration available in production.")
                st.rerun()
                
            st.markdown("""
            <small>
            <strong>Note:</strong> Demo mode for testing. 
            Real Google Calendar integration requires OAuth setup.
            </small>
            """, unsafe_allow_html=True)
    
    # Main chat interface
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Display chat messages
        st.subheader("💬 Chat")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="user-message">
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="ai-message">
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)

        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Check if Gemini service is available
            if not st.session_state.gemini_service or not st.session_state.gemini_service.is_configured():
                st.error("🚨 Cannot send message: Gemini AI is not configured properly.")
                st.info("Please configure your GEMINI_API_KEY in Streamlit Cloud secrets.")
                st.stop()
            
            # Add user message
            st.session_state.messages.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })

            # Process with AI
            with st.spinner("🤖 TailorTalk is thinking..."):
                try:
                    # Get AI response
                    ai_response = st.session_state.gemini_service.get_response(
                        user_input,
                        st.session_state.messages[:-1],
                        st.session_state.google_calendar_connected
                    )

                    # Add AI response
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': ai_response,
                        'timestamp': datetime.now()
                    })

                except Exception as e:
                    error_message = f"I apologize, but I encountered an error: {str(e)}"
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': error_message,
                        'timestamp': datetime.now()
                    })
                    st.error(f"❌ Error processing message: {str(e)}")

            st.rerun()

if __name__ == "__main__":
    main()
