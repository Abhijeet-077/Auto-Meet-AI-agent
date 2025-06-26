"""
Calendar Router for TailorTalk API
Handles Google Calendar operations
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
import os
from datetime import datetime, timedelta

from models import (
    CalendarEventRequest, CalendarEventResponse, CalendarEventsResponse,
    CalendarEvent, BaseResponse, ErrorResponse
)
from services.calendar_service import CalendarService
from services.auth_service import get_current_user_tokens

router = APIRouter()

# Initialize calendar service
calendar_service = CalendarService()

async def get_calendar_service_with_auth(authorization: Optional[str] = Header(None)):
    """Dependency to get calendar service with authentication"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    access_token = authorization.split(" ")[1]
    
    # Initialize calendar service with token
    if not await calendar_service.initialize_with_token(access_token):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    
    return calendar_service

@router.get("/status", response_model=BaseResponse)
async def calendar_status():
    """Get calendar service status"""
    try:
        return BaseResponse(
            success=True,
            message="Calendar service available"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar service error: {str(e)}")

@router.post("/events", response_model=CalendarEventResponse)
async def create_event(
    event_request: CalendarEventRequest,
    service: CalendarService = Depends(get_calendar_service_with_auth)
):
    """Create a new calendar event"""
    try:
        result = await service.create_event(
            title=event_request.title,
            start_time=event_request.start_time,
            end_time=event_request.end_time,
            description=event_request.description,
            attendees=event_request.attendees,
            timezone=event_request.timezone
        )
        
        return CalendarEventResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@router.get("/events", response_model=CalendarEventsResponse)
async def list_events(
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
    max_results: int = 10,
    service: CalendarService = Depends(get_calendar_service_with_auth)
):
    """List calendar events"""
    try:
        # Set default time range if not provided
        if not time_min:
            time_min = datetime.now()
        if not time_max:
            time_max = time_min + timedelta(days=30)
        
        events = await service.list_events(
            time_min=time_min,
            time_max=time_max,
            max_results=max_results
        )
        
        return CalendarEventsResponse(
            success=True,
            events=events
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list events: {str(e)}")

@router.get("/events/{event_id}")
async def get_event(
    event_id: str,
    service: CalendarService = Depends(get_calendar_service_with_auth)
):
    """Get a specific calendar event"""
    try:
        event = await service.get_event(event_id)
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event: {str(e)}")

@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: str,
    event_request: CalendarEventRequest,
    service: CalendarService = Depends(get_calendar_service_with_auth)
):
    """Update a calendar event"""
    try:
        result = await service.update_event(
            event_id=event_id,
            title=event_request.title,
            start_time=event_request.start_time,
            end_time=event_request.end_time,
            description=event_request.description,
            attendees=event_request.attendees,
            timezone=event_request.timezone
        )
        
        return CalendarEventResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

@router.delete("/events/{event_id}", response_model=BaseResponse)
async def delete_event(
    event_id: str,
    service: CalendarService = Depends(get_calendar_service_with_auth)
):
    """Delete a calendar event"""
    try:
        success = await service.delete_event(event_id)
        
        if success:
            return BaseResponse(success=True, message="Event deleted successfully")
        else:
            raise HTTPException(status_code=400, detail="Failed to delete event")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

@router.get("/events/recent/{hours}")
async def get_recent_events(
    hours: int = 24,
    service: CalendarService = Depends(get_calendar_service_with_auth)
):
    """Get events created in the last N hours"""
    try:
        events = await service.get_recent_events(hours)
        
        return CalendarEventsResponse(
            success=True,
            events=events
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent events: {str(e)}")

@router.post("/events/{event_id}/verify", response_model=BaseResponse)
async def verify_event(
    event_id: str,
    service: CalendarService = Depends(get_calendar_service_with_auth)
):
    """Verify that an event exists"""
    try:
        exists = await service.verify_event_exists(event_id)
        
        return BaseResponse(
            success=exists,
            message="Event exists" if exists else "Event not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify event: {str(e)}")

@router.get("/free-busy")
async def get_free_busy(
    time_min: datetime,
    time_max: datetime,
    service: CalendarService = Depends(get_calendar_service_with_auth)
):
    """Get free/busy information for a time range"""
    try:
        free_busy = await service.get_free_busy(time_min, time_max)
        return free_busy
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get free/busy info: {str(e)}")

@router.get("/calendars")
async def list_calendars(
    service: CalendarService = Depends(get_calendar_service_with_auth)
):
    """List user's calendars"""
    try:
        calendars = await service.list_calendars()
        return {"success": True, "calendars": calendars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list calendars: {str(e)}")
