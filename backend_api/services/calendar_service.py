"""
Calendar Service for TailorTalk API
Migrated from backend/google_calendar_service.py to work with FastAPI
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pytz
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

class CalendarService:
    """Google Calendar service for FastAPI backend"""
    
    def __init__(self):
        """Initialize calendar service"""
        self.service = None
        self.credentials = None
        
    def _get_client_id(self) -> str:
        """Get Google OAuth Client ID"""
        return os.getenv('GOOGLE_CLIENT_ID', '')
    
    def _get_client_secret(self) -> str:
        """Get Google OAuth Client Secret"""
        return os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    async def initialize_with_token(self, access_token: str, refresh_token: str = None) -> bool:
        """Initialize service with OAuth token"""
        try:
            # Create credentials from token
            self.credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self._get_client_id(),
                client_secret=self._get_client_secret(),
                scopes=[
                    'https://www.googleapis.com/auth/calendar.readonly',
                    'https://www.googleapis.com/auth/calendar.events',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile'
                ]
            )
            
            # Check if token is expired and refresh if needed
            if self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                except Exception:
                    return False
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            
            # Test the connection
            try:
                calendar_list = self.service.calendarList().list(maxResults=1).execute()
                return True
            except Exception:
                return False
                
        except Exception:
            return False
    
    async def create_event(self, title: str, start_time: datetime, end_time: datetime,
                          description: str = "", attendees: List[str] = None,
                          timezone: str = None) -> Dict[str, Any]:
        """Create a new calendar event"""
        if not self.service:
            return {"success": False, "error": "Calendar service not initialized"}
        
        try:
            # Determine timezone
            if timezone is None:
                try:
                    calendar_info = self.service.calendars().get(calendarId='primary').execute()
                    timezone = calendar_info.get('timeZone', 'UTC')
                except:
                    timezone = 'UTC'
            
            # Ensure datetime objects have timezone info
            if start_time.tzinfo is None:
                tz = pytz.timezone(timezone)
                start_time = tz.localize(start_time)
                end_time = tz.localize(end_time)
            
            # Create event object
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': timezone,
                },
            }
            
            # Add attendees if provided
            if attendees and len(attendees) > 0:
                event['attendees'] = [{'email': email.strip()} for email in attendees if email.strip()]
                event['sendUpdates'] = 'all'
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all' if attendees else 'none'
            ).execute()
            
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            
            # Verify the event was created
            try:
                verification = self.service.events().get(
                    calendarId='primary',
                    eventId=event_id
                ).execute()
                
                if verification:
                    # Generate additional verification links
                    verification_link = f'https://calendar.google.com/calendar/r/eventedit/{event_id}'

                    return {
                        "success": True,
                        "event_id": event_id,
                        "event_link": event_link,
                        "verification_link": verification_link,
                        "title": title,
                        "start_time": start_time.strftime("%Y-%m-%d %H:%M %Z"),
                        "end_time": end_time.strftime("%Y-%m-%d %H:%M %Z"),
                        "timezone": timezone,
                        "attendees": attendees or [],
                        "verification_status": "verified",
                        "calendar_integration": "google_calendar",
                        "created_timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"success": False, "error": "Event created but verification failed"}
                    
            except Exception as verify_error:
                # Generate verification link even if verification failed
                verification_link = f'https://calendar.google.com/calendar/r/eventedit/{event_id}'

                return {
                    "success": True,
                    "event_id": event_id,
                    "event_link": event_link,
                    "verification_link": verification_link,
                    "title": title,
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M %Z"),
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M %Z"),
                    "timezone": timezone,
                    "attendees": attendees or [],
                    "verification_status": "created_unverified",
                    "calendar_integration": "google_calendar",
                    "created_timestamp": datetime.now().isoformat(),
                    "warning": f"Event created but verification failed: {str(verify_error)}"
                }
            
        except HttpError as error:
            error_details = f"HTTP {error.resp.status}: {error.content.decode() if error.content else 'Unknown error'}"
            return {"success": False, "error": error_details}
        except Exception as error:
            return {"success": False, "error": f"Unexpected error creating event: {str(error)}"}
    
    async def list_events(self, time_min: datetime = None, time_max: datetime = None,
                         max_results: int = 10) -> List[Dict[str, Any]]:
        """List calendar events"""
        if not self.service:
            return []
        
        try:
            if not time_min:
                time_min = datetime.now(pytz.UTC)
            if not time_max:
                time_max = time_min + timedelta(days=30)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat(),
                timeMax=time_max.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Convert to our format
            formatted_events = []
            for event in events:
                formatted_event = {
                    'id': event.get('id'),
                    'title': event.get('summary', 'No Title'),
                    'start_time': event.get('start', {}).get('dateTime', ''),
                    'end_time': event.get('end', {}).get('dateTime', ''),
                    'description': event.get('description', ''),
                    'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])],
                    'created': event.get('created', ''),
                    'updated': event.get('updated', '')
                }
                formatted_events.append(formatted_event)
            
            return formatted_events
            
        except Exception:
            return []
    
    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific event"""
        if not self.service:
            return None
        
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return {
                'id': event.get('id'),
                'title': event.get('summary', 'No Title'),
                'start_time': event.get('start', {}).get('dateTime', ''),
                'end_time': event.get('end', {}).get('dateTime', ''),
                'description': event.get('description', ''),
                'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])],
                'created': event.get('created', ''),
                'updated': event.get('updated', '')
            }
        except Exception:
            return None
    
    async def verify_event_exists(self, event_id: str) -> bool:
        """Verify that an event exists"""
        if not self.service or not event_id:
            return False
        
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return bool(event)
        except:
            return False
    
    async def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get events created in the last N hours"""
        if not self.service:
            return []
        
        try:
            now = datetime.now(pytz.UTC)
            time_min = now - timedelta(hours=hours)
            
            return await self.list_events(time_min=time_min, time_max=now)
        except Exception:
            return []
