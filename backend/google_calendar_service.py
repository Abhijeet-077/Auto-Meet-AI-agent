import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv('.env.local')

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendarService:
    """Service class for handling Google Calendar operations"""
    
    # OAuth 2.0 scopes for Google Calendar
    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        """Initialize the Google Calendar service"""
        self.credentials = None
        self.service = None
        self.client_config = self._get_client_config()
    
    def _get_client_config(self) -> Optional[Dict[str, Any]]:
        """Get Google OAuth client configuration"""
        try:
            # Try to get from Streamlit secrets first (for cloud deployment)
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return {
                    "web": {
                        "client_id": st.secrets['google_oauth']['client_id'],
                        "client_secret": st.secrets['google_oauth']['client_secret'],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [st.secrets['google_oauth'].get('redirect_uri', 'http://localhost:8501')]
                    }
                }
        except:
            pass
        
        # Fall back to environment variables
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if client_id and client_secret:
            return {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8501"]
                }
            }
        
        return None
    
    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return self.client_config is not None
    
    def get_authorization_url(self) -> Optional[str]:
        """Get the authorization URL for OAuth flow"""
        if not self.client_config:
            return None
        
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri=self.client_config['web']['redirect_uris'][0]
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return auth_url
        except Exception as e:
            st.error(f"Error creating authorization URL: {str(e)}")
            return None
    
    def authenticate_with_code(self, auth_code: str) -> bool:
        """Authenticate using authorization code from OAuth flow"""
        if not self.client_config:
            return False
        
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri=self.client_config['web']['redirect_uris'][0]
            )
            
            flow.fetch_token(code=auth_code)
            self.credentials = flow.credentials
            self.service = build('calendar', 'v3', credentials=self.credentials)
            
            return True
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return False
    
    def authenticate_with_token(self, token_info: Dict[str, Any]) -> bool:
        """Authenticate using existing token information"""
        try:
            self.credentials = Credentials.from_authorized_user_info(token_info, self.SCOPES)
            
            # Refresh token if expired
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            
            self.service = build('calendar', 'v3', credentials=self.credentials)
            return True
        except Exception as e:
            st.error(f"Token authentication error: {str(e)}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, str]]:
        """Get authenticated user information"""
        if not self.service:
            return None
        
        try:
            # Get user's primary calendar to extract email
            calendar_list = self.service.calendarList().list().execute()
            primary_calendar = next(
                (cal for cal in calendar_list['items'] if cal.get('primary')), 
                None
            )
            
            if primary_calendar:
                return {
                    'email': primary_calendar['id'],
                    'name': primary_calendar.get('summary', 'User')
                }
        except Exception as e:
            st.error(f"Error getting user info: {str(e)}")
        
        return None
    
    def list_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """List calendar events in the specified time range"""
        if not self.service:
            return []
        
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', '')
                })
            
            return formatted_events
            
        except HttpError as error:
            st.error(f"Error listing events: {error}")
            return []
    
    def create_event(self, title: str, start_time: datetime, end_time: datetime, 
                    description: str = "", attendees: List[str] = None) -> Optional[str]:
        """Create a new calendar event"""
        if not self.service:
            return None
        
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId='primary', 
                body=event
            ).execute()
            
            return created_event.get('id')
            
        except HttpError as error:
            st.error(f"Error creating event: {error}")
            return None
    
    def find_free_slots(self, start_date: datetime, end_date: datetime, 
                       duration_minutes: int = 60) -> List[Dict[str, datetime]]:
        """Find free time slots in the specified date range"""
        if not self.service:
            return []
        
        try:
            # Get busy times
            busy_times = self.service.freebusy().query(
                body={
                    'timeMin': start_date.isoformat() + 'Z',
                    'timeMax': end_date.isoformat() + 'Z',
                    'items': [{'id': 'primary'}]
                }
            ).execute()
            
            busy_periods = busy_times['calendars']['primary']['busy']
            
            # Convert busy periods to datetime objects
            busy_slots = []
            for period in busy_periods:
                start = datetime.fromisoformat(period['start'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(period['end'].replace('Z', '+00:00'))
                busy_slots.append({'start': start, 'end': end})
            
            # Find free slots
            free_slots = []
            current_time = start_date
            duration = timedelta(minutes=duration_minutes)
            
            while current_time + duration <= end_date:
                slot_end = current_time + duration
                
                # Check if this slot conflicts with any busy period
                is_free = True
                for busy in busy_slots:
                    if (current_time < busy['end'] and slot_end > busy['start']):
                        is_free = False
                        current_time = busy['end']
                        break
                
                if is_free:
                    free_slots.append({
                        'start': current_time,
                        'end': slot_end
                    })
                    current_time += timedelta(minutes=30)  # Move by 30-minute increments
                
            return free_slots[:10]  # Return up to 10 free slots
            
        except HttpError as error:
            st.error(f"Error finding free slots: {error}")
            return []
