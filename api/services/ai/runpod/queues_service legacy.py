# queues_service.py
# Unified queue management system for workflows
# ----------------------------------------------------------
from __future__ import annotations

import asyncio
import json
import os
import random
import string
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic import BaseModel, Field

# Import schemas
from api.schemas.ai.comfyui import ActivePod, WorkflowRequest, WorkflowType

# --- env + config ------------------------------------------------------------

CWD = Path(os.getcwd())
# Load .env files safely, ignore errors
try:
    load_dotenv(CWD / ".env")
    load_dotenv(CWD / ".env.local", override=True)
except Exception as e:
    print(f"Warning: Could not load .env files: {e}")

# Load both configuration files
# Handle both cases: running from root or from api directory
if (CWD / "api" / "config" / "json" / "runpod_config.json").exists():
    RUNPOD_CONFIG_PATH = CWD / "api" / "config" / "json" / "runpod_config.json"
    COMFYUI_CONFIG_PATH = CWD / "api" / "config" / "json" / "comfyui_config.json"
    LLM_CONFIG_PATH = CWD / "api" / "config" / "json" / "llm_config.json"
elif (CWD / "config" / "runpod_config.json").exists():
    RUNPOD_CONFIG_PATH = CWD / "config" / "runpod_config.json"
    COMFYUI_CONFIG_PATH = CWD / "config" / "comfyui_config.json"
    LLM_CONFIG_PATH = CWD / "config" / "llm_config.json"
else:
    # Fallback: try to find the config files relative to this script
    script_dir = Path(__file__).parent.parent
    RUNPOD_CONFIG_PATH = script_dir / "config" / "json" / "runpod_config.json"
    COMFYUI_CONFIG_PATH = script_dir / "config" / "json" / "comfyui_config.json"
    LLM_CONFIG_PATH = script_dir / "config" / "json" / "llm_config.json"

if not RUNPOD_CONFIG_PATH.exists():
    raise RuntimeError(f"Missing config file at {RUNPOD_CONFIG_PATH}")

if not COMFYUI_CONFIG_PATH.exists():
    raise RuntimeError(f"Missing config file at {COMFYUI_CONFIG_PATH}")

with RUNPOD_CONFIG_PATH.open("r", encoding="utf-8") as f:
    RUNPOD_CONFIG: Dict[str, Any] = json.load(f)

with COMFYUI_CONFIG_PATH.open("r", encoding="utf-8") as f:
    COMFYUI_CONFIG: Dict[str, Any] = json.load(f)

# Loadconfig if it exists
LLM_CONFIG: Dict[str, Any] = {}
if LLM_CONFIG_PATH.exists():
    with LLM_CONFIG_PATH.open("r", encoding="utf-8") as f:
        LLM_CONFIG = json.load(f)

# --- types -------------------------------------------------------------------

StatusReq = Literal["pending", "processing", "completed", "failed"]
StatusPod = Literal["running", "paused", "terminated"]


class QueueStatus(BaseModel):
    activePods: List[Dict[str, Any]]
    pendingRequests: Dict[str, List[Dict[str, Any]]]
    isRunning: bool
    # ComfyUI specific status
    comfyuiRequests: Optional[Dict[str, int]] = None


class AddWorkflowBody(BaseModel):
    workflowName: str = Field(..., description="Name of the workflow")
    requestData: Any = Field(..., description="Arbitrary request payload")
    workflow_type: Optional[WorkflowType] = Field(None, description="ComfyUI workflow type")


class MarkBody(BaseModel):
    result: Optional[Any] = None
    error: Optional[str] = None


# --- manager -----------------------------------------------------------------


class UnifiedQueueManager:
    def __init__(self) -> None:
        self.pendingRequests: Dict[str, List[WorkflowRequest]] = {}
        self.isRunning: bool = False
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._pod_manager = None

        # ComfyUI specific
        self.comfyui_requests: Dict[str, WorkflowRequest] = {}
        self._initialized = False

        # Pod creation tracking to prevent duplicates
        self._pod_creation_in_progress: Dict[str, bool] = {}

        # Load configuration
        self._load_config()

    def _load_config(self):
        """Load and merge configuration from all config files"""
        # Queue settings from RunPod config
        qs = RUNPOD_CONFIG.get("queueSettings", {})
        self.check_interval_ms: int = int(qs.get("checkInterval", 2000))

        # Workflow settings from ComfyUI config
        self.workflow_configs = COMFYUI_CONFIG.get("workflows", {})
        self.default_config = COMFYUI_CONFIG.get("defaults", {})

        # Addworkflow configs
        llm_workflows = LLM_CONFIG.get("workflows", {})
        self.workflow_configs.update(llm_workflows)

        # Update default config withdefaults if available
        llm_defaults = LLM_CONFIG.get("defaults", {})
        for key, value in llm_defaults.items():
            if key not in self.default_config:
                self.default_config[key] = value

    def _get_pod_manager(self):
        """Get the pod manager instance"""
        if self._pod_manager is None:
            self._pod_manager = get_pod_manager()
        return self._pod_manager

    # --- lifecycle ------------------------------------------------------------

    async def start(self) -> None:
        async with self._lock:
            if self.isRunning:
                return
            self.isRunning = True
            self._task = asyncio.create_task(self._loop(), name="unified-queue-loop")
            self._initialized = True

    async def stop(self) -> None:
        async with self._lock:
            if not self.isRunning:
                return
            self.isRunning = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        # Clean up pods through pod manager
        pod_manager = self._get_pod_manager()
        await pod_manager.close()

    async def cleanup(self) -> None:
        """Clean up all resources"""
        await self.stop()
        self.pendingRequests.clear()
        self.comfyui_requests.clear()
        self._pod_creation_in_progress.clear()

    # --- public API -----------------------------------------------------------

    async def add_workflow_request(
        self, workflow_name: str, request_data: Any, workflow_type: Optional[WorkflowType] = None
    ) -> str:
        """Add a workflow request to the queue"""
        print(f"\n📥 ===== ADDING WORKFLOW REQUEST TO QUEUE =====")
        print(f"📋 Workflow Name: {workflow_name}")
        print(f"📝 Request Data: {request_data}")
        print(f"🏷️ Workflow Type: {workflow_type}")

        workflow_name = workflow_name.lower()
        rid = f"req_{int(time.time()*1000)}_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=9))

        print(f"🆔 Generated Request ID: {rid}")

        # Map workflow name to workflow type if not provided
        if not workflow_type:
            workflow_type_map = {
                "comfyui_image_qwen": WorkflowType.IMAGE_QWEN,
                "comfyui_image_flux": WorkflowType.IMAGE_FLUX,
                "comfyui_video_wan": WorkflowType.VIDEO_WAN,
                "comfyui_audio_mmaudio": WorkflowType.AUDIO_MMAUDIO,
                "comfyui_voice_voicemaker": WorkflowType.VOICE_VOICEMAKER,
                "comfyui_upscaling": WorkflowType.UPSCALING,
                "comfyui_interpolation": WorkflowType.INTERPOLATION,
                "llm_llm": WorkflowType.LLM_LLM,
                "ollama": WorkflowType.OLLAMA_LLM,
                # Legacy mappings for backward compatibility
                "qwen_image": WorkflowType.IMAGE_QWEN,
                "flux_image": WorkflowType.IMAGE_FLUX,
                "wan_video": WorkflowType.VIDEO_WAN,
                "mmaudio": WorkflowType.AUDIO_MMAUDIO,
                "voicemaker": WorkflowType.VOICE_VOICEMAKER,
                "upscaling": WorkflowType.UPSCALING,
                "interpolation": WorkflowType.INTERPOLATION,
                "llm": WorkflowType.LLM_LLM,
            }
            workflow_type = workflow_type_map.get(workflow_name, WorkflowType.IMAGE_QWEN)
            print(f"🔄 Mapped workflow type: {workflow_type}")

        req = WorkflowRequest(id=rid, workflow_type=workflow_type, inputs=request_data, status="pending")
        async with self._lock:
            self.pendingRequests.setdefault(workflow_name, []).append(req)
            if workflow_type:
                self.comfyui_requests[rid] = req
        # nudge the loop without waiting for the next tick
        asyncio.create_task(self._process_queue_once())
        return rid

    def get_queue_status(self) -> QueueStatus:
        """Get current queue status including ComfyUI requests"""
        pending: Dict[str, List[Dict[str, Any]]] = {}
        for name, reqs in self.pendingRequests.items():
            pending[name] = [r.dict() for r in reqs if r.status == "pending"]

        # ComfyUI specific status
        comfyui_status = {
            "total": len(self.comfyui_requests),
            "active": len([r for r in self.comfyui_requests.values() if r.status in ("pending", "processing")]),
            "completed": len([r for r in self.comfyui_requests.values() if r.status in ("completed", "failed")]),
            "pending": len([r for r in self.comfyui_requests.values() if r.status == "pending"]),
        }

        # Get active pods from pod manager
        pod_manager = self._get_pod_manager()
        active_pods = [p.dict() for p in pod_manager.get_active_pods().values()]

        return QueueStatus(
            activePods=active_pods, pendingRequests=pending, isRunning=self.isRunning, comfyuiRequests=comfyui_status
        )

    async def get_pod_for_workflow(self, workflow_name: str) -> Optional[ActivePod]:
        """Get an available pod for a specific workflow. Will restart paused pods if found."""
        pod_manager = self._get_pod_manager()
        return await pod_manager.find_available_pod(workflow_name.lower())

    def get_pod_by_id(self, pod_id: str) -> Optional[ActivePod]:
        """Get a pod by its ID"""
        pod_manager = self._get_pod_manager()
        return pod_manager.get_pod_by_id(pod_id)

    async def get_pod_with_ip(self, pod_id: str, max_attempts: int = 12) -> Dict[str, Any]:
        """Get pod with IP address, waiting if necessary"""
        pod_manager = self._get_pod_manager()

        # Check if pod is already ready in our active pods
        pod = pod_manager.get_pod_by_id(pod_id)
        if pod and pod.status == "running":
            # Pod is already ready, get connection info directly
            print(f"✅ Pod {pod_id} is already ready, getting connection info directly")
            return await pod_manager.get_pod_public_ip(pod_id)

        # Pod is not ready, wait for it
        print(f"⏳ Pod {pod_id} is not ready (status: {pod.status if pod else 'not found'}), waiting for it")
        return await pod_manager.wait_for_pod_ready(pod_id, max_attempts)

    def mark_request_completed(self, request_id: str, result: Any = None) -> bool:
        """Mark a request as completed"""
        # Update in ComfyUI requests
        if request_id in self.comfyui_requests:
            self.comfyui_requests[request_id].status = "completed"
            self.comfyui_requests[request_id].result = result
            self.comfyui_requests[request_id].completed_at = datetime.fromtimestamp(time.time())
            return True

        return False

    def mark_request_failed(self, request_id: str, error: Optional[str] = None) -> bool:
        """Mark a request as failed"""
        # Update in ComfyUI requests
        if request_id in self.comfyui_requests:
            self.comfyui_requests[request_id].status = "failed"
            self.comfyui_requests[request_id].error = error
            self.comfyui_requests[request_id].completed_at = datetime.fromtimestamp(time.time())
            return True

        return False

    # --- ComfyUI specific methods --------------------------------------------

    def get_comfyui_request(self, request_id: str) -> Optional[WorkflowRequest]:
        """Get a ComfyUI request by ID"""
        return self.comfyui_requests.get(request_id)

    def get_all_comfyui_requests(self) -> List[WorkflowRequest]:
        """Get all ComfyUI requests"""
        return list(self.comfyui_requests.values())

    def get_active_comfyui_requests(self) -> List[WorkflowRequest]:
        """Get active ComfyUI requests"""
        return [r for r in self.comfyui_requests.values() if r.status in ("pending", "processing")]

    def get_completed_comfyui_requests(self) -> List[WorkflowRequest]:
        """Get completed ComfyUI requests"""
        return [r for r in self.comfyui_requests.values() if r.status in ("completed", "failed")]

    def get_workflow_config(self, workflow_name: str) -> Dict[str, Any]:
        """Get configuration for a specific workflow"""
        return self.workflow_configs.get(workflow_name, self.default_config)

    def get_max_queue_size(self, workflow_name: str) -> int:
        """Get maximum queue size for a workflow"""
        config = self.get_workflow_config(workflow_name)
        return config.get("maxQueueSize", self.default_config.get("maxQueueSize", 3))

    # --- internal loop --------------------------------------------------------

    async def _loop(self) -> None:
        try:
            while self.isRunning:
                await self._process_queue_once()
                await asyncio.sleep(self.check_interval_ms / 1000.0)
        except asyncio.CancelledError:
            pass

    async def _process_queue_once(self) -> None:
        if not self.isRunning:
            return

        # Use a global lock to prevent multiple queue processing at the same time
        if hasattr(self, "_processing_lock"):
            if self._processing_lock.locked():
                print(f"⏳ Queue processing already in progress, skipping...")
                return
        else:
            self._processing_lock = asyncio.Lock()

        async with self._processing_lock:
            # print(f"\n🔄 ===== PROCESSING QUEUE ONCE =====")

            async with self._lock:
                workflow_items = list(self.pendingRequests.items())

            for workflow_name, requests in workflow_items:
                pending_count = len([r for r in requests if r.status == "pending"])
                if pending_count > 0:
                    print(f"   {workflow_name}: {len(requests)} total, {pending_count} pending requests")

            for workflow_name, requests in workflow_items:
                pending_requests = [r for r in requests if r.status == "pending"]
                if not pending_requests:
                    continue

                print(f"\n🔍 Processing workflow: {workflow_name} ({len(pending_requests)} pending requests)")

                pod_manager = self._get_pod_manager()

                # Check for available pod first (this will restart paused pods if found)
                pod = await pod_manager.find_available_pod(workflow_name)

                if pod:
                    print(f"✅ Found available pod: {pod.id}")
                else:
                    print(f"❌ No available pod for {workflow_name}")

                    # Check if we can create more pods for this workflow
                    current_pod_count = pod_manager.get_workflow_pod_count(workflow_name)
                    max_pods = pod_manager.get_max_pods_per_workflow(workflow_name)

                    print(f"📊 Pod count: {current_pod_count}/{max_pods}")

                    if current_pod_count >= max_pods:
                        print(f"⚠️ Max pods reached for {workflow_name}, skipping")
                        continue  # Skip if we've reached the limit

                    # Double-check pod count again after acquiring lock to prevent race conditions
                    async with self._lock:
                        current_pod_count = pod_manager.get_workflow_pod_count(workflow_name)
                        if current_pod_count >= max_pods:
                            print(f"⚠️ Max pods reached for {workflow_name} (race condition prevented), skipping")
                            continue

                        # Check if pod creation is already in progress for this workflow
                        if self._pod_creation_in_progress.get(workflow_name, False):
                            print(f"⏳ Pod creation already in progress for {workflow_name}, skipping")
                            continue

                        # Check again if a pod became available while we were waiting (including restarted paused pods)
                        pod = await pod_manager.find_available_pod(workflow_name)
                        if pod:
                            print(f"✅ Found available pod after lock: {pod.id}")
                        else:
                            # Mark pod creation as in progress
                            self._pod_creation_in_progress[workflow_name] = True
                            try:
                                # Create new pod
                                print(f"🚀 Creating new pod for {workflow_name}...")
                                pod = await pod_manager.create_pod_for_workflow(workflow_name)
                            finally:
                                # Always clear the flag, even if creation fails
                                self._pod_creation_in_progress[workflow_name] = False

                if pod:
                    print(f"✅ Processing requests for pod {pod.id}")
                    await self._process_pod_requests(pod)
                else:
                    print(f"❌ No pod available for {workflow_name}")

            # Check pod timeouts
            pod_manager = self._get_pod_manager()
            await pod_manager.check_pod_timeouts()

    async def _process_pod_requests(self, pod: ActivePod) -> None:
        """Process requests for a specific pod"""
        # Only process pods that are fully ready
        if pod.status != "running":
            print(f"❌ Pod {pod.id} is not fully ready, status: {pod.status}")
            return

        # Get max queue size for this workflow
        max_queue_size = self.get_max_queue_size(pod.workflowName)

        # move up to max_queue_size - current queued
        capacity = max_queue_size - len(pod.requestQueue)
        if capacity <= 0:
            print(f"❌ Pod {pod.id} has no capacity for {pod.workflowName}")
            return

        async with self._lock:
            all_requests = self.pendingRequests.get(pod.workflowName, [])
            pending = [r for r in all_requests if r.status == "pending"]
            to_process = pending[:capacity]
            # Remove processed requests from the list
            remaining = [r for r in all_requests if r not in to_process]
            self.pendingRequests[pod.workflowName] = remaining

        print(f"🔍 Pod {pod.id}: Pending requests: {[req.id for req in pending]}")
        print(f"🔍 Pod {pod.id}: To process: {[req.id for req in to_process]}")
        print(
            f"🔍 Pod {pod.id}: Pending requests after processing: {[req.id for req in self.pendingRequests.get(pod.workflowName, [])]}"
        )

        if not to_process:
            print(f"❌ Pod {pod.id} has no pending requests to process")
            return

        # mark + assign
        for req in to_process:
            req.status = "processing"
            req.pod_id = pod.id
        pod.request_queue.extend(to_process)

        # Requests are now assigned to the pod and ready for processing
        print(f"✅ Assigned {len(to_process)} requests to pod {pod.id}")

        # update timers
        now = int(time.time() * 1000)
        pod.last_used_at = now
        pod_manager = self._get_pod_manager()
        pause_s, term_s = pod_manager.get_workflow_timeouts(pod.workflow_name)
        pod.pause_timeout_at = now + pause_s * 1000
        pod.terminate_timeout_at = now + term_s * 1000

        # resume if paused
        if pod.status == "paused":
            try:
                result = await pod_manager.resume_pod(pod.id)
                if result.get("success"):
                    pod.status = "running"
                    pod.pausedAt = None
                else:
                    print(f"❌ Failed to resume pod {pod.id} for {pod.workflowName}")
                    return
            except Exception:
                print(f"❌ Failed to resume pod {pod.id} for {pod.workflowName}")
                return

        # Execute workflows on the pod
        print(f"🚀 Executing {len(to_process)} workflows on pod {pod.id}")
        for req in to_process:
            try:
                await self._execute_workflow_on_pod(req, pod)
            except Exception as e:
                print(f"❌ Failed to execute workflow {req.id} on pod {pod.id}: {e}")
                req.status = "failed"
                req.error = str(e)

    async def _execute_workflow_on_pod(self, workflow_request: WorkflowRequest, pod: ActivePod) -> None:
        """Execute a workflow on a specific pod"""
        print(f"\n🎬 ===== EXECUTING WORKFLOW ON POD =====")
        print(f"📋 Workflow ID: {workflow_request.id}")
        print(f"📋 Workflow Type: {workflow_request.workflow_type.value}")
        print(f"🖥️ Pod ID: {pod.id}")
        print(f"📝 Inputs: {workflow_request.inputs}")

        try:
            # Get pod connection info
            pod_manager = self._get_pod_manager()
            connection_info = await pod_manager.get_pod_connection_info(pod.id)

            print(f"🔍 Connection info for pod {pod.id}: {connection_info}")

            if not connection_info.get("success"):
                print(f"❌ Failed to get pod connection info: {connection_info.get('error')}")
                workflow_request.status = "failed"
                workflow_request.error = f"Pod connection failed: {connection_info.get('error')}"
                return

            pod_info = connection_info.get("podInfo", {})
            print(f"🔍 Pod info: {pod_info}")

            if not pod_info.get("ready"):
                print(f"❌ Pod {pod.id} is not ready (status: {pod_info.get('status')})")
                workflow_request.status = "failed"
                workflow_request.error = f"Pod is not ready (status: {pod_info.get('status')})"
                return

            # Handle different workflow types
            if workflow_request.workflow_type in [WorkflowType.LLM_LLM, WorkflowType.OLLAMA_LLM]:
                # Handleworkflow
                print(f"🤖 Executingworkflow on pod {pod.id}")

                # Importservice
                from api.services.ai.llm_service import LLMService

                # Createservice instance using proxy URL
                service = LLMService(
                    pod_ip="proxy", port=8188, pod_id=pod.id  # Use proxy URL format
                )

                health_status = await service.health_check()
                if not health_status.get("is_running", False):
                    print(f"⏳ LLM not ready on pod {pod.id}, waiting...")
                    for attempt in range(12):
                        await asyncio.sleep(10)
                        health_status = await service.health_check()
                        if health_status.get("is_running", False):
                            break
                        if attempt % 2 == 0:
                            print(f"⏳ LLM still starting... ({attempt + 1}/12)")

                    if not health_status.get("is_running", False):
                        print(f"❌ LLM failed to start on pod {pod.id}")
                        workflow_request.status = "failed"
                        workflow_request.error = "LLM failed to start on pod"
                        return

                # Extract parameters from inputs
                inputs = workflow_request.inputs
                prompt = inputs.get("prompt", "")
                model = inputs.get("model", "deepseek-r1:32b")
                stream = inputs.get("stream", False)
                max_tokens = inputs.get("max_tokens")
                temperature = inputs.get("temperature")
                context = inputs.get("context")

                print(f"🚀 Starting LLM generation on pod {pod.id}")
                result = await service.generate_response(
                    prompt=prompt,
                    model=model,
                    stream=stream,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    context=context,
                )
                

            else:
                # Handle ComfyUI workflows (existing logic)
                print(f"🎨 Executing ComfyUI workflow on pod {pod.id}")

                # Check if Port 8188 actually running on the pod
                print(f"🔍 Checking ComfyUI readiness on pod {pod.id}...")
                comfyui_ready = await self._check_port_8188_ready(pod.id, workflow_request.workflow_type.value)
                if not comfyui_ready:
                    print(f"❌ Port 8188 not ready on pod {pod.id}, waiting...")
                    # Wait for ComfyUI to be ready with retries
                    for attempt in range(12):  # Wait up to 2 minutes
                        await asyncio.sleep(10)
                        comfyui_ready = await self._check_port_8188_ready(pod.id, workflow_request.workflow_type.value)
                        if comfyui_ready:
                            print(f"✅ Port 8188 now ready on pod {pod.id}")
                            break
                        print(f"⏳ port 8188 not ready yet (attempt {attempt + 1}/12)")

                    if not comfyui_ready:
                        print(f"❌ ComfyUI failed to start on pod {pod.id} after 2 minutes")
                        workflow_request.status = "failed"
                        workflow_request.error = "ComfyUI failed to start on pod"
                        return

                # Get ComfyUI manager to generate workflow data
                # Import here to avoid circular dependency
                from api.services.ai.comfyui_service import get_comfyui_manager

                comfyui_manager = get_comfyui_manager()

                # Generate workflow data from inputs
                workflow_data, pattern, download_directory = await comfyui_manager.generate_workflow(
                    workflow_request.workflow_type, workflow_request.inputs
                )

                # Create a temporary service instance for this pod
                # Import here to avoid circular dependency
                from api.services.ai.comfyui_service import ComfyUIService

                service = ComfyUIService(pod_ip=pod_info.get("ip"), port=pod_info.get("port", 8188), pod_id=pod.id)

                # Execute the workflow
                print(f"🚀 Starting workflow execution on pod {pod.id}")
                print(f"🔍 ComfyUI URL: {service.base_url}")
                print(
                    f"🔍 Workflow data keys: {list(workflow_data.keys()) if isinstance(workflow_data, dict) else 'Not a dict'}"
                )

                result = await service.execute_workflow_data(workflow_data, pattern, download_directory)

            print(f"🔍 Workflow execution result: {result}")

            if result.get("success", False):
                print(f"✅ Workflow {workflow_request.id} completed successfully")
                workflow_request.status = "completed"
                
                # Set appropriate ID based on workflow type
                if workflow_request.workflow_type in [WorkflowType.LLM_LLM, WorkflowType.OLLAMA_LLM]:
                    # For LLM, create a proper WorkflowResult object
                    from api.schemas.ai.comfyui import WorkflowResult
                    workflow_request.result = WorkflowResult(
                        success=True,
                        request_id=workflow_request.id,
                        pod_id=workflow_request.pod_id,
                        pod_ip=workflow_request.pod_ip,
                        response_text=result.get("response", ""),
                        model=result.get("model", "qwen-omni"),
                        total_duration=result.get("total_duration", 0),
                        eval_count=result.get("eval_count", 0),
                    )
                    workflow_request.response_text = result.get("response", "")
                else:
                    # For ComfyUI workflows, set result as dictionary (existing behavior)
                    workflow_request.result = result
                    workflow_request.prompt_id = result.get("prompt_id")

                workflow_request.completed_at = datetime.fromtimestamp(time.time())
            else:
                print(f"❌ Workflow {workflow_request.id} failed: {result.get('error', 'Unknown error')}")
                workflow_request.status = "failed"
                workflow_request.error = result.get("error", "Unknown error")
                workflow_request.completed_at = datetime.fromtimestamp(time.time())

        except Exception as e:
            print(f"❌ Exception during workflow execution: {e}")
            workflow_request.status = "failed"
            workflow_request.error = str(e)
            workflow_request.completed_at = datetime.fromtimestamp(time.time())

    def _get_pod_manager(self):
        """Get pod manager instance"""
        from api.services.ai.runpod.runpod_manager import get_pod_manager

        return get_pod_manager()

    async def _check_port_8188_ready(self, pod_id: str, workflow_name: str = None) -> bool:
        """Check if Port 8188 actually running on the pod - workflow-specific"""
        try:
            import aiohttp

            base_url = f"https://{pod_id}-8188.proxy.runpod.net"

            async with aiohttp.ClientSession() as session:
                # Check if this is anworkflow (ollama, llm_llm)
                if workflow_name in ["ollama", "llm_llm"]:
                    # For workflows, check Ollama endpoints
                    endpoints_to_check = ["/api/tags", "/api/version", "/"]
                    print(f"🔍 Checkingendpoints on pod {pod_id}...")
                else:
                    # For ComfyUI workflows, check ComfyUI endpoints
                    endpoints_to_check = ["/system_stats", "/history", "/"]
                    print(f"🔍 Checking ComfyUI endpoints on pod {pod_id}...")

                for endpoint in endpoints_to_check:
                    try:
                        async with session.get(
                            f"{base_url}{endpoint}", timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                if workflow_name in ["ollama", "llm_llm"]:
                                    # For workflows, check model availability
                                    if endpoint == "/api/tags":
                                        try:
                                            data = await response.json()
                                            models = data.get("models", [])
                                            model_names = [model.get("name", "") for model in models]
                                            print(f"🔍 Available models: {model_names}")
                                            
                                            # Check if the requested model is available
                                            # Get the default model from config
                                            workflow_config = self.workflow_configs.get(workflow_name, {})
                                            requested_model = workflow_config.get("defaultModel", "deepseek-r1:32b")
                                            if requested_model in model_names:
                                                print(f"✅ Port 8188 running on pod {pod_id} (LLM endpoint {endpoint} responding, model {requested_model} available)")
                                                return True
                                            else:
                                                print(f"❌({requested_model}) model not found. Available models: {model_names}")
                                                return False
                                        except Exception as e:
                                            print(f"⏳ Failed to parse models from /api/tags: {e}")
                                            return False
                                    else:
                                        # For otherendpoints, any 200 response is good
                                        print(f"✅ Port 8188 running on pod {pod_id} (LLM endpoint {endpoint} responding)")
                                        return True
                                else:
                                    # For ComfyUI workflows, check specific endpoints
                                    if endpoint == "/system_stats":
                                        data = await response.json()
                                        if "system" in data and "comfyui_version" in data.get("system", {}):
                                            print(
                                                f"✅ Port 8188 running on pod {pod_id} (version: {data['system'].get('comfyui_version')})"
                                            )
                                            return True
                                        else:
                                            print(f"⏳ port 8188 not ready on pod {pod_id} (invalid response format)")
                                            return False
                                    else:
                                        print(f"✅ Port 8188 running on pod {pod_id} (endpoint {endpoint} responding)")
                                        return True
                            else:
                                print(
                                    f"⏳ port 8188 not ready on pod {pod_id} (endpoint {endpoint} status: {response.status})"
                                )
                    except Exception as e:
                        print(f"⏳ ComfyUI check failed for pod {pod_id} (endpoint {endpoint}): {e}")
                        continue

                return False
        except Exception as e:
            print(f"⏳ ComfyUI check failed for pod {pod_id}: {e}")
            return False


# Global manager instance
_manager_instance: Optional[UnifiedQueueManager] = None


def get_queue_manager() -> UnifiedQueueManager:
    """Get the global queue manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = UnifiedQueueManager()
    return _manager_instance
