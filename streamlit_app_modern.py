"""
Agentic Calendar - Modern Streamlit Frontend
Professional, clean, and interactive dashboard design
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
    """Modern API client with enhanced error handling"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.session.timeout = 30
    
    def _get_headers(self, include_auth: bool = False) -> Dict[str, str]:
        headers = {'Content-Type': 'application/json'}
        if include_auth and 'access_token' in st.session_state:
            headers['Authorization'] = f"Bearer {st.session_state.access_token}"
        return headers
    
    def get(self, endpoint: str, include_auth: bool = False) -> Optional[Dict[str, Any]]:
        try:
            response = self.session.get(endpoint, headers=self._get_headers(include_auth))
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return None
    
    def post(self, endpoint: str, data: Dict[str, Any], include_auth: bool = False) -> Optional[Dict[str, Any]]:
        try:
            response = self.session.post(endpoint, json=data, headers=self._get_headers(include_auth))
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
    page_title="Agentic Calendar - AI Meeting Scheduler",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Professional CSS Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* CSS Variables for Design System */
    :root {
        --primary-50: #f0f9ff;
        --primary-100: #e0f2fe;
        --primary-500: #0ea5e9;
        --primary-600: #0284c7;
        --primary-700: #0369a1;
        --primary-900: #0c4a6e;
        
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-300: #cbd5e1;
        --gray-400: #94a3b8;
        --gray-500: #64748b;
        --gray-600: #475569;
        --gray-700: #334155;
        --gray-800: #1e293b;
        --gray-900: #0f172a;
        
        --success-50: #f0fdf4;
        --success-500: #22c55e;
        --success-600: #16a34a;
        
        --warning-50: #fffbeb;
        --warning-500: #f59e0b;
        --warning-600: #d97706;
        
        --error-50: #fef2f2;
        --error-500: #ef4444;
        --error-600: #dc2626;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
    }

    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, var(--gray-50) 0%, var(--primary-50) 100%);
        min-height: 100vh;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--gray-100);
        border-radius: var(--radius-md);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gray-300);
        border-radius: var(--radius-md);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--gray-400);
    }

    /* Modern Header */
    .modern-header {
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
        color: white;
        padding: 2rem;
        border-radius: var(--radius-xl);
        margin-bottom: 2rem;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
    }

    .modern-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.3;
    }

    .modern-header-content {
        position: relative;
        z-index: 1;
        text-align: center;
    }

    .modern-header h1 {
        margin: 0 0 0.5rem 0;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, #ffffff 0%, rgba(255,255,255,0.8) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .modern-header p {
        margin: 0;
        font-size: 1.125rem;
        opacity: 0.9;
        font-weight: 400;
    }

    /* Modern Cards */
    .modern-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }

    .modern-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-1px);
    }

    .modern-card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--gray-200);
    }

    .modern-card-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--gray-900);
        margin: 0;
    }

    .modern-card-icon {
        width: 1.5rem;
        height: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--primary-100);
        border-radius: var(--radius-md);
        color: var(--primary-600);
        font-size: 0.875rem;
    }

    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        border-radius: var(--radius-md);
        font-size: 0.875rem;
        font-weight: 500;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }

    .status-healthy {
        background: var(--success-50);
        color: var(--success-600);
        border-color: var(--success-200);
    }

    .status-warning {
        background: var(--warning-50);
        color: var(--warning-600);
        border-color: var(--warning-200);
    }

    .status-error {
        background: var(--error-50);
        color: var(--error-600);
        border-color: var(--error-200);
    }

    /* Modern Buttons */
    .stButton > button {
        background: var(--primary-600) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button:hover {
        background: var(--primary-700) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* Chat Interface */
    .chat-container {
        background: white;
        border-radius: var(--radius-lg);
        border: 1px solid var(--gray-200);
        max-height: 500px;
        overflow-y: auto;
        margin-bottom: 1.5rem;
        position: relative;
    }

    /* Watermark */
    .chat-container::before {
        content: 'Abhijeet Swami';
        position: absolute;
        top: 50%;
        right: 20%;
        transform: translate(50%, -50%) rotate(-45deg);
        font-size: 4rem;
        font-weight: 800;
        color: var(--gray-300);
        opacity: 0.08;
        z-index: 1;
        pointer-events: none;
        user-select: none;
        white-space: nowrap;
    }

    .message-container {
        padding: 1rem;
        border-bottom: 1px solid var(--gray-100);
        position: relative;
        z-index: 2;
    }

    .message-container:last-child {
        border-bottom: none;
    }

    .user-message {
        background: var(--primary-600);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg);
        margin-left: 20%;
        font-weight: 500;
        box-shadow: var(--shadow-sm);
    }

    .assistant-message {
        background: var(--gray-100);
        color: var(--gray-900);
        padding: 0.75rem 1rem;
        border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm);
        margin-right: 20%;
        font-weight: 500;
        border: 1px solid var(--gray-200);
    }

    /* Sidebar Styling */
    .sidebar-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
    }

    /* Connection Status */
    .connection-status {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        border-radius: var(--radius-md);
        margin: 1rem 0;
        font-weight: 500;
        border: 1px solid;
    }

    .connection-connected {
        background: var(--success-50);
        color: var(--success-600);
        border-color: var(--success-200);
    }

    .connection-disconnected {
        background: var(--warning-50);
        color: var(--warning-600);
        border-color: var(--warning-200);
    }

    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid var(--gray-200);
        border-radius: 50%;
        border-top-color: var(--primary-600);
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .modern-header h1 {
            font-size: 2rem;
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

def render_modern_header():
    """Render modern header component"""
    st.markdown("""
    <div class="modern-header">
        <div class="modern-header-content">
            <h1>🤖 Agentic Calendar</h1>
            <p>Intelligent Meeting Scheduler & Calendar Management</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_status_dashboard():
    """Render modern status dashboard"""
    # Check backend health
    backend_healthy, health_data = check_backend_health()

    if not backend_healthy:
        st.markdown("""
        <div class="modern-card">
            <div class="modern-card-header">
                <div class="modern-card-icon">🚨</div>
                <h3 class="modern-card-title">Backend Offline</h3>
            </div>
            <p style="color: var(--gray-600); margin-bottom: 1rem;">The FastAPI backend is not available. Please start the server to continue.</p>
            <div style="background: var(--gray-50); padding: 1rem; border-radius: var(--radius-md); font-family: 'JetBrains Mono', monospace; font-size: 0.875rem;">
                <strong>To start the backend:</strong><br>
                cd backend_api<br>
                uvicorn main:app --reload --host 127.0.0.1 --port 8000
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Service status grid
    col1, col2, col3 = st.columns(3)

    with col1:
        ai_status = health_data and health_data.get('services', {}).get('gemini') == 'configured'
        status_class = "status-healthy" if ai_status else "status-error"
        icon = "🤖" if ai_status else "⚠️"
        text = "AI Ready" if ai_status else "AI Not Configured"
        st.markdown(f'<div class="status-indicator {status_class}"><span>{icon}</span> {text}</div>', unsafe_allow_html=True)

    with col2:
        calendar_status = st.session_state.google_calendar_connected
        status_class = "status-healthy" if calendar_status else "status-warning"
        icon = "📅" if calendar_status else "📅"
        text = "Calendar Connected" if calendar_status else "Calendar Disconnected"
        st.markdown(f'<div class="status-indicator {status_class}"><span>{icon}</span> {text}</div>', unsafe_allow_html=True)

    with col3:
        status_class = "status-healthy" if backend_healthy else "status-error"
        icon = "🔗" if backend_healthy else "❌"
        text = "Backend Online" if backend_healthy else "Backend Offline"
        st.markdown(f'<div class="status-indicator {status_class}"><span>{icon}</span> {text}</div>', unsafe_allow_html=True)

def render_sidebar():
    """Render modern sidebar"""
    with st.sidebar:
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### 🔗 Google Calendar Integration")

        if st.session_state.google_calendar_connected:
            # Connected state
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
                                background: var(--primary-600);
                                color: white;
                                padding: 12px 24px;
                                text-decoration: none;
                                border-radius: var(--radius-md);
                                font-weight: 600;
                                margin: 10px 0;
                                box-shadow: var(--shadow-md);
                                transition: all 0.2s ease;
                            ">🔗 Authorize Google Calendar Access</a>

                            After authorization, you'll be redirected back to this page.
                            """, unsafe_allow_html=True)
                            st.info("💡 A new tab will open for Google authorization.")
                        else:
                            st.error("❌ Failed to generate authorization URL")
            else:
                st.markdown("""
                <div style="background: var(--warning-50); padding: 1rem; border-radius: var(--radius-md); border-left: 4px solid var(--warning-500);">
                    <strong>⚠️ OAuth Not Configured</strong><br>
                    Please configure your Google OAuth credentials.
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Tips section in sidebar
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### 💡 Tips for Better Results")

        st.markdown("""
        **📅 Scheduling:**
        "Schedule a meeting with John tomorrow at 2 PM"

        **🔍 Availability:**
        "What's my availability this week?"

        **📋 Events:**
        "Show me my meetings for today"
        """)

        st.markdown("""
        <div style="margin-top: 1rem; padding: 0.75rem; background: var(--primary-50); border-radius: var(--radius-md); border-left: 3px solid var(--primary-500);">
            <small style="color: var(--gray-600);">
                💡 Agentic Calendar works best with specific dates, times, and attendee information.
            </small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

def render_chat_interface():
    """Render clean, centered chat interface"""
    # Clean header for chat section
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: var(--gray-800); font-weight: 600; margin-bottom: 0.5rem;">💬 Chat with Agentic Calendar</h2>
        <p style="color: var(--gray-600); font-size: 1rem;">Ask me to schedule meetings, check your calendar, or help with appointments!</p>
    </div>
    """, unsafe_allow_html=True)

    # Chat container
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

        st.markdown('<div class="message-container">', unsafe_allow_html=True)

        if role == 'user':
            st.markdown(f"""
            <div class="user-message">
                {content}
                <div style="font-size: 0.75rem; opacity: 0.8; margin-top: 0.5rem; text-align: right;">
                    {time_str}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2em;">🤖</span>
                    <strong style="color: var(--primary-600);">Agentic Calendar</strong>
                </div>
                {content}
                <div style="font-size: 0.75rem; opacity: 0.7; margin-top: 0.5rem;">
                    {time_str}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



def main():
    """Main application function"""
    # Handle OAuth callback first
    handle_oauth_callback()

    # Render modern header
    render_modern_header()

    # Render status dashboard
    render_status_dashboard()

    # Render sidebar
    render_sidebar()

    # Main content area - Clean centered chat interface
    render_chat_interface()

    # Chat input
    user_input = st.chat_input(
        "Type your message here... (e.g., 'Schedule a meeting with John tomorrow at 2 PM')",
        key="chat_input"
    )

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

        # Process with AI
        with st.spinner("🤖 Agentic Calendar is thinking..."):
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

                    # Handle actions
                    if action == "CREATE_EVENT" and st.session_state.google_calendar_connected:
                        with st.spinner("📅 Creating calendar event..."):
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

                                    if calendar_response and calendar_response.get('success'):
                                        success_message = f"✅ Event '{calendar_response['title']}' created successfully!"
                                        st.balloons()
                                        st.success(success_message)

                                        if calendar_response.get('event_link'):
                                            st.markdown(f"""
                                            <div style="text-align: center; margin: 1rem 0;">
                                                <a href="{calendar_response['event_link']}" target="_blank" style="
                                                    display: inline-block;
                                                    background: var(--success-600);
                                                    color: white;
                                                    padding: 12px 24px;
                                                    text-decoration: none;
                                                    border-radius: var(--radius-md);
                                                    font-weight: 600;
                                                    box-shadow: var(--shadow-md);
                                                ">🔗 View in Google Calendar</a>
                                            </div>
                                            """, unsafe_allow_html=True)

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
                                    st.warning("⚠️ Could not extract meeting details from the conversation.")
                            else:
                                st.error("❌ Failed to extract meeting information.")
                    elif action == "CREATE_EVENT" and not st.session_state.google_calendar_connected:
                        st.warning("⚠️ Please connect your Google Calendar first to create events.")
                else:
                    st.error("❌ Failed to get AI response from backend")

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
