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

@router.get("/status")
async def ai_status():
    """Get AI service status with provider information"""
    try:
        is_configured = ai_service.is_configured()
        current_provider = ai_service.get_current_provider_info()

        return {
            "success": is_configured,
            "message": "AI service configured" if is_configured else "AI service not configured",
            "current_provider": current_provider,
            "model": ai_service.get_model_name()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/chat")
async def chat(request: dict):
    """Process AI chat request with provider switching support"""
    try:
        # Handle provider switching
        if request.get('action') == 'switch_provider':
            provider = request.get('provider', 'demo')
            api_key = request.get('api_key')
            model = request.get('model')

            try:
                ai_service.set_provider(provider, api_key, model)
                return {
                    "success": True,
                    "message": f"Switched to {provider}",
                    "current_provider": ai_service.get_current_provider_info()
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to switch provider: {str(e)}"
                }

        # Handle test mode
        if request.get('test_mode'):
            provider = request.get('provider', 'demo')
            api_key = request.get('api_key')

            # Test the provider without switching
            try:
                if provider == 'demo':
                    return {"success": True, "message": "Demo mode is always available"}
                elif provider == 'gemini' and api_key:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content("Hello")
                    return {"success": True, "message": "Gemini API key is valid"}
                elif provider == 'openai' and api_key:
                    import openai
                    client = openai.OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5
                    )
                    return {"success": True, "message": "OpenAI API key is valid"}
                elif provider == 'claude' and api_key:
                    import anthropic
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=5,
                        messages=[{"role": "user", "content": "Hello"}]
                    )
                    return {"success": True, "message": "Claude API key is valid"}
                else:
                    return {"success": False, "error": "Invalid provider or missing API key"}
            except Exception as e:
                return {"success": False, "error": f"API key test failed: {str(e)}"}

        # Regular chat processing
        message = request.get('message', '')
        chat_history = request.get('chat_history', [])
        calendar_connected = request.get('calendar_connected', False)

        if not ai_service.is_configured() and ai_service.current_provider != 'demo':
            return {
                "success": False,
                "error": "AI service not configured. Please configure an AI provider or use demo mode."
            }

        result = await ai_service.get_response(
            user_message=message,
            chat_history=chat_history,
            calendar_connected=calendar_connected
        )

        return {
            "success": True,
            "response": result.get("response", ""),
            "action": result.get("action"),
            "meeting_info": result.get("meeting_info"),
            "provider": result.get("provider")
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Chat processing failed: {str(e)}"
        }

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
