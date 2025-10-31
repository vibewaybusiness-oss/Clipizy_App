import asyncio
import time
from typing import Any, Dict, Optional, Union, List

from api.services.ai.runpod.queues_service import get_queue_manager
from api.schemas.ai.comfyui import WorkflowRequest, WorkflowType


class ImageQueueClient:
    def __init__(self) -> None:
        self.queue = get_queue_manager()

    async def start(self) -> None:
        if not self.queue.isRunning:
            await self.queue.start()

    async def execute(
        self,
        workflow_type: WorkflowType,
        inputs: Dict[str, Any],
        *,
        timeout_seconds: int = 300,
        poll_interval_seconds: float = 3.0,
    ) -> WorkflowRequest:
        await self.start()
        request_id = await self.queue.add_workflow_request(
            workflow_type.value,
            inputs,
            workflow_type,
        )
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            await asyncio.sleep(poll_interval_seconds)
            req = self.queue.get_request(request_id) or self.queue.get_comfyui_request(request_id)
            if not req:
                continue
            if req.status == "completed":
                return req
            if req.status == "failed":
                raise Exception()
        raise Exception()

    async def generate_image(
        self,
        *,
        prompt: str,
        reference_image: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        guidance: float = 7.5,
        seed: Optional[int] = None,
        timeout_seconds: int = 600,
        workflow_type: Optional[WorkflowType] = None,
    ) -> Union[str, Dict[str, Any]]:
        inputs: Dict[str, Any] = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "guidance": guidance,
        }
        if seed is not None:
            inputs["seed"] = seed
        if reference_image is not None:
            inputs["reference_image"] = reference_image

        effective_workflow = workflow_type
        if effective_workflow is None:
            if reference_image is None:
                effective_workflow = WorkflowType.IMAGE_FLUX
            else:
                effective_workflow = WorkflowType.IMAGE_QWEN_EDIT

        result = await self.execute(
            workflow_type=effective_workflow,
            inputs=inputs,
            timeout_seconds=timeout_seconds,
        )

        if result.status == "completed" and result.result:
            payload = result.result
            if isinstance(payload, dict):
                if "image" in payload:
                    return payload["image"]
                if "images" in payload and isinstance(payload["images"], list) and payload["images"]:
                    first: Union[str, Dict[str, Any]] = payload["images"][0]
                    return first
                return payload
            if isinstance(payload, list) and payload:
                return payload[0]

        raise Exception("Failed to generate image")


_image_client_instance: Optional[ImageQueueClient] = None


def get_image_client() -> ImageQueueClient:
    global _image_client_instance
    if _image_client_instance is None:
        _image_client_instance = ImageQueueClient()
    return _image_client_instance


def get_image_manager() -> ImageQueueClient:
    return get_image_client()


async def generate_image(
    prompt: str,
    reference_image: Optional[str] = None,
    width: int = 1024,
    height: int = 1024,
    steps: int = 30,
    guidance: float = 7.5,
    seed: Optional[int] = None,
    timeout_seconds: int = 600,
    workflow_type: Optional[WorkflowType] = None,
) -> Union[str, Dict[str, Any]]:
    client = get_image_client()
    return await client.generate_image(
        prompt=prompt,
        reference_image=reference_image,
        width=width,
        height=height,
        steps=steps,
        guidance=guidance,
        seed=seed,
        timeout_seconds=timeout_seconds,
        workflow_type=workflow_type,
    )

