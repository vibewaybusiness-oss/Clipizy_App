from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
from api.services.auth import get_current_user
from api.models import User
from api.services.ai.runpod.queues_service import compute_pod_signal

router = APIRouter(prefix="/api/ai/runpod", tags=["RunPod"])

@router.get("/health")
async def health_check():
    """Health check endpoint for RunPod router"""
    return {"status": "ok", "service": "runpod"}

@router.post("/signal-pod")
async def signal_pod(
    request_data: Dict[str, Any],
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Ensure a pod is available for the given workflow using existing queue manager/config.
    - Starts the queue manager if not running
    - Uses RUNPOD_CONFIG workflow.maxQueueSize and maxConcurrentPods
    - Since we don't manage real pods here, we simulate availability based on pending queue depth
    """
    try:
        workflow_name = request_data.get("workflow")
        if not workflow_name:
            raise HTTPException(status_code=400, detail="Workflow name is required")

        return await compute_pod_signal(workflow_name)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to signal pod: {str(e)}")

runpod_router = router
