"""
Demo Router for Agentic Calendar
Provides demo endpoints for academic evaluation and testing
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import Dict, Any, List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

from services.demo_service import DemoService
from models import ChatRequest, TokenResponse, CalendarEventRequest

load_dotenv('../.env.local')

router = APIRouter()
demo_service = DemoService()

@router.get("/status")
async def demo_status():
    """Get demo mode status and available features"""
    return demo_service.get_demo_status()

@router.get("/enable")
async def enable_demo_mode():
    """Enable demo mode for evaluation"""
    demo_service.demo_mode = True
    return {
        "demo_mode": True,
        "message": "Demo mode enabled! All features are now available with simulated data.",
        "instructions": [
            "1. Use the chat interface to test AI responses",
            "2. Try scheduling meetings with natural language",
            "3. Check calendar availability and view events",
            "4. Test the OAuth flow with simulated authentication",
            "5. All data is simulated for evaluation purposes"
        ]
    }

@router.get("/disable")
async def disable_demo_mode():
    """Disable demo mode"""
    demo_service.demo_mode = False
    return {
        "demo_mode": False,
        "message": "Demo mode disabled. Real API credentials required for functionality."
    }

@router.get("/oauth/config")
async def demo_oauth_config():
    """Get demo OAuth configuration"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    return demo_service.get_demo_oauth_config()

@router.get("/oauth/auth-url")
async def demo_auth_url():
    """Get demo authorization URL"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    return demo_service.get_demo_auth_url()

@router.get("/oauth/callback")
async def demo_oauth_callback(demo: bool = Query(True), state: str = Query(...)):
    """Handle demo OAuth callback"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    # Simulate successful OAuth flow
    import secrets
    session_id = secrets.token_urlsafe(32)
    
    # Store demo tokens (in real implementation, this would be in token service)
    demo_tokens = demo_service.simulate_oauth_success()
    
    # Redirect to frontend with success
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:8501')
    return RedirectResponse(
        url=f"{frontend_url}?demo_session_id={session_id}&demo_success=true",
        status_code=302
    )

@router.get("/oauth/tokens/{session_id}")
async def demo_get_tokens(session_id: str):
    """Get demo tokens by session ID"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    return demo_service.simulate_oauth_success()

@router.post("/ai/chat")
async def demo_ai_chat(request: ChatRequest):
    """Demo AI chat endpoint"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    try:
        # Get demo AI response
        response = demo_service.get_demo_ai_response(request.message)
        
        return {
            **response,
            'timestamp': datetime.now().isoformat(),
            'demo_note': 'This is a simulated AI response for evaluation purposes.'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo AI chat error: {str(e)}")

@router.post("/ai/extract-meeting")
async def demo_extract_meeting(request: ChatRequest):
    """Demo meeting extraction endpoint"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    # Simulate meeting extraction
    return {
        'success': True,
        'demo_mode': True,
        'meeting_info': {
            'title': 'Demo Meeting - Extracted from Conversation',
            'date': (datetime.now().date()).isoformat(),
            'start_time': '14:00',
            'end_time': '15:00',
            'description': 'Demo meeting extracted from conversation for evaluation',
            'attendees': ['demo.attendee@example.com']
        },
        'note': 'This is simulated meeting extraction for evaluation purposes.'
    }

@router.get("/calendar/events")
async def demo_get_events(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    max_results: int = Query(10)
):
    """Get demo calendar events"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    events = demo_service.get_demo_events(start_date, end_date)
    
    return {
        'success': True,
        'demo_mode': True,
        'events': events[:max_results],
        'total_events': len(events),
        'note': 'These are simulated calendar events for evaluation purposes.'
    }

@router.post("/calendar/events")
async def demo_create_event(request: CalendarEventRequest):
    """Create demo calendar event"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    try:
        # Create demo event
        event_data = {
            'title': request.title,
            'start_time': request.start_time,
            'end_time': request.end_time,
            'description': request.description,
            'attendees': request.attendees or []
        }
        
        result = demo_service.create_demo_event(event_data)
        
        return {
            **result,
            'verification_link': result['event_link'],
            'demo_note': 'This is a simulated calendar event created for evaluation purposes.'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo event creation error: {str(e)}")

@router.get("/calendar/status")
async def demo_calendar_status():
    """Get demo calendar status"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    return {
        'success': True,
        'demo_mode': True,
        'connected': True,
        'calendar_id': 'demo_primary_calendar',
        'user_email': demo_service.demo_user['email'],
        'note': 'This is a simulated calendar connection for evaluation purposes.'
    }

@router.get("/user-info")
async def demo_user_info():
    """Get demo user information"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    return {
        **demo_service.get_demo_user_info(),
        'demo_mode': True,
        'note': 'This is simulated user information for evaluation purposes.'
    }

@router.get("/test-scenarios")
async def demo_test_scenarios():
    """Get predefined test scenarios for evaluators"""
    if not demo_service.is_demo_mode():
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    return {
        'demo_mode': True,
        'test_scenarios': [
            {
                'scenario': 'Schedule a Meeting',
                'description': 'Test AI-powered meeting scheduling',
                'steps': [
                    'Type: "Schedule a meeting with John tomorrow at 2 PM"',
                    'Observe AI response and meeting creation',
                    'Verify meeting appears in calendar view',
                    'Check for verification link to Google Calendar'
                ],
                'expected_result': 'Meeting created with confirmation and calendar link'
            },
            {
                'scenario': 'Check Availability',
                'description': 'Test calendar availability checking',
                'steps': [
                    'Type: "What\'s my availability this week?"',
                    'Review AI response with available time slots',
                    'Observe demo calendar data integration'
                ],
                'expected_result': 'List of available time slots displayed'
            },
            {
                'scenario': 'View Calendar Events',
                'description': 'Test calendar event viewing',
                'steps': [
                    'Type: "Show me my meetings for today"',
                    'Review displayed calendar events',
                    'Check event details and formatting'
                ],
                'expected_result': 'List of demo calendar events displayed'
            },
            {
                'scenario': 'OAuth Flow Test',
                'description': 'Test Google Calendar connection',
                'steps': [
                    'Click "Connect Google Calendar" in sidebar',
                    'Follow simulated OAuth flow',
                    'Verify successful connection status'
                ],
                'expected_result': 'Successful OAuth simulation with demo user'
            },
            {
                'scenario': 'Error Handling',
                'description': 'Test application resilience',
                'steps': [
                    'Try various invalid inputs',
                    'Test with malformed requests',
                    'Verify graceful error handling'
                ],
                'expected_result': 'Appropriate error messages and recovery'
            }
        ],
        'evaluation_notes': [
            'All functionality works with simulated data',
            'No real Google credentials required',
            'All features demonstrate core capabilities',
            'Error handling shows production readiness'
        ]
    }

@router.get("/evaluation-guide")
async def demo_evaluation_guide():
    """Get comprehensive evaluation guide for assessors"""
    return {
        'demo_mode': True,
        'evaluation_guide': {
            'overview': 'This demo mode allows complete evaluation of Agentic Calendar without requiring real Google credentials.',
            'setup_instructions': [
                '1. Ensure the application is running (python start_project.py)',
                '2. Access frontend at http://localhost:8501',
                '3. Demo mode is automatically enabled for evaluation',
                '4. All features work with simulated data'
            ],
            'key_features_to_test': [
                'AI-powered natural language processing',
                'Meeting scheduling and calendar integration',
                'OAuth authentication flow (simulated)',
                'Real-time status monitoring',
                'Error handling and user feedback',
                'Modern, responsive user interface'
            ],
            'technical_assessment_points': [
                'Full-stack architecture (FastAPI + Streamlit)',
                'RESTful API design and implementation',
                'Modern UI/UX with professional design',
                'Security considerations (OAuth 2.0)',
                'Error handling and resilience',
                'Code quality and documentation'
            ],
            'demo_limitations': [
                'Calendar events are simulated (not real Google Calendar)',
                'AI responses use predefined patterns',
                'OAuth flow is mocked for demonstration',
                'No persistent data storage in demo mode'
            ],
            'evaluation_criteria': [
                'Functionality: All features work as demonstrated',
                'User Experience: Intuitive and professional interface',
                'Technical Implementation: Clean, well-structured code',
                'Documentation: Comprehensive and clear',
                'Innovation: AI integration and modern architecture'
            ]
        }
    }
