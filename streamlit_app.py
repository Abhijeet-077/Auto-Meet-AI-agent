import streamlit as st
import os
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any
import json

# Simplified imports for bulletproof deployment
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    st.error("Google Generative AI not available. Please check your deployment configuration.")

# Simple service classes embedded in main file to avoid import issues
class SimpleGeminiService:
    def __init__(self):
        st.info("🔄 Initializing Gemini AI service...")

        # Check if Gemini library is available
        if not GEMINI_AVAILABLE:
            st.error("❌ Google Generative AI library not available")
            self.api_key = None
            self.model = None
            return

        # Get API key
        self.api_key = self._get_api_key()
        self.model = None

        if not self.api_key:
            st.error("❌ No API key found - Gemini service not initialized")
            return

        # Initialize Gemini model
        try:
            st.info("🔧 Configuring Gemini API...")
            genai.configure(api_key=self.api_key)

            st.info("🤖 Creating Gemini model...")
            self.model = genai.GenerativeModel('gemini-1.5-flash')

            st.success("✅ Gemini AI service initialized successfully!")

        except Exception as e:
            st.error(f"❌ Error initializing Gemini model: {e}")
            st.error(f"🔍 Error type: {type(e).__name__}")
            st.error(f"🔍 Error details: {str(e)}")
            self.model = None

    def _get_api_key(self) -> str:
        """Get Gemini API key from Streamlit secrets or environment variables"""
        api_key = None

        # Method 1: Try Streamlit secrets (for cloud deployment)
        try:
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                api_key = st.secrets['GEMINI_API_KEY']
                if api_key and api_key.strip():
                    st.info(f"🔑 API key loaded from Streamlit secrets: {api_key[:10]}...{api_key[-4:]}")
                    return api_key.strip()
        except Exception as e:
            st.warning(f"⚠️ Error accessing Streamlit secrets: {e}")

        # Method 2: Try environment variables (for local development)
        try:
            import os
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key and api_key.strip() and api_key != 'PLACEHOLDER_API_KEY':
                st.info(f"🔑 API key loaded from environment: {api_key[:10]}...{api_key[-4:]}")
                return api_key.strip()
        except Exception as e:
            st.warning(f"⚠️ Error accessing environment variables: {e}")

        # Method 3: Hardcoded for testing (REMOVE IN PRODUCTION)
        # Temporarily enabled for troubleshooting - should be removed for security
        test_api_key = "AIzaSyBn-kcJcmzPzxqmu4U-nAQXpUiWa9XRWCQ"
        if test_api_key:
            st.warning(f"🧪 Using hardcoded API key for testing: {test_api_key[:10]}...{test_api_key[-4:]}")
            st.warning("⚠️ SECURITY WARNING: Remove hardcoded API key in production!")
            return test_api_key

        # No API key found
        st.error("❌ No GEMINI_API_KEY found in secrets or environment variables")
        return None

    def is_configured(self) -> bool:
        """Check if Gemini service is properly configured"""
        configured = self.model is not None

        if not configured:
            st.warning("⚠️ Gemini service is not configured")
            if not GEMINI_AVAILABLE:
                st.error("📦 Google Generative AI library not available")
            elif not self.api_key:
                st.error("🔑 No API key found")
            else:
                st.error("🤖 Model initialization failed")

        return configured

    def get_response(self, user_message: str, chat_history: List[Dict], calendar_connected: bool = False) -> str:
        if not self.model:
            error_msg = "I apologize, but I'm not properly configured. "
            if not GEMINI_AVAILABLE:
                error_msg += "The Google Generative AI library is not available. Please check your deployment configuration."
            elif not self.api_key:
                error_msg += "Please ensure the GEMINI_API_KEY is set in Streamlit Cloud secrets."
            else:
                error_msg += "The Gemini model failed to initialize. Please check the API key and try again."
            return error_msg

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
    st.session_state.gemini_service = SimpleGeminiService()

# Initialize services
def initialize_services():
    """Initialize services with error handling"""
    try:
        # Gemini service is already initialized in session state
        if not st.session_state.gemini_service.is_configured():
            st.error("🚨 Gemini AI is not properly configured. Please check your API key.")
            with st.expander("🔧 Gemini AI Setup Instructions"):
                st.markdown("""
                **To configure Gemini AI:**

                1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
                2. Add it to Streamlit Cloud secrets:
                   ```toml
                   GEMINI_API_KEY = "your_api_key_here"
                   ```
                3. Restart the application

                **Current Status:** API key not found or invalid
                """)
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {str(e)}")
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
            st.info("📅 Calendar: Demo Mode Available")

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
                st.success("🔓 Disconnected from Google Calendar")
                st.rerun()
        else:
            st.markdown("""
            <div class="calendar-status disconnected">
                ❌ Not Connected
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔗 Connect Google Calendar", type="primary"):
                # Demo connection for deployment testing
                st.session_state.google_calendar_connected = True
                st.session_state.google_user_info = {
                    'name': 'Demo User',
                    'email': 'demo@example.com'
                }
                st.success("✅ Calendar connected successfully! (Demo Mode)")
                st.info("💡 This is a demo connection for testing deployment. Full OAuth integration can be added later.")
                st.rerun()

            st.markdown("""
            <small>
            <strong>Note:</strong> Demo mode for testing deployment.
            Real Google Calendar integration can be added after successful deployment.
            </small>
            """, unsafe_allow_html=True)

        # Debug panel
        st.header("🔧 Debug Information")
        with st.expander("🐛 Gemini AI Debug Info"):
            st.write("**Library Status:**")
            st.write(f"- Google Generative AI Available: {'✅' if GEMINI_AVAILABLE else '❌'}")

            if st.session_state.gemini_service:
                st.write("**Service Status:**")
                st.write(f"- API Key Found: {'✅' if st.session_state.gemini_service.api_key else '❌'}")
                st.write(f"- Model Initialized: {'✅' if st.session_state.gemini_service.model else '❌'}")
                st.write(f"- Service Configured: {'✅' if st.session_state.gemini_service.is_configured() else '❌'}")

                if st.session_state.gemini_service.api_key:
                    api_key = st.session_state.gemini_service.api_key
                    st.write(f"- API Key Preview: {api_key[:10]}...{api_key[-4:]}")
                    st.write(f"- API Key Length: {len(api_key)} characters")

            st.write("**Secrets Check:**")
            try:
                if hasattr(st, 'secrets'):
                    secrets_available = 'GEMINI_API_KEY' in st.secrets
                    st.write(f"- Streamlit Secrets Available: ✅")
                    st.write(f"- GEMINI_API_KEY in Secrets: {'✅' if secrets_available else '❌'}")
                    if secrets_available:
                        secret_key = st.secrets['GEMINI_API_KEY']
                        st.write(f"- Secret Key Preview: {secret_key[:10]}...{secret_key[-4:]}")
                else:
                    st.write(f"- Streamlit Secrets Available: ❌")
            except Exception as e:
                st.write(f"- Secrets Error: {e}")

            if st.button("🔄 Reinitialize Gemini Service"):
                st.session_state.gemini_service = SimpleGeminiService()
                st.rerun()

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