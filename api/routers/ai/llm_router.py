from fastapi import APIRouter, HTTPException, Query, Request
from typing import Dict, Any, List, Optional

from api.services.ai.llm_service import generate_prompt
from api.config.logging import get_prompt_logger
from api.services.ai.prompt_service import PromptService
from api.routers.factory import create_ai_router
from api.middleware.auth_middleware import get_user_from_request

logger = get_prompt_logger()

# Create router using sophisticated architecture
router_wrapper = create_ai_router("llm", "", ["LLM AI"])  # Let architecture handle the prefix
router = router_wrapper.router

@router.get("/health")
async def llm_health():
    """Ensure LLM service is available and return simple health info."""
    try:
        return {"ok": True, "service": "llm"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {str(e)}")

@router.post("/generate")
async def generate_prompt_endpoint(prompt_data: Dict[str, Any], request: Request):
    """Generate AI prompts using LLM API (qwen-omni) - simplified version."""
    try:
        current_user = get_user_from_request(request)
        logger.info(f"LLM (qwen-omni) generation request from user: {current_user.email if current_user else 'unknown'}")
        
        prompt = prompt_data.get("prompt", "")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Generate response using LLM service
        result = await generate_prompt(prompt)
        
        return {
            "success": True,
            "generated_prompt": result,
            "original_prompt": prompt
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate prompt: {str(e)}")

@router.post("/generate-music-prompt")
async def generate_music_prompt(prompt_request: Dict[str, Any], request: Request):
    """Generate optimized music generation prompt from user input using LLM"""
    try:
        current_user = get_user_from_request(request)
        logger.info(f"Music prompt generation request from user: {current_user.email if current_user else 'unknown'}")
        
        user_input = prompt_request.get("user_input", "")
        genre = prompt_request.get("genre", "")
        project_id = prompt_request.get("project_id")
        
        if not user_input:
            raise HTTPException(status_code=400, detail="user_input is required")
        
        # Get pod_id from queue system for LLM workflow
        from api.services.ai.runpod.queues_service import compute_pod_signal, _get_active_pods_for_workflow
        
        workflow_name = "llm-mistral"
        logger.info(f"Signaling for LLM pod availability for workflow: {workflow_name}")
        await compute_pod_signal(workflow_name)
        
        active_pods = await _get_active_pods_for_workflow(workflow_name)
        
        if not active_pods:
            raise HTTPException(
                status_code=503,
                detail="No active LLM pods available. The system is setting up infrastructure. Please try again in a moment."
            )
        
        pod_id = active_pods[0].get("id")
        if not pod_id:
            raise HTTPException(
                status_code=500,
                detail="Active pod found but pod ID is missing. Please contact support."
            )
        
        logger.info(f"Using pod ID from queue system: {pod_id}")
        
        # Create prompt to optimize the user's music description
        music_prompt = f"""Create an optimized, detailed music generation prompt based on this user request:

User request: {user_input}
{f"Genre: {genre}" if genre else ""}

Generate a comprehensive music generation prompt that includes:
- BPM (beats per minute)
- Genre/style details
- Instrumentation
- Energy level and mood
- Production style
- Any specific technical requirements

Make it detailed and ready for music generation AI systems. Return ONLY the optimized prompt, no explanations."""
        
        optimized_prompt = await generate_prompt(music_prompt, pod_id=pod_id)
        
        return {
            "success": True,
            "data": {
                "prompt": optimized_prompt.strip(),
                "genre": genre or "electronic",
                "user_input": user_input
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate music prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate music prompt: {str(e)}")

@router.post("/generate-lyrics")
async def generate_lyrics(lyrics_request: Dict[str, Any], request: Request):
    """Generate lyrics for a music track using LLM"""
    try:
        current_user = get_user_from_request(request)
        logger.info(f"Lyrics generation request from user: {current_user.email if current_user else 'unknown'}")
        
        music_description = lyrics_request.get("music_description", "")
        genre = lyrics_request.get("genre", "")
        is_instrumental = lyrics_request.get("is_instrumental", False)
        
        if not music_description:
            raise HTTPException(status_code=400, detail="Music description is required")
        
        if is_instrumental:
            return {
                "success": True,
                "lyrics": "",
                "message": "Track is instrumental, no lyrics generated"
            }
        
        # Get pod_id from queue system for LLM workflow
        from api.services.ai.runpod.queues_service import compute_pod_signal, _get_active_pods_for_workflow
        
        workflow_name = "llm-mistral"
        logger.info(f"Signaling for LLM pod availability for workflow: {workflow_name}")
        await compute_pod_signal(workflow_name)
        
        active_pods = await _get_active_pods_for_workflow(workflow_name)
        
        if not active_pods:
            raise HTTPException(
                status_code=503,
                detail="No active LLM pods available. The system is setting up infrastructure. Please try again in a moment."
            )
        
        pod_id = active_pods[0].get("id")
        if not pod_id:
            raise HTTPException(
                status_code=500,
                detail="Active pod found but pod ID is missing. Please contact support."
            )
        
        logger.info(f"Using pod ID from queue system: {pod_id}")
        
        lyrics_prompt = f"""Generate song lyrics for a {genre if genre else 'music'} track.

Music description: {music_description}

Create engaging, creative lyrics that match the vibe and style described. Make them suitable for a music video. Format as verses and a chorus."""
        
        lyrics = await generate_prompt(lyrics_prompt, pod_id=pod_id)
        
        return {
            "success": True,
            "lyrics": lyrics,
            "genre": genre,
            "music_description": music_description
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate lyrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate lyrics: {str(e)}")

@router.post("/create_dynamic_scenes_script")
async def create_dynamic_scenes_script_endpoint(prompt_data: Dict[str, Any], request: Request):
    """Create dynamic scenes script with multiple scenes from a base prompt using simple LLM call."""
    try:
        current_user = get_user_from_request(request)
        logger.info(f"Dynamic scenes script request from user: {current_user.email if current_user else 'unknown'}")

        prompt = prompt_data.get("prompt", "")
        num_scenes = prompt_data.get("numScenes", 3)
        style = prompt_data.get("style", "")
        prompt_type = prompt_data.get("promptType", "video")

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        if not isinstance(num_scenes, int) or num_scenes < 1 or num_scenes > 10:
            raise HTTPException(status_code=400, detail="numScenes must be an integer between 1 and 10")

        planning_prompt = (
            f"You are a director planning a {prompt_type} with {num_scenes} scenes.\n"
            f"Base prompt: {prompt}.\n"
            f"Style: {style or 'any'}.\n"
            "Return a numbered list of concise scene descriptions with key visual elements."
        )

        scene_plan = await generate_prompt(planning_prompt)

        return {
            "success": True,
            "scene_planning_result": scene_plan,
            "generated_prompt": scene_plan,
            "original_prompt": prompt
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dynamic scenes script: {str(e)}")

@router.get("/random")
def get_random_prompt(
    prompt_type: str = Query(
        ..., regex="^(music|image|video|looped_video|image_prompts|video_prompts|random_image|random_video)$"
    ),
    categories: Optional[List[str]] = Query(None),
    source: str = Query("json", regex="^(json|gemini|runpod)$"),
    style: Optional[str] = None,
    instrumental: str = Query("false", description="Whether the music should be instrumental"),
    video_type: Optional[str] = Query(None, description="Video type for random prompts: looped-static or scenes"),
    request: Request = None
    ):
    """Fetch a random prompt from JSON, Gemini, or RunPod"""
    current_user = get_user_from_request(request)
    logger.info(f"Random prompt request from user: {current_user.email if current_user else 'unknown'}")
    
    # Convert string to boolean
    instrumental_bool = instrumental.lower() in ["true", "1", "yes", "on"]
    logger.info(
        f"DEBUG: Received instrumental parameter: {instrumental} (type: {type(instrumental)}) -> converted to: {instrumental_bool}"
    )
    logger.info(
        f"DEBUG: All parameters - prompt_type: {prompt_type}, categories: {categories}, source: {source}, style: {style}, instrumental: {instrumental_bool}, video_type: {video_type}"
    )
    
    result = PromptService.get_random_prompt(prompt_type, categories, source, style, instrumental_bool, video_type)
    return result
