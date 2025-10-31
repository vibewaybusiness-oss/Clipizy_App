from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from api.services.ai.runpod.queues_service import get_queue_manager


class MusicAnalysisInput(BaseModel):
    project_id: Optional[str] = Field(None, description="Optional project identifier")
    file_path: str = Field(..., description="Absolute path to the audio file on disk")
    analyzer: bool = Field(True, description="Run DSP segmentation and analysis")
    llm_analyzer: bool = Field(True, description="Run LLM full-track and per-segment analysis")


class MusicAnalysisQueueClient:
    def __init__(self) -> None:
        self.queue = get_queue_manager()

    async def start(self) -> None:
        if not self.queue.isRunning:
            await self.queue.start()

    async def enqueue(
        self,
        *,
        project_id: Optional[str],
        file_path: str,
        analyzer: bool = True,
        llm_analyzer: bool = True,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        await self.start()
        payload = MusicAnalysisInput(
            project_id=project_id,
            file_path=file_path,
            analyzer=analyzer,
            llm_analyzer=llm_analyzer,
        ).dict()
        if extra:
            payload.update(extra)

        # We intentionally pass workflow_type=None so this request is handled by
        # an external worker (not ComfyUI-specific handling).
        request_id = await self.queue.add_workflow_request(
            "music_analyzer",
            payload,
            workflow_type=None,
        )
        return request_id

    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        req = self.queue.get_request(request_id)
        if not req:
            return None
        return req.dict()


_music_client_instance: Optional[MusicAnalysisQueueClient] = None


def get_music_analysis_client() -> MusicAnalysisQueueClient:
    global _music_client_instance
    if _music_client_instance is None:
        _music_client_instance = MusicAnalysisQueueClient()
    return _music_client_instance


async def enqueue_music_analysis(
    *,
    project_id: Optional[str],
    file_path: str,
    analyzer: bool = True,
    llm_analyzer: bool = True,
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    client = get_music_analysis_client()
    return await client.enqueue(
        project_id=project_id,
        file_path=file_path,
        analyzer=analyzer,
        llm_analyzer=llm_analyzer,
        extra=extra,
    )


