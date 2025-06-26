import streamlit as st
import os
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any
import json

# Import our custom modules
from backend.gemini_service import GeminiService
from backend.google_calendar_service import GoogleCalendarService
from backend.oauth_handler import GoogleOAuthHandler

# Page configuration
st.set_page_config(
    page_title="TailorTalk - AI Calendar Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #f9f9f9;
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

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Add initial greeting
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
    st.session_state.gemini_service = None

if 'calendar_service' not in st.session_state:
    st.session_state.calendar_service = None

if 'oauth_handler' not in st.session_state:
    st.session_state.oauth_handler = None

if 'google_tokens' not in st.session_state:
    st.session_state.google_tokens = None

# Initialize services
def initialize_services():
    """Initialize Gemini and Google Calendar services"""
    try:
        if st.session_state.gemini_service is None:
            st.session_state.gemini_service = GeminiService()

            # Check if Gemini service is properly configured
            if not st.session_state.gemini_service.is_configured():
                st.error("🚨 Gemini AI is not properly configured. Please check your API key.")
                with st.expander("🔧 Gemini AI Setup Instructions"):
                    st.markdown("""
                    **To configure Gemini AI:**

                    1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
                    2. Add it to your `.env.local` file:
                       ```
                       GEMINI_API_KEY=your_api_key_here
                       ```
                    3. Restart the application

                    **Current Status:** API key not found or invalid
                    """)

        if st.session_state.calendar_service is None:
            st.session_state.calendar_service = GoogleCalendarService()

        if st.session_state.oauth_handler is None:
            st.session_state.oauth_handler = GoogleOAuthHandler()

        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {str(e)}")
        st.info("💡 Please check your configuration and try refreshing the page.")
        return False

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📅 TailorTalk</h1>
        <p>Your AI-powered Calendar Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize services
    if not initialize_services():
        st.stop()

    # Handle OAuth callback if present
    if st.session_state.oauth_handler:
        if st.session_state.oauth_handler.handle_oauth_callback():
            st.success("✅ Successfully connected to Google Calendar!")
            # Initialize calendar service with tokens
            if st.session_state.google_tokens:
                st.session_state.calendar_service.initialize_with_tokens(st.session_state.google_tokens)
            st.rerun()

    # Service status indicators
    col_status1, col_status2 = st.columns(2)

    with col_status1:
        if st.session_state.gemini_service and st.session_state.gemini_service.is_configured():
            st.success("🤖 Gemini AI: Ready")
        else:
            st.error("🤖 Gemini AI: Not Configured")

    with col_status2:
        if st.session_state.google_calendar_connected and st.session_state.calendar_service.is_authenticated():
            st.success("📅 Calendar: Connected & Authenticated")
        elif st.session_state.oauth_handler and st.session_state.oauth_handler.is_configured():
            st.info("📅 Calendar: OAuth Ready (Not Connected)")
        else:
            st.warning("📅 Calendar: OAuth Not Configured")

    # Sidebar for Google Calendar connection
    with st.sidebar:
        st.header("🔗 Google Calendar")

        # Check if OAuth is configured
        oauth_configured = st.session_state.oauth_handler and st.session_state.oauth_handler.is_configured()

        if not oauth_configured:
            st.warning("⚠️ Google Calendar OAuth not configured")
            st.markdown("""
            <div class="calendar-status disconnected">
                ❌ OAuth Not Configured
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📋 OAuth Setup Instructions"):
                st.markdown("""
                **To enable Google Calendar integration:**

                1. Go to [Google Cloud Console](https://console.cloud.google.com/)
                2. Create a project and enable Google Calendar API
                3. Create OAuth 2.0 credentials (Web application)
                4. Add authorized redirect URIs:
                   - For local: `http://localhost:8501`
                   - For Streamlit Cloud: `https://your-app-name.streamlit.app`
                5. Add credentials to your secrets:
                   ```toml
                   [google_oauth]
                   client_id = "your_client_id"
                   client_secret = "your_client_secret"
                   redirect_uri = "your_redirect_uri"
                   ```
                6. Restart the application
                """)

        elif st.session_state.google_calendar_connected and st.session_state.google_user_info:
            user_info = st.session_state.google_user_info
            st.markdown(f"""
            <div class="calendar-status connected">
                ✅ Connected as {user_info.get('name', user_info.get('email', 'User'))}
            </div>
            """, unsafe_allow_html=True)

            # Show user avatar if available
            if 'picture' in user_info:
                st.image(user_info['picture'], width=50)

            st.write(f"📧 {user_info.get('email', 'No email')}")

            if st.button("🔓 Disconnect Calendar", type="secondary"):
                # Revoke tokens
                if st.session_state.google_tokens and 'access_token' in st.session_state.google_tokens:
                    st.session_state.oauth_handler.revoke_token(st.session_state.google_tokens['access_token'])

                # Clear session state
                st.session_state.google_calendar_connected = False
                st.session_state.google_user_info = None
                st.session_state.google_tokens = None
                st.session_state.calendar_service = GoogleCalendarService()

                st.success("🔓 Disconnected from Google Calendar")
                st.rerun()
        else:
            st.markdown("""
            <div class="calendar-status disconnected">
                ❌ Not Connected
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔗 Connect Google Calendar", type="primary"):
                try:
                    # Generate OAuth URL
                    auth_url, state = st.session_state.oauth_handler.generate_auth_url()

                    # Show instructions to user
                    st.info("🔄 Redirecting to Google for authentication...")
                    st.markdown(f"""
                    **Click the link below to authenticate with Google:**

                    [🔗 Authenticate with Google Calendar]({auth_url})

                    After authentication, you'll be redirected back to this app.
                    """)

                except Exception as e:
                    st.error(f"❌ Error generating auth URL: {str(e)}")

            st.markdown("""
            <small>
            <strong>Note:</strong> Real Google Calendar integration with OAuth 2.0 authentication.
            Your calendar data will be accessed securely through Google's API.
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
                        st.session_state.messages[:-1],  # Exclude the current user message
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
                    # Also show error in UI
                    st.error(f"❌ Error processing message: {str(e)}")

            st.rerun()

if __name__ == "__main__":
    main()