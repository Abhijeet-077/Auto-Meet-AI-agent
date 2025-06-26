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
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendarService:
    """Service class for handling Google Calendar operations with OAuth tokens"""

    def __init__(self):
        """Initialize the Google Calendar service"""
        self.service = None
        self.credentials = None
    
    def initialize_with_tokens(self, tokens: Dict[str, Any]) -> bool:
        """Initialize service with OAuth tokens"""
        try:
            if not tokens or 'access_token' not in tokens:
                st.error("Invalid tokens provided for calendar service initialization")
                return False

            # Create credentials from tokens
            self.credentials = Credentials(
                token=tokens.get('access_token'),
                refresh_token=tokens.get('refresh_token'),
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
                    st.success("Access token refreshed successfully")
                except Exception as refresh_error:
                    st.error(f"Failed to refresh access token: {str(refresh_error)}")
                    return False

            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)

            # Test the connection with a simple API call
            try:
                calendar_list = self.service.calendarList().list(maxResults=1).execute()
                st.success("Google Calendar service initialized successfully")
                return True
            except Exception as test_error:
                st.error(f"Calendar service test failed: {str(test_error)}")
                return False

        except Exception as e:
            st.error(f"Error initializing calendar service: {str(e)}")
            if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                st.exception(e)
            return False

    def _get_client_id(self) -> str:
        """Get Google OAuth Client ID"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth']['client_id']
        except:
            pass
        return os.getenv('GOOGLE_CLIENT_ID', '')

    def _get_client_secret(self) -> str:
        """Get Google OAuth Client Secret"""
        try:
            if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                return st.secrets['google_oauth']['client_secret']
        except:
            pass
        return os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return bool(self._get_client_id() and self._get_client_secret())

    def is_authenticated(self) -> bool:
        """Check if the service is authenticated and ready to use"""
        if self.service is None or self.credentials is None:
            return False

        # Check if credentials are still valid
        try:
            if self.credentials.expired:
                if self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    return True
                else:
                    return False
            return True
        except Exception:
            return False

    def get_authentication_status(self) -> Dict[str, Any]:
        """Get detailed authentication status"""
        if not self.credentials:
            return {
                'authenticated': False,
                'error': 'No credentials available'
            }

        try:
            status = {
                'authenticated': True,
                'has_access_token': bool(self.credentials.token),
                'has_refresh_token': bool(self.credentials.refresh_token),
                'expired': self.credentials.expired,
                'scopes': self.credentials.scopes
            }

            if self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    status['refreshed'] = True
                    status['expired'] = False
                except Exception as e:
                    status['refresh_error'] = str(e)
                    status['authenticated'] = False

            return status

        except Exception as e:
            return {
                'authenticated': False,
                'error': str(e)
            }
    

    
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
