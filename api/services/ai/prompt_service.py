import json
import random
from pathlib import Path
from typing import Dict, List, Optional

from api.config.logging import get_prompt_logger

logger = get_prompt_logger()

# Use RunPod config directory for prompt sources
PROMPTS_PATH = Path(__file__).resolve().parent / "runpod" / "config" / "prompts_random.json"
PROMPT_RULES_PATH = Path(__file__).resolve().parent / "runpod" / "config" / "prompt_rules.json"

# Load once at startup
try:
    with open(PROMPTS_PATH, encoding="utf-8") as f:
        PROMPTS = json.load(f)
except Exception as e:
    logger.error(f"Failed to load prompts from {PROMPTS_PATH}: {str(e)}")
    PROMPTS = {}

# Load prompt rules
try:
    with open(PROMPT_RULES_PATH, encoding="utf-8") as f:
        PROMPT_RULES = json.load(f)
except Exception as e:
    logger.error(f"Failed to load prompt rules from {PROMPT_RULES_PATH}: {str(e)}")
    PROMPT_RULES = {}


class PromptService:
    @staticmethod
    def _format_prompt(
        prompt_type: str, base_prompt: str, style: Optional[str] = None, instrumental: bool = False
    ) -> str:
        
        rules = PROMPT_RULES.get(prompt_type, {})
        if not rules:
            logger.warning(f"No rules found for prompt type: {prompt_type}")
            return base_prompt

        formatted_prompt = rules.get("prompt_prefix", "")
        formatted_prompt += base_prompt
        formatted_prompt += rules.get("prompt_suffix", "")
        if style and rules.get("style_true"):
            formatted_prompt += " " + rules["style_true"] + style
        if instrumental and rules.get("instrumental_true"):
            formatted_prompt += " " + rules["instrumental_true"]
        return formatted_prompt

    @staticmethod
    def get_random_prompt(
        prompt_type: str,
        categories: Optional[List[str]] = None,
        source: str = "json",
        style: Optional[str] = None,
        instrumental: bool = False,
        video_type: Optional[str] = None,
    ) -> Dict[str, str]:
        

        try:
            if source == "json":
                if prompt_type == "random_image":
                    if video_type == "scenes":
                        result = PromptService._get_from_json(
                            "video_prompts", categories, style, instrumental, video_type
                        )
                    else:
                        result = PromptService._get_from_json(
                            "image_prompts", categories, style, instrumental, video_type
                        )
                elif prompt_type == "random_video":
                    result = PromptService._get_from_json("video_prompts", categories, style, instrumental, video_type)
                else:
                    result = PromptService._get_from_json(prompt_type, categories, style, instrumental, video_type)
                return result
            elif source == "gemini":
                result = PromptService._get_from_gemini(prompt_type, style)
                return result
            elif source == "runpod":
                result = PromptService._get_from_runpod(prompt_type, style)
                return result
            else:
                logger.error(f"Invalid prompt source: {source}")
                raise ValueError("Invalid prompt source")
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            raise

    @staticmethod
    def _get_from_json(
        prompt_type: str,
        categories: Optional[List[str]],
        style: Optional[str],
        instrumental: bool = False,
        video_type: Optional[str] = None,
    ) -> Dict[str, str]:
        if prompt_type in ["image_prompts", "video_prompts"]:
            key = prompt_type
        else:
            key = f"{prompt_type}_prompts"

        if key not in PROMPTS:
            logger.error(f"Invalid prompt type: {prompt_type}. Available types: {list(PROMPTS.keys())}")
            raise ValueError(f"Invalid prompt type: {prompt_type}")

        if isinstance(PROMPTS[key], list):
            prompt = random.choice(PROMPTS[key])
            category = "video"
        else:
            available_categories = list(PROMPTS[key].keys())
            if categories:
                matching_category = None
                for requested_category in categories:
                    if requested_category in available_categories:
                        matching_category = requested_category
                        break
                if not matching_category:
                    for requested_category in categories:
                        for available_category in available_categories:
                            if (
                                requested_category.lower() in available_category.lower()
                                or available_category.lower() in requested_category.lower()
                            ):
                                matching_category = available_category
                                break
                        if matching_category:
                            break
                if matching_category:
                    category = matching_category
                else:
                    category = random.choice(available_categories)
                    logger.warning(f"No matching category found for {categories}, using random: {category}")
            else:
                category = random.choice(available_categories)
            prompt = random.choice(PROMPTS[key][category])
        formatted_prompt = PromptService._format_prompt(key, prompt, style, instrumental)
        result = {"prompt": formatted_prompt, "category": category, "source": "json"}
        return result