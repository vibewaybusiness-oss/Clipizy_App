# chatbot_router.py
# API Router for chatbot service
# ----------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import os
import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from api.services.chatbot.chatbot_service import get_chatbot_service, ChatbotService
from api.services.chatbot.chatbot_workflows import get_chatbot_workflows
from api.services.database import get_db
from api.services.auth import get_current_user
from api.models import User

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class ChatbotRequest(BaseModel):
    user_input: str = Field(..., description="User's request or prompt")
    input_tracks: int = Field(default=0, description="Number of audio tracks uploaded")
    input_images: int = Field(default=0, description="Number of images uploaded")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for multi-turn conversations")
    user_response: Optional[str] = Field(None, description="User's response to clarifying questions")

class ChatbotResponse(BaseModel):
    success: bool
    config: Optional[Dict[str, Any]] = None
    pipelines: Optional[List[Dict[str, Any]]] = None
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    error: Optional[str] = None
    conversation_id: Optional[str] = None
    raw_response: Optional[str] = None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/analyze", response_model=ChatbotResponse)
async def analyze_request(
    request: ChatbotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze user request and determine project configuration
    
    This endpoint uses DeepSeek/LLM to analyze the user's request and determine
    what type of project they want to create.
    """
    try:
        chatbot_service = get_chatbot_service()
        
        # Get user subscription tier
        # This is a simplified version - adjust based on your user model
        subscription_tier = getattr(current_user, 'subscription_tier', 'free')
        
        # If this is a continuation of a conversation
        if request.conversation_id and request.user_response:
            # Get current config from conversation history
            # In production, retrieve from Redis/DB
            # For now, try to get from the chatbot service's conversation history
            chatbot_service = get_chatbot_service()
            current_config = {}
            
            # Try to find conversation in history
            for conv in chatbot_service.conversation_history:
                if conv.get("conversation_id") == request.conversation_id:
                    current_config = conv.get("config", {})
                    break
            
            result = await chatbot_service.continue_conversation(
                conversation_id=request.conversation_id,
                user_response=request.user_response,
                current_config=current_config,
                input_tracks=request.input_tracks,
                input_images=request.input_images
            )
            
            # Get pipelines for updated config if available
            if result.get("success"):
                workflows_service = get_chatbot_workflows()
                pipelines_result = workflows_service.get_pipelines_for_project_type(
                    result.get("config", {}).get("project_type", "")
                )
                if pipelines_result.get("success"):
                    result["pipelines"] = pipelines_result.get("pipelines", [])
        else:
            # Initial request
            result = await chatbot_service.analyze_request(
                user_input=request.user_input,
                input_tracks=request.input_tracks,
                input_images=request.input_images,
                conversation_id=request.conversation_id,
                user_subscription_tier=subscription_tier
            )
        
        if not result.get("success"):
            return ChatbotResponse(
                success=False,
                error=result.get("error", "Unknown error"),
                needs_clarification=True
            )
        
        config = result.get("config", {})
        needs_clarification = result.get("needs_clarification", False)
        
        # Use conversational response if available, otherwise generate clarification question
        clarification_question = result.get("conversational_response")
        if not clarification_question and needs_clarification:
            missing_fields = result.get("missing_fields", [])
            if missing_fields:
                clarification_question = missing_fields[0]  # Use first missing field prompt
            else:
                clarification_question = _generate_clarification_question(config, request.input_tracks, request.input_images)
        
        return ChatbotResponse(
            success=True,
            config=config,
            pipelines=result.get("pipelines", []),
            needs_clarification=needs_clarification,
            clarification_question=clarification_question,
            conversation_id=result.get("conversation_id"),
            raw_response=result.get("raw_response")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing request: {str(e)}"
        )

def _generate_clarification_question(
    config: Dict[str, Any],
    input_tracks: int,
    input_images: int
) -> str:
    """Generate a clarification question based on missing fields"""
    
    project_type = config.get("project_type")
    
    if project_type == "music_video_clip" and not config.get("video_type"):
        return "What type of video would you like? (static, animated, or scene-based)"
    
    if input_tracks > 0 and project_type != "music_video_clip":
        return "You uploaded audio tracks. Do you want to create a music video?"
    
    if input_images > 0 and config.get("reference_images", 0) == 0:
        return "How should we use the images you uploaded? (reference images, style guide, etc.)"
    
    if not config.get("duration"):
        return "What duration would you like for your video? (in seconds)"
    
    if not config.get("visual_style"):
        return "What visual style are you looking for? (e.g., cinematic, abstract, vibrant, minimal)"
    
    return "I need a bit more information to set up your project. Can you provide more details?"

@router.get("/pipelines/{project_type}")
async def get_pipelines(
    project_type: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get available pipelines for a project type
    
    Returns pipelines with their required data fields
    """
    try:
        workflows_service = get_chatbot_workflows()
        result = workflows_service.get_pipelines_for_project_type(project_type)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to get pipelines")
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting pipelines: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "chatbot"}


# ============================================================================
# WORKFLOW CONFIG ENDPOINTS (serve JSON from backend configs directory)
# ============================================================================

# Resolve to: /root/clipizy/api/services/chatbot/configs
# Use Path.resolve() to ensure absolute path regardless of working directory
CONFIGS_DIR = str(Path(__file__).resolve().parent.parent.parent / "services" / "chatbot" / "configs")

@router.get("/workflows")
async def list_workflow_configs():
    try:
        files = [f for f in os.listdir(CONFIGS_DIR) if f.endswith('.json')]
        return {"success": True, "workflows": [os.path.splitext(f)[0] for f in files]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflow configs: {str(e)}")


@router.get("/workflows/{name}")
async def get_workflow_config(name: str):
    try:
        filename = f"{name}.json" if not name.endswith('.json') else name
        path = os.path.join(CONFIGS_DIR, filename)
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Looking for workflow config: {path}")
        logger.debug(f"CONFIGS_DIR: {CONFIGS_DIR}")
        logger.debug(f"File exists: {os.path.exists(path)}")
        
        if not os.path.isfile(path):
            logger.error(f"Workflow config not found at: {path}")
            logger.error(f"Available files in CONFIGS_DIR: {os.listdir(CONFIGS_DIR) if os.path.exists(CONFIGS_DIR) else 'CONFIGS_DIR does not exist'}")
            raise HTTPException(status_code=404, detail=f"Workflow config not found: {filename}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading workflow config {name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load workflow config: {str(e)}")

