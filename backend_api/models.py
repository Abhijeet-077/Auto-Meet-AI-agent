"""
Pydantic models for TailorTalk API
Defines request/response schemas for all endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Base response models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None

# OAuth Models
class OAuthConfig(BaseModel):
    """OAuth configuration response"""
    client_id: str
    redirect_uri: str
    scopes: List[str]
    is_configured: bool

class AuthURLResponse(BaseModel):
    """OAuth authorization URL response"""
    auth_url: str
    state: str

class TokenRequest(BaseModel):
    """Token exchange request"""
    code: str
    state: str

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None
    token_type: str = "Bearer"
    user_info: Optional[Dict[str, Any]] = None

class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str

# Calendar Models
class CalendarEventRequest(BaseModel):
    """Calendar event creation request"""
    title: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    end_time: datetime
    description: Optional[str] = Field(None, max_length=1000)
    attendees: Optional[List[str]] = []
    timezone: Optional[str] = "UTC"

class CalendarEventResponse(BaseModel):
    """Calendar event creation response"""
    success: bool
    event_id: Optional[str] = None
    event_link: Optional[str] = None
    title: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    timezone: Optional[str] = None
    attendees: Optional[List[str]] = []
    error: Optional[str] = None
    warning: Optional[str] = None

class CalendarEvent(BaseModel):
    """Calendar event model"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    attendees: List[str] = []
    created: datetime
    updated: datetime

class CalendarEventsResponse(BaseModel):
    """Calendar events list response"""
    success: bool
    events: List[CalendarEvent] = []
    error: Optional[str] = None

# AI Models
class MessageRole(str, Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """Chat message model"""
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    """AI chat request"""
    message: str = Field(..., min_length=1, max_length=2000)
    chat_history: List[ChatMessage] = []
    calendar_connected: bool = False

class ChatResponse(BaseModel):
    """AI chat response"""
    response: str
    action: Optional[str] = None
    meeting_info: Optional[Dict[str, Any]] = None

class MeetingInfo(BaseModel):
    """Meeting information extracted from conversation"""
    title: Optional[str] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    attendees: Optional[List[str]] = []
    description: Optional[str] = None

class MeetingExtractionRequest(BaseModel):
    """Meeting information extraction request"""
    chat_history: List[ChatMessage]

class MeetingExtractionResponse(BaseModel):
    """Meeting information extraction response"""
    success: bool
    meeting_info: Optional[MeetingInfo] = None
    error: Optional[str] = None

# Health Models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]

# Session Models
class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    user_id: Optional[str] = None
    calendar_connected: bool = False
    created_at: datetime
    last_activity: datetime

class SessionResponse(BaseModel):
    """Session response"""
    success: bool
    session_info: Optional[SessionInfo] = None
    error: Optional[str] = None

# Configuration Models
class APIConfig(BaseModel):
    """API configuration"""
    oauth_available: bool
    gemini_available: bool
    debug_mode: bool
    api_version: str
