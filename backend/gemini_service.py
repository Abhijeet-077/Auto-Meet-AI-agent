import os
import google.generativeai as genai
from typing import List, Dict, Any
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv('.env.local')

class GeminiService:
    """Service class for handling Gemini AI interactions"""
    
    def __init__(self):
        """Initialize the Gemini service with API key"""
        self.api_key = self._get_api_key()
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use the correct model name for Gemini 1.5
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def _get_api_key(self) -> str:
        """Get Gemini API key from environment or Streamlit secrets"""
        # Try to get from Streamlit secrets first (for cloud deployment)
        try:
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                return st.secrets['GEMINI_API_KEY']
        except:
            pass

        # Fall back to environment variable
        api_key = os.getenv('GEMINI_API_KEY')

        # Check if it's the placeholder or empty
        if not api_key or api_key == 'PLACEHOLDER_API_KEY':
            return None

        return api_key
    
    def get_system_prompt(self, calendar_connected: bool = False) -> str:
        """Get the system prompt for TailorTalk"""
        base_prompt = """You are TailorTalk, a friendly and highly efficient AI assistant specialized in scheduling appointments using Google Calendar. Your goal is to seamlessly guide users through booking appointments.

Key capabilities:
1. **Natural Conversation:** Engage in clear, polite, and back-and-forth dialogue.
2. **Intent Understanding:** Accurately determine if a user wants to schedule, modify, or cancel an appointment.
3. **Google Calendar Integration:**"""
        
        if calendar_connected:
            calendar_prompt = """
   * **Connected:** The user has connected their Google Calendar.
   * **Permission:** Before accessing their calendar (reading or writing), always ask for explicit confirmation for the specific action.
   * **Information Gathering:** If necessary, ask clarifying questions like 'What day and time are you considering?', 'For how long do you need the slot?', or 'What is the purpose of this meeting?'.
   * **Availability Check:** When asked about availability (and after user confirms access), check the actual Google Calendar for busy times.
   * **Event Creation:** Once a user agrees to a time slot and confirms booking, create the event in their calendar.
   * **Confirmation:** Confirm successful bookings or inform about failures politely."""
        else:
            calendar_prompt = """
   * **Connection Check:** The user has NOT connected their Google Calendar yet. If they try to perform a calendar action (check availability, book), politely ask them to connect it using the "Connect Google Calendar" button in the sidebar. Example: "To help you with that, I'll need access to your Google Calendar. Could you please connect it using the button in the sidebar?"
   * **No Calendar Actions:** Until connected, you cannot check availability or book appointments."""
        
        ending_prompt = """
4. **Politeness:** Always maintain a friendly and helpful tone.
5. **Conciseness:** Keep responses concise but informative.
6. **Clarification:** If the user's request is ambiguous (e.g., "next week", "afternoon"), ask for more specific details.
7. **Timezone Awareness:** Remind users that scheduling is based on their local timezone.

Do not ask for personal information beyond what's needed for scheduling.
Assume the current year if not specified.
When suggesting dates or times, be specific (e.g., 'Wednesday, July 24th at 3:00 PM').
"""
        
        return base_prompt + calendar_prompt + ending_prompt
    
    def format_chat_history(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format chat history for Gemini API"""
        formatted_history = []
        
        for message in messages:
            if message['role'] == 'user':
                formatted_history.append({
                    'role': 'user',
                    'parts': [message['content']]
                })
            elif message['role'] == 'assistant':
                formatted_history.append({
                    'role': 'model',
                    'parts': [message['content']]
                })
        
        return formatted_history
    
    def get_response(self, user_message: str, chat_history: List[Dict[str, Any]], calendar_connected: bool = False) -> str:
        """Get response from Gemini AI"""
        if not self.model:
            return "I apologize, but I'm not properly configured. Please ensure the GEMINI_API_KEY is set correctly."
        
        try:
            # Create system prompt based on calendar connection status
            system_prompt = self.get_system_prompt(calendar_connected)
            
            # Format the conversation for Gemini
            formatted_history = self.format_chat_history(chat_history)
            
            # Create the full prompt with system instructions
            full_prompt = f"{system_prompt}\n\nConversation history:\n"
            
            # Add conversation history
            for msg in formatted_history:
                role = "User" if msg['role'] == 'user' else "TailorTalk"
                full_prompt += f"{role}: {msg['parts'][0]}\n"
            
            # Add current user message
            full_prompt += f"User: {user_message}\nTailorTalk:"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                return response.text.strip()
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            error_msg = str(e)
            if "API_KEY" in error_msg.upper():
                return "I'm having trouble connecting to my AI service. Please check that the GEMINI_API_KEY is properly configured."
            else:
                return f"I encountered an error while processing your request: {error_msg}"
    
    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return self.model is not None and self.api_key is not None
