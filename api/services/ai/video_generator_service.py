import asyncio
import time
from typing import Any, Dict, Optional, Union, List

from api.services.ai.runpod.queues_service import get_queue_manager
from api.schemas.ai.comfyui import WorkflowRequest, WorkflowType


class VideoQueueClient:
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
        timeout_seconds: int = 1200,
        poll_interval_seconds: float = 5.0,
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

    async def generate_video(
        self,
        *,
        prompt: str,
        reference_image: Optional[str] = None,
        duration_seconds: int = 5,
        width: int = 720,
        height: int = 1280,
        fps: int = 24,
        seed: Optional[int] = None,
        timeout_seconds: int = 1800,
        workflow_type: WorkflowType = WorkflowType.VIDEO_WAN,
    ) -> Dict[str, Any]:
        inputs: Dict[str, Any] = {
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "width": width,
            "height": height,
            "fps": fps,
        }
        if seed is not None:
            inputs["seed"] = seed
        if reference_image is not None:
            inputs["reference_image"] = reference_image

        result = await self.execute(
            workflow_type=workflow_type,
            inputs=inputs,
            timeout_seconds=timeout_seconds,
        )

        if result.status == "completed" and result.result:
            files = result.result.get("files") or []
            videos = result.result.get("videos") or []
            return {
                "files": files,
                "videos": videos,
                "request_id": result.id,
                "workflow_type": workflow_type.value,
            }

        raise Exception("Failed to generate video")


_video_client_instance: Optional[VideoQueueClient] = None


def get_video_client() -> VideoQueueClient:
    global _video_client_instance
    if _video_client_instance is None:
        _video_client_instance = VideoQueueClient()
    return _video_client_instance


def get_video_manager() -> VideoQueueClient:
    return get_video_client()


async def generate_video(
    prompt: str,
    reference_image: Optional[str] = None,
    duration_seconds: int = 5,
    width: int = 720,
    height: int = 1280,
    fps: int = 24,
    seed: Optional[int] = None,
    timeout_seconds: int = 1800,
    workflow_type: WorkflowType = WorkflowType.VIDEO_WAN,
) -> Dict[str, Any]:
    client = get_video_client()
    return await client.generate_video(
        prompt=prompt,
        reference_image=reference_image,
        duration_seconds=duration_seconds,
        width=width,
        height=height,
        fps=fps,
        seed=seed,
        timeout_seconds=timeout_seconds,
        workflow_type=workflow_type,
    )

