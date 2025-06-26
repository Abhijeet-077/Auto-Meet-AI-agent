"""
AI Router for TailorTalk API
Handles AI conversation and meeting extraction
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from models import (
    ChatRequest, ChatResponse, MeetingExtractionRequest,
    MeetingExtractionResponse, BaseResponse
)
from services.ai_service import AIService

router = APIRouter()

# Initialize AI service
ai_service = AIService()

@router.get("/status", response_model=BaseResponse)
async def ai_status():
    """Get AI service status"""
    try:
        is_configured = ai_service.is_configured()
        return BaseResponse(
            success=is_configured,
            message="AI service configured" if is_configured else "AI service not configured"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """Process AI chat request"""
    try:
        if not ai_service.is_configured():
            raise HTTPException(status_code=400, detail="AI service not configured")
        
        # Convert chat history to the format expected by AI service
        chat_history = [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in chat_request.chat_history
        ]
        
        result = await ai_service.get_response(
            user_message=chat_request.message,
            chat_history=chat_history,
            calendar_connected=chat_request.calendar_connected
        )
        
        return ChatResponse(
            response=result.get("response", ""),
            action=result.get("action"),
            meeting_info=result.get("meeting_info")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/extract-meeting", response_model=MeetingExtractionResponse)
async def extract_meeting_info(extraction_request: MeetingExtractionRequest):
    """Extract meeting information from conversation"""
    try:
        if not ai_service.is_configured():
            raise HTTPException(status_code=400, detail="AI service not configured")
        
        # Convert chat history to the format expected by AI service
        chat_history = [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in extraction_request.chat_history
        ]
        
        meeting_info = await ai_service.extract_meeting_info(chat_history)
        
        if meeting_info:
            return MeetingExtractionResponse(
                success=True,
                meeting_info=meeting_info
            )
        else:
            return MeetingExtractionResponse(
                success=False,
                error="Could not extract meeting information from conversation"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meeting extraction failed: {str(e)}")

@router.post("/create-event")
async def create_calendar_event(
    meeting_info: Dict[str, Any],
    access_token: str
):
    """Create calendar event using AI-extracted meeting information"""
    try:
        if not ai_service.is_configured():
            raise HTTPException(status_code=400, detail="AI service not configured")
        
        # Import calendar service for event creation
        from services.calendar_service import CalendarService
        
        calendar_service = CalendarService()
        
        # Initialize calendar service with token
        if not await calendar_service.initialize_with_token(access_token):
            raise HTTPException(status_code=401, detail="Invalid access token")
        
        result = await ai_service.create_calendar_event(meeting_info, calendar_service)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event creation failed: {str(e)}")

@router.get("/config")
async def get_ai_config():
    """Get AI service configuration"""
    try:
        return {
            "gemini_available": ai_service.is_configured(),
            "model": ai_service.get_model_name(),
            "capabilities": [
                "natural_conversation",
                "meeting_scheduling",
                "information_extraction",
                "calendar_integration"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI config: {str(e)}")

@router.post("/test")
async def test_ai_service():
    """Test AI service functionality"""
    try:
        if not ai_service.is_configured():
            return {
                "success": False,
                "error": "AI service not configured"
            }
        
        # Test with a simple message
        test_result = await ai_service.get_response(
            user_message="Hello, can you help me schedule a meeting?",
            chat_history=[],
            calendar_connected=False
        )
        
        return {
            "success": True,
            "test_response": test_result.get("response", ""),
            "message": "AI service test successful"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"AI service test failed: {str(e)}"
        }
