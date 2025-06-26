"""
TailorTalk Streamlit Frontend with FastAPI Backend
Modified to communicate with FastAPI backend via HTTP API calls
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
API_ENDPOINTS = {
    'health': f'{API_BASE_URL}/api/v1/health',
    'oauth_config': f'{API_BASE_URL}/api/v1/oauth/config',
    'oauth_auth_url': f'{API_BASE_URL}/api/v1/oauth/auth-url',
    'oauth_token': f'{API_BASE_URL}/api/v1/oauth/token',
    'oauth_status': f'{API_BASE_URL}/api/v1/oauth/status',
    'ai_chat': f'{API_BASE_URL}/api/v1/ai/chat',
    'ai_extract': f'{API_BASE_URL}/api/v1/ai/extract-meeting',
    'ai_status': f'{API_BASE_URL}/api/v1/ai/status',
    'calendar_events': f'{API_BASE_URL}/api/v1/calendar/events',
    'calendar_status': f'{API_BASE_URL}/api/v1/calendar/status'
}

class APIClient:
    """Client for communicating with FastAPI backend"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.session.timeout = 30
    
    def _get_headers(self, include_auth: bool = False) -> Dict[str, str]:
        """Get request headers"""
        headers = {'Content-Type': 'application/json'}
        
        if include_auth and 'access_token' in st.session_state:
            headers['Authorization'] = f"Bearer {st.session_state.access_token}"
        
        return headers
    
    def get(self, endpoint: str, include_auth: bool = False) -> Optional[Dict[str, Any]]:
        """Make GET request to API"""
        try:
            response = self.session.get(
                endpoint,
                headers=self._get_headers(include_auth)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return None
    
    def post(self, endpoint: str, data: Dict[str, Any], include_auth: bool = False) -> Optional[Dict[str, Any]]:
        """Make POST request to API"""
        try:
            response = self.session.post(
                endpoint,
                json=data,
                headers=self._get_headers(include_auth)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return None

# Initialize API client
api_client = APIClient()

# Page configuration
st.set_page_config(
    page_title="Agentic Calendar - Intelligent Meeting Scheduler",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Custom CSS with Modern Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Main Header */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.1;
    }

    .main-header h1 {
        margin: 0;
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }

    .main-header p {
        margin: 1rem 0 0 0;
        font-size: 1.3rem;
        opacity: 0.95;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    /* Status Cards */
    .status-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .status-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }

    .status-indicator {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.25rem;
        transition: all 0.2s ease;
        border: 2px solid transparent;
    }

    .status-healthy {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        color: #155724;
        border-color: #b8dabc;
    }
    .status-degraded {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        color: #856404;
        border-color: #f4d03f;
    }
    .status-error {
        background: linear-gradient(135deg, #f8d7da, #f5b7b1);
        color: #721c24;
        border-color: #e74c3c;
    }

    /* Chat Interface */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1.5rem;
        background: linear-gradient(145deg, #f8f9fa, #ffffff);
        border-radius: 20px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.05);
    }

    .message-container {
        margin: 1rem 0;
        display: flex;
        flex-direction: column;
    }

    .user-message {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin-left: 15%;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
        font-weight: 500;
        position: relative;
    }

    .assistant-message {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        color: #2c3e50;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin-right: 15%;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.05);
        font-weight: 500;
        position: relative;
    }

    /* Sidebar Enhancements */
    .sidebar-section {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }

    /* Button Enhancements */
    .stButton > button {
        border-radius: 25px !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
    }

    /* Connection Status */
    .connection-status {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: 500;
    }

    .connection-connected {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        color: #155724;
        border: 2px solid #b8dabc;
    }

    .connection-disconnected {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        color: #856404;
        border: 2px solid #f4d03f;
    }

    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        .main-header p {
            font-size: 1.1rem;
        }
        .user-message, .assistant-message {
            margin-left: 5%;
            margin-right: 5%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        'role': 'assistant',
        'content': "Welcome to Agentic Calendar! I'm your intelligent scheduling assistant. I can help you manage appointments, check availability, and seamlessly integrate with your Google Calendar. How can I help you today?",
        'timestamp': datetime.now()
    })

if 'google_calendar_connected' not in st.session_state:
    st.session_state.google_calendar_connected = False

if 'access_token' not in st.session_state:
    st.session_state.access_token = None

def check_backend_health():
    """Check if FastAPI backend is healthy"""
    health_data = api_client.get(API_ENDPOINTS['health'])
    
    if health_data:
        return health_data.get('status') == 'healthy', health_data
    else:
        return False, None

def handle_oauth_callback():
    """Handle OAuth callback from URL parameters"""
    query_params = st.query_params

    # Handle new session-based OAuth flow
    if 'session_id' in query_params and 'success' in query_params:
        session_id = query_params['session_id']

        # Retrieve tokens using session ID
        response = api_client.get(f"{API_BASE_URL}/api/v1/oauth/tokens/{session_id}")

        if response and response.get('access_token'):
            st.session_state.access_token = response['access_token']
            st.session_state.google_calendar_connected = True
            st.session_state.user_info = response.get('user_info', {})

            # Clear URL parameters
            st.query_params.clear()

            st.success("🎉 Google Calendar connected successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error("Failed to retrieve OAuth tokens")

    # Handle error cases
    elif 'error' in query_params:
        error = query_params['error']
        error_messages = {
            'invalid_state': 'OAuth state validation failed. Please try connecting again.',
            'token_exchange_failed': 'Failed to exchange authorization code for tokens.',
            'missing_parameters': 'Missing required OAuth parameters.',
            'callback_error': 'An error occurred during OAuth callback.'
        }

        error_message = error_messages.get(error, f'OAuth error: {error}')
        st.error(f"❌ {error_message}")

        # Clear URL parameters
        st.query_params.clear()
        st.rerun()

    # Legacy support for old flow (fallback)
    elif 'code' in query_params and 'state' in query_params:
        code = query_params['code']
        state = query_params['state']

        # Exchange code for tokens (legacy)
        token_data = {
            'code': code,
            'state': state
        }

        response = api_client.post(API_ENDPOINTS['oauth_token'], token_data)

        if response and response.get('access_token'):
            st.session_state.access_token = response['access_token']
            st.session_state.google_calendar_connected = True
            st.session_state.user_info = response.get('user_info', {})

            # Clear URL parameters
            st.query_params.clear()

            st.success("🎉 Google Calendar connected successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error("Failed to exchange authorization code for tokens")

def render_status_dashboard():
    """Render enhanced status dashboard"""
    st.markdown("### 📊 System Status")

    # Check backend health
    backend_healthy, health_data = check_backend_health()

    if not backend_healthy:
        st.markdown("""
        <div class="status-card">
            <div style="text-align: center; padding: 2rem;">
                <h3 style="color: #e74c3c; margin-bottom: 1rem;">🚨 Backend Offline</h3>
                <p style="color: #7f8c8d; margin-bottom: 1.5rem;">The FastAPI backend is not available. Please start the server to continue.</p>
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; font-family: monospace; text-align: left;">
                    <strong>To start the backend:</strong><br>
                    cd backend_api<br>
                    uvicorn main:app --reload --host 127.0.0.1 --port 8000
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Service status indicators in a grid
    col1, col2, col3 = st.columns(3)

    with col1:
        ai_status = health_data and health_data.get('services', {}).get('gemini') == 'configured'
        status_class = "status-healthy" if ai_status else "status-error"
        icon = "🤖" if ai_status else "⚠️"
        text = "AI Ready" if ai_status else "AI Not Configured"
        st.markdown(f'<div class="status-indicator {status_class}">{icon} {text}</div>', unsafe_allow_html=True)

    with col2:
        calendar_status = st.session_state.google_calendar_connected
        status_class = "status-healthy" if calendar_status else "status-degraded"
        icon = "📅" if calendar_status else "📅"
        text = "Calendar Connected" if calendar_status else "Calendar Disconnected"
        st.markdown(f'<div class="status-indicator {status_class}">{icon} {text}</div>', unsafe_allow_html=True)

    with col3:
        status_class = "status-healthy" if backend_healthy else "status-error"
        icon = "🔗" if backend_healthy else "❌"
        text = "Backend Online" if backend_healthy else "Backend Offline"
        st.markdown(f'<div class="status-indicator {status_class}">{icon} {text}</div>', unsafe_allow_html=True)

def main():
    """Enhanced main application function"""
    # Handle OAuth callback first
    handle_oauth_callback()

    # Enhanced Header with Animation
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Agentic Calendar</h1>
        <p>Intelligent Meeting Scheduler & Calendar Management</p>
    </div>
    """, unsafe_allow_html=True)

    # Render status dashboard
    render_status_dashboard()
    
    # Enhanced Sidebar for Google Calendar connection
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🔗 Google Calendar Integration")

        if st.session_state.google_calendar_connected:
            # Connected state with user info
            st.markdown("""
            <div class="connection-status connection-connected">
                <span style="font-size: 1.2em;">✅</span>
                <span>Successfully Connected</span>
            </div>
            """, unsafe_allow_html=True)

            if 'user_info' in st.session_state:
                user_info = st.session_state.user_info
                st.markdown(f"""
                **👤 Account Details:**
                - **Name:** {user_info.get('name', 'Unknown')}
                - **Email:** {user_info.get('email', 'Unknown')}
                """)

            st.markdown("---")

            if st.button("🔓 Disconnect Calendar", type="secondary", use_container_width=True):
                st.session_state.google_calendar_connected = False
                st.session_state.access_token = None
                if 'user_info' in st.session_state:
                    del st.session_state.user_info
                st.success("Calendar disconnected successfully!")
                st.rerun()
        else:
            # Disconnected state
            st.markdown("""
            <div class="connection-status connection-disconnected">
                <span style="font-size: 1.2em;">⚠️</span>
                <span>Calendar Not Connected</span>
            </div>
            """, unsafe_allow_html=True)

            oauth_config = api_client.get(API_ENDPOINTS['oauth_config'])

            if oauth_config and oauth_config.get('is_configured'):
                st.markdown("**Ready to connect your Google Calendar!**")
                st.markdown("This will allow Agentic Calendar to:")
                st.markdown("- 📅 View your calendar events")
                st.markdown("- ➕ Create new appointments")
                st.markdown("- 🔍 Check availability")

                if st.button("🔗 Connect Google Calendar", type="primary", use_container_width=True):
                    with st.spinner("Generating authorization URL..."):
                        auth_response = api_client.get(API_ENDPOINTS['oauth_auth_url'])

                        if auth_response and auth_response.get('auth_url'):
                            st.markdown("### 🚀 Authorization Required")
                            st.markdown(f"""
                            Click the button below to authorize Agentic Calendar:

                            <a href="{auth_response['auth_url']}" target="_blank" style="
                                display: inline-block;
                                background: linear-gradient(135deg, #667eea, #764ba2);
                                color: white;
                                padding: 12px 24px;
                                text-decoration: none;
                                border-radius: 25px;
                                font-weight: 600;
                                margin: 10px 0;
                                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                                transition: all 0.3s ease;
                            ">🔗 Authorize Google Calendar Access</a>

                            After authorization, you'll be redirected back to this page.
                            """, unsafe_allow_html=True)
                            st.info("💡 A new tab will open for Google authorization.")
                        else:
                            st.error("❌ Failed to generate authorization URL")
            else:
                st.markdown("""
                <div style="background: #fff3cd; padding: 1rem; border-radius: 10px; border-left: 4px solid #ffc107;">
                    <strong>⚠️ OAuth Not Configured</strong><br>
                    Please configure your Google OAuth credentials.
                </div>
                """, unsafe_allow_html=True)

                with st.expander("📋 Setup Instructions"):
                    st.markdown("""
                    **To configure OAuth:**
                    1. 🔧 Set up Google OAuth credentials in Google Cloud Console
                    2. 📝 Update `.env.local` with your credentials
                    3. 🔄 Restart the FastAPI backend
                    4. 📖 See `FASTAPI_OAUTH_SETUP.md` for detailed instructions
                    """)

        st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Main chat interface
    st.markdown("### 💬 Chat with Agentic Calendar")
    st.markdown("Ask me to schedule meetings, check your calendar, or help with appointments!")

    # Enhanced chat container with better message rendering
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for i, message in enumerate(st.session_state.messages):
        role = message['role']
        content = message['content']
        timestamp = message.get('timestamp', datetime.now())

        # Format timestamp
        if isinstance(timestamp, datetime):
            time_str = timestamp.strftime("%H:%M")
        else:
            time_str = "now"

        if role == 'user':
            st.markdown(f"""
            <div class="message-container">
                <div class="user-message">
                    {content}
                    <div style="font-size: 0.7em; opacity: 0.8; margin-top: 0.5rem; text-align: right;">
                        {time_str}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-container">
                <div class="assistant-message">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2em;">🤖</span>
                        <strong style="color: #667eea;">Agentic Calendar</strong>
                    </div>
                    {content}
                    <div style="font-size: 0.7em; opacity: 0.7; margin-top: 0.5rem;">
                        {time_str}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Chat input with better UX
    st.markdown("---")

    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📅 Schedule Meeting", use_container_width=True):
            st.session_state.quick_input = "I need to schedule a meeting"
    with col2:
        if st.button("🔍 Check Availability", use_container_width=True):
            st.session_state.quick_input = "What's my availability today?"
    with col3:
        if st.button("📋 View Calendar", use_container_width=True):
            st.session_state.quick_input = "Show me my upcoming events"

    # Chat input with placeholder
    user_input = st.chat_input(
        "Type your message here... (e.g., 'Schedule a meeting with John tomorrow at 2 PM')",
        key="chat_input"
    )

    # Handle quick input
    if hasattr(st.session_state, 'quick_input'):
        user_input = st.session_state.quick_input
        del st.session_state.quick_input

    if user_input:
        # Check if AI service is available
        ai_status = api_client.get(API_ENDPOINTS['ai_status'])

        if not ai_status or not ai_status.get('success'):
            st.error("🚨 AI service is not available. Please check the backend configuration.")
            st.stop()

        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })

        # Enhanced processing with better visual feedback
        with st.spinner("🤖 Agentic Calendar is thinking..."):
            # Show a progress indicator
            progress_placeholder = st.empty()
            progress_placeholder.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <div class="loading-spinner"></div>
                <p style="margin-top: 1rem; color: #667eea;">Processing your request...</p>
            </div>
            """, unsafe_allow_html=True)
            try:
                # Prepare chat request
                chat_request = {
                    'message': user_input,
                    'chat_history': [
                        {
                            'role': msg['role'],
                            'content': msg['content'],
                            'timestamp': msg['timestamp'].isoformat() if isinstance(msg['timestamp'], datetime) else str(msg['timestamp'])
                        }
                        for msg in st.session_state.messages[:-1]  # Exclude current user message
                    ],
                    'calendar_connected': st.session_state.google_calendar_connected
                }
                
                # Get AI response
                ai_response = api_client.post(API_ENDPOINTS['ai_chat'], chat_request)
                
                if ai_response:
                    response_text = ai_response.get('response', 'I apologize, but I couldn\'t generate a response.')
                    action = ai_response.get('action')
                    
                    # Add AI response
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': response_text,
                        'timestamp': datetime.now()
                    })
                    
                    # Clear progress indicator
                    progress_placeholder.empty()

                    # Handle actions with enhanced feedback
                    if action == "CREATE_EVENT" and st.session_state.google_calendar_connected:
                        with st.spinner("📅 Creating calendar event..."):
                            # Show detailed progress
                            progress_placeholder.markdown("""
                            <div style="text-align: center; padding: 1rem;">
                                <div class="loading-spinner"></div>
                                <p style="margin-top: 1rem; color: #667eea;">Extracting meeting details...</p>
                            </div>
                            """, unsafe_allow_html=True)

                            # Extract meeting information
                            extract_request = {
                                'chat_history': [
                                    {
                                        'role': msg['role'],
                                        'content': msg['content'],
                                        'timestamp': msg['timestamp'].isoformat() if isinstance(msg['timestamp'], datetime) else str(msg['timestamp'])
                                    }
                                    for msg in st.session_state.messages
                                ]
                            }

                            extraction_response = api_client.post(API_ENDPOINTS['ai_extract'], extract_request)

                            if extraction_response and extraction_response.get('success'):
                                meeting_info = extraction_response.get('meeting_info')

                                if meeting_info:
                                    # Update progress
                                    progress_placeholder.markdown("""
                                    <div style="text-align: center; padding: 1rem;">
                                        <div class="loading-spinner"></div>
                                        <p style="margin-top: 1rem; color: #667eea;">Creating calendar event...</p>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    # Create calendar event
                                    event_request = {
                                        'title': meeting_info.get('title', ''),
                                        'start_time': f"{meeting_info.get('date')}T{meeting_info.get('start_time')}:00",
                                        'end_time': f"{meeting_info.get('date')}T{meeting_info.get('end_time', '23:59')}:00",
                                        'description': meeting_info.get('description', ''),
                                        'attendees': meeting_info.get('attendees', [])
                                    }

                                    calendar_response = api_client.post(
                                        API_ENDPOINTS['calendar_events'],
                                        event_request,
                                        include_auth=True
                                    )

                                    progress_placeholder.empty()

                                    if calendar_response and calendar_response.get('success'):
                                        # Enhanced success feedback
                                        success_message = f"✅ Event '{calendar_response['title']}' created successfully!"

                                        # Show success with balloons
                                        st.balloons()
                                        st.success(success_message)

                                        if calendar_response.get('event_link'):
                                            st.markdown(f"""
                                            <div style="text-align: center; margin: 1rem 0;">
                                                <a href="{calendar_response['event_link']}" target="_blank" style="
                                                    display: inline-block;
                                                    background: linear-gradient(135deg, #28a745, #20c997);
                                                    color: white;
                                                    padding: 12px 24px;
                                                    text-decoration: none;
                                                    border-radius: 25px;
                                                    font-weight: 600;
                                                    box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
                                                ">🔗 View in Google Calendar</a>
                                            </div>
                                            """, unsafe_allow_html=True)

                                        # Add success message to conversation
                                        st.session_state.messages.append({
                                            'role': 'assistant',
                                            'content': success_message,
                                            'timestamp': datetime.now()
                                        })
                                    else:
                                        error_msg = f"❌ Failed to create event: {calendar_response.get('error', 'Unknown error') if calendar_response else 'API error'}"
                                        st.error(error_msg)

                                        st.session_state.messages.append({
                                            'role': 'assistant',
                                            'content': error_msg,
                                            'timestamp': datetime.now()
                                        })
                                else:
                                    progress_placeholder.empty()
                                    st.warning("⚠️ Could not extract meeting details from the conversation.")
                            else:
                                progress_placeholder.empty()
                                st.error("❌ Failed to extract meeting information.")
                    elif action == "CREATE_EVENT" and not st.session_state.google_calendar_connected:
                        progress_placeholder.empty()
                        st.warning("⚠️ Please connect your Google Calendar first to create events.")
                else:
                    progress_placeholder.empty()
                    st.error("❌ Failed to get AI response from backend")

            except Exception as e:
                progress_placeholder.empty()
                error_message = f"I apologize, but I encountered an error: {str(e)}"
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': error_message,
                    'timestamp': datetime.now()
                })
                st.error(f"❌ Error processing message: {str(e)}")

        st.rerun()

    # Footer with helpful information
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 15px; margin-top: 2rem;">
        <h4 style="color: #667eea; margin-bottom: 1rem;">💡 Tips for Better Results</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; text-align: left;">
            <div>
                <strong>📅 Scheduling:</strong><br>
                "Schedule a meeting with John tomorrow at 2 PM"
            </div>
            <div>
                <strong>🔍 Availability:</strong><br>
                "What's my availability this week?"
            </div>
            <div>
                <strong>📋 Events:</strong><br>
                "Show me my meetings for today"
            </div>
        </div>
        <p style="margin-top: 1rem; color: #6c757d; font-size: 0.9em;">
            Agentic Calendar works best with specific dates, times, and attendee information.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
