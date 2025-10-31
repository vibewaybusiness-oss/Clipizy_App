import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, List

from api.services.ai.llm_service import generate_prompt
from api.services.ai.llm_queue_service import get_llm_queue_client
from api.services.storage.backend_storage import backend_storage_service

logger = logging.getLogger(__name__)

LLM_CONFIGS_DIR = Path(__file__).parent


class LLMRequestHandler:
    """
    HANDLES WORKFLOW-BASED LLM REQUESTS
    Dynamically loads prompt configurations from JSON files based on workflow and prompt names
    """
    
    def __init__(self):
        self.config_cache: Dict[str, Dict[str, Any]] = {}
    
    def _load_workflow_config(self, workflow_name: str) -> Dict[str, Any]:
        """
        LOAD WORKFLOW CONFIGURATION FROM JSON FILE
        """
        if workflow_name in self.config_cache:
            return self.config_cache[workflow_name]
        
        config_file = LLM_CONFIGS_DIR / f"{workflow_name}-llm.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Workflow configuration not found: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.config_cache[workflow_name] = config
            logger.info(f"Loaded workflow configuration: {workflow_name}")
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in workflow configuration {config_file}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load workflow configuration {config_file}: {e}")
    
    def _format_prompt(
        self,
        prompt_template: str,
        arguments: Dict[str, Any],
        optional_arguments: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        FORMAT PROMPT TEMPLATE WITH PROVIDED ARGUMENTS
        Handles missing optional arguments by using empty strings
        """
        all_args = {**arguments}
        if optional_arguments:
            all_args.update(optional_arguments)
        
        try:
            formatted_prompt = prompt_template.format(**all_args)
            return formatted_prompt
        except KeyError as e:
            missing_key = str(e).strip("'\"")
            logger.warning(f"Missing argument '{missing_key}' in prompt template, using empty string")
            all_args[missing_key] = ""
            try:
                return prompt_template.format(**all_args)
            except KeyError:
                import re
                pattern = re.compile(r'\{(?:' + missing_key + r'[^}]*)\}')
                formatted_prompt = pattern.sub('', prompt_template)
                return formatted_prompt.strip()
    
    async def process_request(
        self,
        workflow: str,
        prompt: str,
        arguments: Dict[str, Any],
        optional_arguments: Optional[Dict[str, Any]] = None,
        image_base64: Optional[str] = None,
        image_file_path: Optional[str] = None,
        image_s3_key: Optional[str] = None,
        use_queue: bool = True
    ) -> str:
        """
        PROCESS LLM REQUEST FOR SPECIFIC WORKFLOW AND PROMPT
        
        Args:
            workflow: Workflow name (e.g., "music-clip")
            prompt: Prompt name (e.g., "generate-lyrics")
            arguments: Required arguments for the prompt
            optional_arguments: Optional arguments (e.g., image descriptions)
            image_base64: Optional base64-encoded image
            image_file_path: Optional path to image file
            image_s3_key: Optional S3 key for image file (will generate short-lived presigned URL)
            use_queue: Whether to use queue system (default: True) for pod management
            
        Returns:
            LLM-generated response text
        """
        try:
            config = self._load_workflow_config(workflow)
            
            if "prompts" not in config:
                raise ValueError(f"No prompts defined in workflow configuration: {workflow}")
            
            prompts_config = config["prompts"]
            
            if prompt not in prompts_config:
                available = ", ".join(prompts_config.keys())
                raise ValueError(
                    f"Prompt '{prompt}' not found in workflow '{workflow}'. "
                    f"Available prompts: {available}"
                )
            
            prompt_config = prompts_config[prompt]
            
            prompt_template = prompt_config.get("template", "")
            if not prompt_template:
                raise ValueError(f"Prompt template not found for '{workflow}.{prompt}'")
            
            formatted_prompt = self._format_prompt(
                prompt_template=prompt_template,
                arguments=arguments,
                optional_arguments=optional_arguments
            )
            
            logger.info(f"Processing LLM request: {workflow}.{prompt}")
            logger.debug(f"Formatted prompt: {formatted_prompt[:200]}...")
            
            image_url = None
            if image_s3_key:
                try:
                    image_url = backend_storage_service.get_short_lived_image_url(image_s3_key)
                    logger.info(f"Generated short-lived image URL for S3 key: {image_s3_key}")
                except Exception as e:
                    logger.error(f"Failed to generate image URL for S3 key {image_s3_key}: {e}")
                    raise
            
            if use_queue:
                logger.info(f"Using queue system for LLM request: {workflow}.{prompt}")
                queue_client = get_llm_queue_client()
                response = await queue_client.execute(
                    prompt=formatted_prompt,
                    model=prompt_config.get("model"),
                    image_url=image_url,
                    image_base64=image_base64,
                    timeout_seconds=prompt_config.get("timeout_seconds", 300)
                )
            else:
                logger.info(f"Using direct LLM call for: {workflow}.{prompt}")
                response = await generate_prompt(
                    prompt=formatted_prompt,
                    image_base64=image_base64,
                    image_file_path=image_file_path,
                    image_url=image_url,
                    model=prompt_config.get("model"),
                    timeout_seconds=prompt_config.get("timeout_seconds", 300)
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process LLM request {workflow}.{prompt}: {e}")
            raise
    
    def get_available_workflows(self) -> List[str]:
        """
        GET LIST OF AVAILABLE WORKFLOW CONFIGURATIONS
        """
        workflows = []
        for file in LLM_CONFIGS_DIR.glob("*-llm.json"):
            workflow_name = file.stem.replace("-llm", "")
            workflows.append(workflow_name)
        return workflows
    
    def get_workflow_prompts(self, workflow: str) -> List[str]:
        """
        GET LIST OF AVAILABLE PROMPTS FOR A WORKFLOW
        """
        try:
            config = self._load_workflow_config(workflow)
            prompts_config = config.get("prompts", {})
            return list(prompts_config.keys())
        except Exception as e:
            logger.error(f"Failed to get prompts for workflow {workflow}: {e}")
            return []


_llm_request_handler = None


def get_llm_request_handler() -> LLMRequestHandler:
    """
    GET SINGLETON LLM REQUEST HANDLER INSTANCE
    """
    global _llm_request_handler
    if _llm_request_handler is None:
        _llm_request_handler = LLMRequestHandler()
    return _llm_request_handler

