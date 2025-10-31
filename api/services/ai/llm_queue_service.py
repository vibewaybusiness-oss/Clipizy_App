import asyncio
import time
from typing import Any, Dict, Optional

from api.services.ai.runpod.queues_service import get_queue_manager, RUNPOD_CONFIG
from api.schemas.ai.comfyui import WorkflowRequest, WorkflowType


class LLMQueueClient:
    def __init__(self) -> None:
        self.queue = get_queue_manager()

    async def start(self) -> None:
        if not self.queue.isRunning:
            await self.queue.start()

    async def execute(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        poll_interval_seconds: float = 3.0,
    ) -> str:
        await self.start()
        
        has_image = bool(image_url or image_base64)
        
        if has_image:
            workflow_name = "llm-qwen3-vl"
            default_model = "qwen3-vl"
            default_timeout = 300
        else:
            workflow_name = "llm-mistral"
            default_model = "mistral"
            default_timeout = 60
        
        if timeout_seconds is None:
            llm_ollama_cfg = RUNPOD_CONFIG.get("workflow", {}).get("llm-ollama", {})
            queue_cfg = llm_ollama_cfg.get(workflow_name, {})
            timeout_seconds = queue_cfg.get("generationTimeout", default_timeout)
        
        inputs: Dict[str, Any] = {
            "prompt": prompt,
            "model": model or default_model,
        }
        if image_url:
            inputs["image_url"] = image_url
        if image_base64:
            inputs["image_base64"] = image_base64
        
        request_id = await self.queue.add_workflow_request(
            workflow_name,
            inputs,
            WorkflowType.OLLAMA_LLM,
        )
        
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            await asyncio.sleep(poll_interval_seconds)
            req = self.queue.get_request(request_id) or self.queue.get_comfyui_request(request_id)
            if not req:
                continue
            if req.status == "completed":
                if req.result and isinstance(req.result, dict):
                    if req.result.get("response_text"):
                        return req.result["response_text"]
                if req.response_text:
                    return req.response_text
                raise Exception("LLM request completed but no response text in result")
            if req.status == "failed":
                error_msg = req.error or "LLM request failed"
                raise Exception(f"LLM request failed: {error_msg}")
        
        raise Exception(f"LLM request timed out after {timeout_seconds} seconds")


_llm_client_instance: Optional[LLMQueueClient] = None


def get_llm_queue_client() -> LLMQueueClient:
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMQueueClient()
    return _llm_client_instance

