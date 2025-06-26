"""
Demo Service for Agentic Calendar
Provides mock data and responses for academic evaluation and demonstration
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv('../.env.local')

class DemoService:
    """Demo service for academic evaluation and testing"""
    
    def __init__(self):
        """Initialize demo service with sample data"""
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'
        self.demo_user = {
            'name': 'Demo User',
            'email': 'demo.user@agenticcalendar.com',
            'picture': 'https://via.placeholder.com/150/0066cc/ffffff?text=Demo'
        }
        
        # Sample calendar events for demo
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
            },
            {
                'id': 'demo_event_3',
                'title': 'Client Presentation',
                'start_time': (datetime.now() + timedelta(days=2, hours=14)).isoformat(),
                'end_time': (datetime.now() + timedelta(days=2, hours=15, minutes=30)).isoformat(),
                'description': 'Presentation to key client stakeholders',
                'attendees': ['client@external.com', 'sales@company.com'],
                'location': 'Client Office',
                'event_link': 'https://calendar.google.com/calendar/event?eid=demo_event_3'
            }
        ]
        
        # Demo AI responses for common queries
        self.demo_responses = {
            'schedule_meeting': [
                "I'll help you schedule that meeting! Let me create it in your calendar.",
                "Perfect! I'm scheduling the meeting for you right now.",
                "Great choice of time! I'll add this to your calendar immediately.",
                "Excellent! I'm creating the calendar event for you."
            ],
            'check_availability': [
                "Let me check your calendar availability for you.",
                "I'll analyze your schedule to find the best available times.",
                "Checking your calendar for free time slots...",
                "Looking at your availability across the requested timeframe."
            ],
            'view_events': [
                "Here are your upcoming events from your calendar.",
                "Let me show you what's scheduled in your calendar.",
                "Here's your calendar overview for the requested period.",
                "These are your scheduled meetings and appointments."
            ],
            'general': [
                "I'm here to help you manage your calendar and schedule meetings!",
                "I can help you schedule meetings, check availability, and manage your calendar.",
                "Feel free to ask me about scheduling meetings or checking your calendar.",
                "I'm your AI assistant for all calendar and scheduling needs!"
            ]
        }
    
    def is_demo_mode(self) -> bool:
        """Check if demo mode is enabled"""
        return self.demo_mode
    
    def get_demo_user_info(self) -> Dict[str, Any]:
        """Get demo user information"""
        return self.demo_user.copy()
    
    def get_demo_events(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get demo calendar events"""
        if not start_date or not end_date:
            return self.demo_events.copy()
        
        # Filter events by date range (simplified for demo)
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            filtered_events = []
            for event in self.demo_events:
                event_start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                if start_dt <= event_start <= end_dt:
                    filtered_events.append(event)
            
            return filtered_events
        except:
            return self.demo_events.copy()
    
    def create_demo_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a demo calendar event"""
        import secrets
        
        # Generate demo event
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
            'demo_mode': True,
            'message': 'Demo event created successfully! This is a simulated calendar event for evaluation purposes.'
        }
    
    def get_demo_ai_response(self, message: str, intent: str = 'general') -> Dict[str, Any]:
        """Get demo AI response based on message intent"""
        import random
        
        # Determine intent from message if not provided
        message_lower = message.lower()
        if any(word in message_lower for word in ['schedule', 'meeting', 'book', 'create']):
            intent = 'schedule_meeting'
        elif any(word in message_lower for word in ['availability', 'available', 'free', 'busy']):
            intent = 'check_availability'
        elif any(word in message_lower for word in ['show', 'view', 'list', 'events', 'meetings']):
            intent = 'view_events'
        
        # Get appropriate response
        responses = self.demo_responses.get(intent, self.demo_responses['general'])
        base_response = random.choice(responses)
        
        # Add demo-specific context
        if intent == 'schedule_meeting':
            return {
                'response': f"{base_response} (Demo Mode: This will create a simulated calendar event for evaluation purposes.)",
                'action': 'CREATE_EVENT',
                'confidence': 0.95,
                'demo_mode': True,
                'intent': intent
            }
        elif intent == 'check_availability':
            return {
                'response': f"{base_response} Based on your demo calendar, you have several free slots available this week.",
                'action': 'CHECK_AVAILABILITY',
                'confidence': 0.90,
                'demo_mode': True,
                'intent': intent,
                'availability': self._get_demo_availability()
            }
        elif intent == 'view_events':
            return {
                'response': f"{base_response} You have {len(self.demo_events)} upcoming events in your demo calendar.",
                'action': 'VIEW_EVENTS',
                'confidence': 0.92,
                'demo_mode': True,
                'intent': intent,
                'events': self.get_demo_events()
            }
        else:
            return {
                'response': f"{base_response} You're currently in demo mode, which allows you to test all features with simulated data.",
                'action': 'GENERAL',
                'confidence': 0.85,
                'demo_mode': True,
                'intent': intent
            }
    
    def _get_demo_availability(self) -> List[Dict[str, str]]:
        """Get demo availability slots"""
        now = datetime.now()
        availability = []
        
        # Generate some demo free slots
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
                },
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'start_time': '16:00',
                    'end_time': '17:00',
                    'status': 'free'
                }
            ])
        
        return availability
    
    def get_demo_oauth_config(self) -> Dict[str, Any]:
        """Get demo OAuth configuration"""
        return {
            'is_configured': True,
            'demo_mode': True,
            'has_client_id': True,
            'has_client_secret': True,
            'redirect_uri': 'http://localhost:8000/api/v1/oauth/callback',
            'message': 'Demo mode: OAuth is simulated for evaluation purposes'
        }
    
    def get_demo_auth_url(self) -> Dict[str, Any]:
        """Get demo authorization URL"""
        import secrets
        state = secrets.token_urlsafe(32)
        
        return {
            'auth_url': f'http://localhost:8000/api/v1/oauth/demo-callback?demo=true&state={state}',
            'state': state,
            'demo_mode': True,
            'message': 'Demo mode: This will simulate the OAuth flow for evaluation'
        }
    
    def simulate_oauth_success(self) -> Dict[str, Any]:
        """Simulate successful OAuth authentication"""
        return {
            'access_token': 'demo_access_token_for_evaluation',
            'refresh_token': 'demo_refresh_token_for_evaluation',
            'expires_at': int((datetime.now() + timedelta(hours=1)).timestamp()),
            'token_type': 'Bearer',
            'user_info': self.get_demo_user_info(),
            'demo_mode': True,
            'message': 'Demo authentication successful! You can now test all calendar features.'
        }
    
    def get_demo_status(self) -> Dict[str, Any]:
        """Get demo service status"""
        return {
            'demo_mode': True,
            'status': 'operational',
            'features_available': [
                'AI Chat with simulated responses',
                'Calendar event creation (simulated)',
                'Event viewing with sample data',
                'Availability checking with mock data',
                'OAuth flow simulation'
            ],
            'note': 'All features are functional in demo mode for evaluation purposes'
        }
