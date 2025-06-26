"""
AI Service for Agentic Calendar
Professional Google Gemini integration for intelligent meeting scheduling
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env.local')

class AIService:
    """AI service for conversation and meeting scheduling"""
    
    def __init__(self):
        """Initialize AI service"""
        self.api_key = self._get_api_key()
        self.model = None
        self._initialize_model()
    
    def _get_api_key(self) -> Optional[str]:
        """Get Gemini API key from environment"""
        api_key = os.getenv('GEMINI_API_KEY', '')
        if not api_key or api_key in ['your_gemini_api_key_here']:
            return None
        return api_key
    
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
    
    def is_configured(self) -> bool:
        """Check if AI service is properly configured"""
        return bool(self.api_key and self.model)
    
    def get_model_name(self) -> str:
        """Get model name"""
        return "gemini-1.5-flash" if self.is_configured() else "not_configured"
    
    async def get_response(self, user_message: str, chat_history: List[Dict], 
                          calendar_connected: bool = False) -> Dict[str, Any]:
        """Get AI response to user message"""
        if not self.model:
            return {
                "response": "I apologize, but I'm not properly configured. Please check the Gemini API key.",
                "action": None
            }
        
        try:
            # Enhanced system prompt
            system_prompt = """You are TailorTalk, a friendly AI assistant specialized in scheduling appointments using Google Calendar.

            IMPORTANT INSTRUCTIONS:
            1. **Remember Context**: Use the full conversation history to avoid asking for information already provided.
            2. **Extract Information**: When users provide meeting details, remember them for the entire conversation.
            3. **Take Action**: When you have complete meeting information, indicate you're ready to create the event.

            ACTION INDICATORS:
            - When you have all required information to create a meeting, end your response with: [ACTION:CREATE_EVENT]
            - When you need more information, end your response with: [ACTION:NEED_INFO]

            Required information for scheduling:
            - Meeting title/subject
            - Date (specific date)
            - Start time
            - Duration or end time
            - Attendees (optional)

            Be helpful, concise, and friendly."""
            
            if calendar_connected:
                system_prompt += "\n\nThe user has connected their Google Calendar and you can create events."
            else:
                system_prompt += "\n\nThe user has NOT connected their Google Calendar yet. If they want to schedule something, ask them to connect their calendar first."
            
            # Build conversation context
            conversation_context = system_prompt + "\n\nConversation History:\n"
            
            for msg in chat_history[-10:]:  # Last 10 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conversation_context += f"{role.title()}: {content}\n"
            
            conversation_context += f"User: {user_message}\nTailorTalk:"
            
            response = self.model.generate_content(conversation_context)
            
            if response.text:
                response_text = response.text.strip()
                
                # Extract action from response
                action = self._extract_action(response_text)
                
                # Clean response text (remove action indicator)
                clean_response = self._clean_response_text(response_text)
                
                # Extract meeting info if action is CREATE_EVENT
                meeting_info = None
                if action == "CREATE_EVENT":
                    meeting_info = await self.extract_meeting_info(chat_history + [
                        {"role": "user", "content": user_message}
                    ])
                
                return {
                    "response": clean_response,
                    "action": action,
                    "meeting_info": meeting_info
                }
            else:
                return {
                    "response": "I apologize, but I couldn't generate a response. Please try again.",
                    "action": None
                }
        
        except Exception as e:
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "action": None
            }
    
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
