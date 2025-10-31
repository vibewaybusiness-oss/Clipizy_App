import json
import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from api.services.ai.llm_service import generate_prompt

logger = logging.getLogger(__name__)

class ChatbotService:
    """Service for analyzing user input and determining project configuration"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
    
    async def analyze_request(
        self,
        user_input: str,
        input_tracks: int = 0,
        input_images: int = 0,
        conversation_id: Optional[str] = None,
        user_subscription_tier: str = "free"
    ) -> Dict[str, Any]:
        """Analyze user request and determine project configuration"""
        
        try:
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            analysis_prompt = self._build_analysis_prompt(
                user_input=user_input,
                input_tracks=input_tracks,
                input_images=input_images,
                user_subscription_tier=user_subscription_tier
            )
            
            raw_response = await generate_prompt(analysis_prompt)
            
            config = self._parse_llm_response(raw_response, input_tracks, input_images)
            
            needs_clarification = self._check_if_clarification_needed(config)
            missing_fields = self._get_missing_fields(config) if needs_clarification else []
            
            conversation_entry = {
                "conversation_id": conversation_id,
                "user_input": user_input,
                "config": config,
                "timestamp": datetime.utcnow().isoformat(),
                "raw_response": raw_response
            }
            self.conversation_history.append(conversation_entry)
            
            return {
                "success": True,
                "config": config,
                "needs_clarification": needs_clarification,
                "missing_fields": missing_fields,
                "conversation_id": conversation_id,
                "raw_response": raw_response,
                "conversational_response": None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "config": {},
                "needs_clarification": True
            }
    
    async def continue_conversation(
        self,
        conversation_id: str,
        user_response: str,
        current_config: Dict[str, Any],
        input_tracks: int = 0,
        input_images: int = 0
    ) -> Dict[str, Any]:
        """Continue conversation with user response to clarify configuration"""
        
        try:
            continuation_prompt = self._build_continuation_prompt(
                user_response=user_response,
                current_config=current_config,
                input_tracks=input_tracks,
                input_images=input_images
            )
            
            raw_response = await generate_prompt(continuation_prompt)
            
            updated_config = self._update_config_from_response(
                current_config=current_config,
                llm_response=raw_response,
                user_response=user_response
            )
            
            needs_clarification = self._check_if_clarification_needed(updated_config)
            missing_fields = self._get_missing_fields(updated_config) if needs_clarification else []
            
            for conv in self.conversation_history:
                if conv.get("conversation_id") == conversation_id:
                    conv["config"] = updated_config
                    conv["user_response"] = user_response
                    conv["timestamp"] = datetime.utcnow().isoformat()
                    break
            
            return {
                "success": True,
                "config": updated_config,
                "needs_clarification": needs_clarification,
                "missing_fields": missing_fields,
                "conversation_id": conversation_id,
                "raw_response": raw_response,
                "conversational_response": None
            }
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "config": current_config,
                "needs_clarification": True
            }
    
    def _build_analysis_prompt(
        self,
        user_input: str,
        input_tracks: int,
        input_images: int,
        user_subscription_tier: str
    ) -> str:
        """Build prompt for LLM analysis"""
        
        prompt = f"""Analyze the user's request and determine the project configuration.

        User Request: "{user_input}"

        Context:
        - Audio tracks uploaded: {input_tracks}
        - Images uploaded: {input_images}
        - Subscription tier: {user_subscription_tier}

        Determine the following project configuration:
        1. project_type: One of: "music_video_clip", "video_clip", "business_ad", "automate_workflow"
        2. If music_video_clip, determine video_type: One of: "looped-static", "looped-animated", "recurring-scenes"
        3. visual_style: Describe the visual style (e.g., "cinematic", "abstract", "vibrant", "minimal")
        4. duration: Estimated duration in seconds (default: 30)
        5. prompt_user_input: Enhanced version of user's input for video generation
        6. reference_images: Count of reference images ({input_images})

        Respond in JSON format only:
        {{
        "project_type": "...",
        "video_type": "..." (if project_type is music_video_clip),
        "visual_style": "...",
        "duration": ...,
        "prompt_user_input": "...",
        "reference_images": {input_images}
        }}

        If you cannot determine some fields, include them as null or empty. Only respond with valid JSON, no additional text."""
        
        return prompt
    
    def _build_continuation_prompt(
        self,
        user_response: str,
        current_config: Dict[str, Any],
        input_tracks: int,
        input_images: int
    ) -> str:
        """Build prompt for conversation continuation"""
        
        prompt = f"""Update the project configuration based on the user's response to a clarification question.

        Current Configuration:
        {json.dumps(current_config, indent=2)}

        User Response: "{user_response}"

        Context:
        - Audio tracks uploaded: {input_tracks}
        - Images uploaded: {input_images}

        Update the configuration based on the user's response. Fill in missing fields or update existing ones.

        Respond in JSON format only with the updated configuration:
        {{
        "project_type": "...",
        "video_type": "..." (if project_type is music_video_clip),
        "visual_style": "...",
        "duration": ...,
        "prompt_user_input": "...",
        "reference_images": {input_images}
        }}

        Only respond with valid JSON, no additional text."""
        
        return prompt
    
    def _parse_llm_response(self, response: str, input_tracks: int, input_images: int) -> Dict[str, Any]:
        """Parse LLM response into configuration dict"""
        
        try:
            cleaned_response = response.strip()
            
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response.replace("```json", "").replace("```", "").strip()
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.replace("```", "").strip()
            
            config = json.loads(cleaned_response)
            
            defaults = {
                "project_type": "music_video_clip" if input_tracks > 0 else "video_clip",
                "visual_style": "cinematic",
                "duration": 30,
                "prompt_user_input": "",
                "reference_images": input_images
            }
            
            for key, default_value in defaults.items():
                if key not in config or config[key] is None:
                    config[key] = default_value
            
            if config.get("project_type") == "music_video_clip" and not config.get("video_type"):
                config["video_type"] = "recurring-scenes"
            
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.debug(f"Response content: {response[:500]}")
            
            return {
                "project_type": "music_video_clip" if input_tracks > 0 else "video_clip",
                "video_type": "recurring-scenes" if input_tracks > 0 else None,
                "visual_style": "cinematic",
                "duration": 30,
                "prompt_user_input": response[:500] if response else "",
                "reference_images": input_images
            }
    
    def _update_config_from_response(
        self,
        current_config: Dict[str, Any],
        llm_response: str,
        user_response: str
    ) -> Dict[str, Any]:
        """Update configuration based on LLM response"""
        
        try:
            updated = self._parse_llm_response(llm_response, 0, current_config.get("reference_images", 0))
            
            for key, value in updated.items():
                if value and value not in [None, "", []]:
                    current_config[key] = value
            
            if not current_config.get("prompt_user_input") and user_response:
                current_config["prompt_user_input"] = user_response
            
            return current_config
            
        except Exception as e:
            logger.error(f"Error updating config: {str(e)}")
            return current_config
    
    def _check_if_clarification_needed(self, config: Dict[str, Any]) -> bool:
        """Check if clarification is needed based on missing fields"""
        
        project_type = config.get("project_type")
        
        if not project_type:
            return True
        
        if project_type == "music_video_clip" and not config.get("video_type"):
            return True
        
        if not config.get("visual_style"):
            return True
        
        if not config.get("duration"):
            return True
        
        return False
    
    def _get_missing_fields(self, config: Dict[str, Any]) -> List[str]:
        """Get list of missing field prompts"""
        
        missing = []
        
        project_type = config.get("project_type")
        if not project_type:
            missing.append("What type of project would you like to create? (music video, video clip, business ad, etc.)")
        
        if project_type == "music_video_clip" and not config.get("video_type"):
            missing.append("What type of video would you like? (static, animated, or scene-based)")
        
        if not config.get("visual_style"):
            missing.append("What visual style are you looking for? (e.g., cinematic, abstract, vibrant, minimal)")
        
        if not config.get("duration"):
            missing.append("What duration would you like for your video? (in seconds)")
        
        return missing

_chatbot_service = None

def get_chatbot_service() -> ChatbotService:
    """Get singleton chatbot service instance"""
    
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service

