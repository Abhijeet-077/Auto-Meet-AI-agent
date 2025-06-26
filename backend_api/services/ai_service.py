"""
AI Service for Agentic Calendar
Multi-provider AI integration for intelligent meeting scheduling
Supports: Google Gemini, OpenAI GPT, Anthropic Claude, and Demo Mode
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env.local')

class BaseAIProvider:
    """Base class for AI providers"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    async def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat message - to be implemented by subclasses"""
        raise NotImplementedError

    def is_configured(self) -> bool:
        """Check if provider is properly configured"""
        return bool(self.api_key)

class DemoAIProvider(BaseAIProvider):
    """Demo AI provider with simulated responses"""

    def __init__(self):
        super().__init__()

    async def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Provide demo responses"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create']):
            return {
                "response": "I'd be happy to help you schedule a meeting! I can see you want to create an appointment. Please provide details like the date, time, duration, and attendees, and I'll help you set it up in your calendar.",
                "action": "CREATE_EVENT",
                "meeting_info": {
                    "title": "Demo Meeting",
                    "date": "2024-01-15",
                    "time": "14:00",
                    "duration": 60,
                    "attendees": []
                }
            }
        elif any(word in message_lower for word in ['availability', 'available', 'free']):
            return {
                "response": "I can help you check your availability! Based on your calendar, you have several free slots this week. Would you like me to show you specific available times?",
                "action": "CHECK_AVAILABILITY"
            }
        else:
            return {
                "response": "Hello! I'm your AI calendar assistant. I can help you schedule meetings, check availability, and manage your calendar. What would you like to do today?",
                "action": "GENERAL"
            }

    def is_configured(self) -> bool:
        """Demo mode is always configured"""
        return True

class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize Gemini model"""
        if not self.api_key:
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except ImportError:
            self.model = None
        except Exception:
            self.model = None
    
    async def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat with Gemini"""
        if not self.model:
            return {
                "response": "I apologize, but Gemini AI is not properly configured. Please check the API key.",
                "action": "GENERAL"
            }

        try:
            # Build conversation context
            context = self._build_context(message, chat_history)

            # Generate response
            response = self.model.generate_content(context)

            # Parse response and determine action
            response_text = response.text
            action = self._determine_action(message)

            result = {
                "response": response_text,
                "action": action
            }

            # Extract meeting info if needed
            if action == "CREATE_EVENT":
                meeting_info = self._extract_meeting_info(message, response_text)
                if meeting_info:
                    result["meeting_info"] = meeting_info

            return result

        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}",
                "action": "GENERAL"
            }

    def _build_context(self, message: str, chat_history: List[Dict] = None) -> str:
        """Build context for Gemini"""
        system_prompt = """You are an AI assistant specialized in scheduling appointments using Google Calendar.

        When users want to schedule meetings, help them by:
        1. Gathering required information (title, date, time, duration, attendees)
        2. Providing clear, helpful responses
        3. Being friendly and professional

        If you have all the information needed to create a meeting, indicate this clearly."""

        context = system_prompt + "\n\nConversation:\n"

        if chat_history:
            for msg in chat_history[-10:]:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                context += f"{role.title()}: {content}\n"

        context += f"User: {message}\nAssistant:"
        return context

    def _determine_action(self, message: str) -> str:
        """Determine action from message"""
        message_lower = message.lower()
        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create', 'appointment']):
            return 'CREATE_EVENT'
        elif any(word in message_lower for word in ['availability', 'available', 'free', 'busy']):
            return 'CHECK_AVAILABILITY'
        elif any(word in message_lower for word in ['show', 'view', 'list', 'events', 'calendar']):
            return 'VIEW_EVENTS'
        else:
            return 'GENERAL'

    def _extract_meeting_info(self, message: str, response: str) -> Optional[Dict[str, Any]]:
        """Extract meeting information from message and response"""
        # Simple extraction - in a real implementation, this would be more sophisticated
        info = {}

        # Try to extract basic information
        if 'meeting' in message.lower() or 'appointment' in message.lower():
            info['title'] = 'Meeting'
            info['date'] = '2024-01-15'  # Default date
            info['time'] = '14:00'       # Default time
            info['duration'] = 60        # Default duration
            info['attendees'] = []

        return info if info else None

    def is_configured(self) -> bool:
        """Check if Gemini is properly configured"""
        return bool(self.api_key and self.model)

class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key)
        self.model_name = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client"""
        if not self.api_key:
            return

        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            self.client = None
        except Exception:
            self.client = None

    async def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat with OpenAI"""
        if not self.client:
            return {
                "response": "I apologize, but OpenAI is not properly configured. Please check the API key.",
                "action": "GENERAL"
            }

        try:
            # Build messages for OpenAI format
            messages = self._build_openai_messages(message, chat_history)

            # Generate response
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            response_text = response.choices[0].message.content
            action = self._determine_action(message)

            result = {
                "response": response_text,
                "action": action
            }

            # Extract meeting info if needed
            if action == "CREATE_EVENT":
                meeting_info = self._extract_meeting_info(message, response_text)
                if meeting_info:
                    result["meeting_info"] = meeting_info

            return result

        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}",
                "action": "GENERAL"
            }

    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return bool(self.api_key and self.client)

    def _build_openai_messages(self, message: str, chat_history: List[Dict] = None) -> List[Dict]:
        """Build messages for OpenAI format"""
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant specialized in scheduling appointments using Google Calendar. Help users schedule meetings by gathering required information and providing clear, helpful responses."
            }
        ]

        if chat_history:
            for msg in chat_history[-10:]:
                role = msg.get('role', 'user')
                if role == 'assistant':
                    role = 'assistant'
                content = msg.get('content', '')
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": message})
        return messages

    def _determine_action(self, message: str) -> str:
        """Determine action from message"""
        message_lower = message.lower()
        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create', 'appointment']):
            return 'CREATE_EVENT'
        elif any(word in message_lower for word in ['availability', 'available', 'free', 'busy']):
            return 'CHECK_AVAILABILITY'
        elif any(word in message_lower for word in ['show', 'view', 'list', 'events', 'calendar']):
            return 'VIEW_EVENTS'
        else:
            return 'GENERAL'

    def _extract_meeting_info(self, message: str, response: str) -> Optional[Dict[str, Any]]:
        """Extract meeting information from message and response"""
        # Simple extraction - in a real implementation, this would be more sophisticated
        info = {}

        # Try to extract basic information
        if 'meeting' in message.lower() or 'appointment' in message.lower():
            info['title'] = 'Meeting'
            info['date'] = '2024-01-15'  # Default date
            info['time'] = '14:00'       # Default time
            info['duration'] = 60        # Default duration
            info['attendees'] = []

        return info if info else None
    
class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        super().__init__(api_key)
        self.model_name = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Claude client"""
        if not self.api_key:
            return

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            self.client = None
        except Exception:
            self.client = None

    async def chat(self, message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat with Claude"""
        if not self.client:
            return {
                "response": "I apologize, but Claude is not properly configured. Please check the API key.",
                "action": "GENERAL"
            }

        try:
            # Build messages for Claude format
            messages = self._build_claude_messages(message, chat_history)

            # Generate response
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=500,
                messages=messages
            )

            response_text = response.content[0].text
            action = self._determine_action(message)

            result = {
                "response": response_text,
                "action": action
            }

            # Extract meeting info if needed
            if action == "CREATE_EVENT":
                meeting_info = self._extract_meeting_info(message, response_text)
                if meeting_info:
                    result["meeting_info"] = meeting_info

            return result

        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}",
                "action": "GENERAL"
            }

    def is_configured(self) -> bool:
        """Check if Claude is properly configured"""
        return bool(self.api_key and self.client)

    def _build_claude_messages(self, message: str, chat_history: List[Dict] = None) -> List[Dict]:
        """Build messages for Claude format"""
        messages = []

        if chat_history:
            for msg in chat_history[-10:]:
                role = msg.get('role', 'user')
                if role == 'assistant':
                    role = 'assistant'
                content = msg.get('content', '')
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": message})
        return messages

    def _determine_action(self, message: str) -> str:
        """Determine action from message"""
        message_lower = message.lower()
        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create', 'appointment']):
            return 'CREATE_EVENT'
        elif any(word in message_lower for word in ['availability', 'available', 'free', 'busy']):
            return 'CHECK_AVAILABILITY'
        elif any(word in message_lower for word in ['show', 'view', 'list', 'events', 'calendar']):
            return 'VIEW_EVENTS'
        else:
            return 'GENERAL'

    def _extract_meeting_info(self, message: str, response: str) -> Optional[Dict[str, Any]]:
        """Extract meeting information from message and response"""
        # Simple extraction - in a real implementation, this would be more sophisticated
        info = {}

        # Try to extract basic information
        if 'meeting' in message.lower() or 'appointment' in message.lower():
            info['title'] = 'Meeting'
            info['date'] = '2024-01-15'  # Default date
            info['time'] = '14:00'       # Default time
            info['duration'] = 60        # Default duration
            info['attendees'] = []

        return info if info else None

class AIService:
    """Multi-provider AI service for conversation and meeting scheduling"""

    def __init__(self):
        """Initialize AI service with multi-provider support"""
        self.providers = {
            'demo': DemoAIProvider(),
            'gemini': None,
            'openai': None,
            'claude': None
        }
        self.current_provider = 'demo'
        self._initialize_default_provider()

    def _initialize_default_provider(self):
        """Initialize default provider based on available API keys"""
        # Check for Gemini (legacy support)
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        if gemini_key and gemini_key not in ['your_gemini_api_key_here']:
            self.providers['gemini'] = GeminiProvider(gemini_key)
            self.current_provider = 'gemini'
            return

        # Check for OpenAI
        openai_key = os.getenv('OPENAI_API_KEY', '')
        if openai_key and openai_key not in ['your_openai_api_key_here']:
            self.providers['openai'] = OpenAIProvider(openai_key)
            self.current_provider = 'openai'
            return

        # Check for Claude
        claude_key = os.getenv('CLAUDE_API_KEY', '')
        if claude_key and claude_key not in ['your_claude_api_key_here']:
            self.providers['claude'] = ClaudeProvider(claude_key)
            self.current_provider = 'claude'
            return

        # Default to demo mode
        self.current_provider = 'demo'

    def set_provider(self, provider_name: str, api_key: str = None, model: str = None):
        """Set the active AI provider"""
        if provider_name == 'demo':
            self.providers['demo'] = DemoAIProvider()
            self.current_provider = 'demo'
        elif provider_name == 'gemini' and api_key:
            self.providers['gemini'] = GeminiProvider(api_key)
            self.current_provider = 'gemini'
        elif provider_name == 'openai' and api_key:
            model = model or 'gpt-3.5-turbo'
            self.providers['openai'] = OpenAIProvider(api_key, model)
            self.current_provider = 'openai'
        elif provider_name == 'claude' and api_key:
            model = model or 'claude-3-haiku-20240307'
            self.providers['claude'] = ClaudeProvider(api_key, model)
            self.current_provider = 'claude'

    def get_current_provider(self) -> BaseAIProvider:
        """Get current provider instance"""
        return self.providers[self.current_provider]

    def get_current_provider_info(self) -> Dict[str, Any]:
        """Get information about current provider"""
        provider_info = {
            'demo': {'name': 'Demo Mode', 'icon': '🎯', 'key': 'demo'},
            'gemini': {'name': 'Google Gemini', 'icon': '🧠', 'key': 'gemini'},
            'openai': {'name': 'OpenAI GPT', 'icon': '🤖', 'key': 'openai'},
            'claude': {'name': 'Anthropic Claude', 'icon': '🎭', 'key': 'claude'}
        }
        return provider_info.get(self.current_provider, {'name': 'Unknown', 'icon': '❓', 'key': 'unknown'})

    async def get_response(self, user_message: str, chat_history: List[Dict],
                          calendar_connected: bool = False) -> Dict[str, Any]:
        """Get AI response using current provider"""
        provider = self.get_current_provider()
        if not provider:
            return {
                "response": "I apologize, but no AI provider is available.",
                "action": "GENERAL"
            }
        
        try:
            result = await provider.chat(user_message, chat_history)

            # Add provider info to result
            result['provider'] = self.get_current_provider_info()
            result['calendar_connected'] = calendar_connected

            return result

        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}",
                "action": "GENERAL",
                "provider": self.get_current_provider_info()
            }

    def is_configured(self) -> bool:
        """Check if current provider is configured"""
        provider = self.get_current_provider()
        return provider and provider.is_configured()

    def get_model_name(self) -> str:
        """Get current model name"""
        if self.current_provider == 'demo':
            return "demo-mode"
        elif self.current_provider == 'gemini':
            return "gemini-1.5-flash"
        elif self.current_provider == 'openai':
            provider = self.providers.get('openai')
            return provider.model_name if provider else "gpt-3.5-turbo"
        elif self.current_provider == 'claude':
            provider = self.providers.get('claude')
            return provider.model_name if provider else "claude-3-haiku-20240307"
        else:
            return "unknown"
    
    def _extract_action(self, response_text: str) -> Optional[str]:
        """Extract action indicator from response"""
        if "[ACTION:CREATE_EVENT]" in response_text:
            return "CREATE_EVENT"
        elif "[ACTION:NEED_INFO]" in response_text:
            return "NEED_INFO"
        return None
    
    def _clean_response_text(self, response_text: str) -> str:
        """Remove action indicators from response text"""
        # Remove action indicators
        clean_text = re.sub(r'\[ACTION:[^\]]+\]', '', response_text)
        return clean_text.strip()
    
    async def extract_meeting_info(self, chat_history: List[Dict]) -> Optional[Dict[str, Any]]:
        """Extract meeting information from conversation history"""
        if not self.model:
            return None
        
        try:
            # Create extraction prompt
            extraction_prompt = """Extract meeting information from this conversation. Return ONLY a JSON object with these fields:
            {
                "title": "meeting title/subject",
                "date": "YYYY-MM-DD format",
                "start_time": "HH:MM format (24-hour)",
                "end_time": "HH:MM format (24-hour)" or null,
                "duration_minutes": number or null,
                "attendees": ["email1", "email2"] or [],
                "description": "any additional details" or null
            }

            If information is missing, use null. Only return the JSON object, no other text.

            Conversation:
            """
            
            for msg in chat_history[-20:]:  # Last 20 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                extraction_prompt += f"{role.title()}: {content}\n"
            
            response = self.model.generate_content(extraction_prompt)
            
            if response.text:
                # Try to parse JSON from response
                try:
                    # Clean the response to extract JSON
                    json_text = response.text.strip()
                    
                    # Find JSON object in response
                    start_idx = json_text.find('{')
                    end_idx = json_text.rfind('}') + 1
                    
                    if start_idx >= 0 and end_idx > start_idx:
                        json_text = json_text[start_idx:end_idx]
                        meeting_info = json.loads(json_text)
                        
                        # Validate and clean the extracted info
                        return self._validate_meeting_info(meeting_info)
                    
                except json.JSONDecodeError:
                    pass
            
            return None
        
        except Exception:
            return None
    
    def _validate_meeting_info(self, meeting_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted meeting information"""
        validated = {}
        
        # Title
        if meeting_info.get('title'):
            validated['title'] = str(meeting_info['title']).strip()
        
        # Date
        if meeting_info.get('date'):
            validated['date'] = str(meeting_info['date']).strip()
        
        # Start time
        if meeting_info.get('start_time'):
            validated['start_time'] = str(meeting_info['start_time']).strip()
        
        # End time
        if meeting_info.get('end_time'):
            validated['end_time'] = str(meeting_info['end_time']).strip()
        
        # Duration
        if meeting_info.get('duration_minutes'):
            try:
                validated['duration_minutes'] = int(meeting_info['duration_minutes'])
            except (ValueError, TypeError):
                pass
        
        # Attendees
        if meeting_info.get('attendees'):
            attendees = meeting_info['attendees']
            if isinstance(attendees, list):
                validated['attendees'] = [str(email).strip() for email in attendees if email]
        
        # Description
        if meeting_info.get('description'):
            validated['description'] = str(meeting_info['description']).strip()
        
        return validated
    
    async def create_calendar_event(self, meeting_info: Dict[str, Any], 
                                   calendar_service) -> Dict[str, Any]:
        """Create calendar event using extracted meeting information"""
        try:
            # Validate required information
            if not meeting_info.get('title'):
                return {"success": False, "error": "Meeting title is required"}
            
            if not meeting_info.get('date'):
                return {"success": False, "error": "Meeting date is required"}
            
            if not meeting_info.get('start_time'):
                return {"success": False, "error": "Meeting start time is required"}
            
            # Parse date and time
            date_str = meeting_info['date']
            start_time_str = meeting_info['start_time']
            
            # Combine date and time
            datetime_str = f"{date_str} {start_time_str}"
            start_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            
            # Calculate end time
            if meeting_info.get('end_time'):
                end_time_str = meeting_info['end_time']
                end_datetime_str = f"{date_str} {end_time_str}"
                end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
            elif meeting_info.get('duration_minutes'):
                duration = int(meeting_info['duration_minutes'])
                end_datetime = start_datetime + timedelta(minutes=duration)
            else:
                # Default to 1 hour
                end_datetime = start_datetime + timedelta(hours=1)
            
            # Create event using calendar service
            result = await calendar_service.create_event(
                title=meeting_info['title'],
                start_time=start_datetime,
                end_time=end_datetime,
                description=meeting_info.get('description', ''),
                attendees=meeting_info.get('attendees', [])
            )
            
            return result
        
        except ValueError as e:
            return {"success": False, "error": f"Invalid date/time format: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Error creating event: {str(e)}"}

    # Helper methods for different providers
    def _build_context(self, message: str, chat_history: List[Dict] = None) -> str:
        """Build context for Gemini"""
        system_prompt = """You are an AI assistant specialized in scheduling appointments using Google Calendar.

        When users want to schedule meetings, help them by:
        1. Gathering required information (title, date, time, duration, attendees)
        2. Providing clear, helpful responses
        3. Being friendly and professional

        If you have all the information needed to create a meeting, indicate this clearly."""

        context = system_prompt + "\n\nConversation:\n"

        if chat_history:
            for msg in chat_history[-10:]:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                context += f"{role.title()}: {content}\n"

        context += f"User: {message}\nAssistant:"
        return context

    def _build_openai_messages(self, message: str, chat_history: List[Dict] = None) -> List[Dict]:
        """Build messages for OpenAI format"""
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant specialized in scheduling appointments using Google Calendar. Help users schedule meetings by gathering required information and providing clear, helpful responses."
            }
        ]

        if chat_history:
            for msg in chat_history[-10:]:
                role = msg.get('role', 'user')
                if role == 'assistant':
                    role = 'assistant'
                content = msg.get('content', '')
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": message})
        return messages

    def _build_claude_messages(self, message: str, chat_history: List[Dict] = None) -> List[Dict]:
        """Build messages for Claude format"""
        messages = []

        if chat_history:
            for msg in chat_history[-10:]:
                role = msg.get('role', 'user')
                if role == 'assistant':
                    role = 'assistant'
                content = msg.get('content', '')
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": message})
        return messages

    def _determine_action(self, message: str) -> str:
        """Determine action from message"""
        message_lower = message.lower()
        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create', 'appointment']):
            return 'CREATE_EVENT'
        elif any(word in message_lower for word in ['availability', 'available', 'free', 'busy']):
            return 'CHECK_AVAILABILITY'
        elif any(word in message_lower for word in ['show', 'view', 'list', 'events', 'calendar']):
            return 'VIEW_EVENTS'
        else:
            return 'GENERAL'

    def _extract_meeting_info(self, message: str, response: str) -> Optional[Dict[str, Any]]:
        """Extract meeting information from message and response"""
        # Simple extraction - in a real implementation, this would be more sophisticated
        info = {}

        # Try to extract basic information
        if 'meeting' in message.lower() or 'appointment' in message.lower():
            info['title'] = 'Meeting'
            info['date'] = '2024-01-15'  # Default date
            info['time'] = '14:00'       # Default time
            info['duration'] = 60        # Default duration
            info['attendees'] = []

        return info if info else None
