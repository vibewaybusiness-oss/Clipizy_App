from __future__ import annotations

import asyncio
import random
import string
import time
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
import os
from dotenv import load_dotenv
import json
from pathlib import Path

from pydantic import BaseModel, Field

from api.schemas.ai.comfyui import WorkflowRequest, WorkflowType
from api.services.ai.runpod.errors import ErrorCode

# Load RunPod configuration for workflow settings
RUNPOD_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "runpod_config.json"
try:
    with open(RUNPOD_CONFIG_PATH, encoding="utf-8") as _f:
        RUNPOD_CONFIG: Dict[str, Any] = json.load(_f)
except Exception as _e:
    # Surface a minimal, safe default; callers should handle missing values using defaults
    RUNPOD_CONFIG = {"workflow": {}, "podSettings": {}}

# Attempt to load environment variables (including RUNPOD_API_KEY)
try:
    # Load from current working directory
    load_dotenv()
    # Also attempt to load from project root (walk up to find .env)
    current = Path(__file__).resolve()
    for parent in current.parents:
        env_path = parent / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=False)
            break
except Exception:
    pass

StatusReq = Literal["pending", "processing", "completed", "failed"]


class QueueStatus(BaseModel):
    activePods: List[Dict[str, Any]]
    pendingRequests: Dict[str, List[Dict[str, Any]]]
    isRunning: bool
    comfyuiRequests: Optional[Dict[str, int]] = None


class AddWorkflowBody(BaseModel):
    workflowName: str = Field(...)
    requestData: Any = Field(...)
    workflow_type: Optional[WorkflowType] = Field(None)


class MarkBody(BaseModel):
    result: Optional[Any] = None
    error: Optional[str] = None


class UnifiedQueueManager:
    def __init__(self) -> None:
        self.pendingRequests: Dict[str, List[WorkflowRequest]] = {}
        self.isRunning: bool = False
        self._lock = asyncio.Lock()
        self._requests_index: Dict[str, WorkflowRequest] = {}
        self.comfyui_requests: Dict[str, WorkflowRequest] = {}

    async def start(self) -> None:
        async with self._lock:
            if self.isRunning:
                return
            self.isRunning = True

    async def stop(self) -> None:
        async with self._lock:
            if not self.isRunning:
                return
            self.isRunning = False

    async def cleanup(self) -> None:
        async with self._lock:
            self.pendingRequests.clear()
            self._requests_index.clear()
            self.comfyui_requests.clear()

    async def add_workflow_request(
        self, workflow_name: str, request_data: Any, workflow_type: Optional[WorkflowType] = None
    ) -> str:
        workflow_key = workflow_name.lower()
        request_id = f"req_{int(time.time()*1000)}_" + "".join(
            random.choices(string.ascii_lowercase + string.digits, k=9)
        )
        req = WorkflowRequest(id=request_id, workflow_type=workflow_type, inputs=request_data, status="pending")
        async with self._lock:
            self.pendingRequests.setdefault(workflow_key, []).append(req)
            self._requests_index[request_id] = req
            if workflow_type is not None:
                self.comfyui_requests[request_id] = req
        return request_id

    def get_queue_status(self) -> QueueStatus:
        pending: Dict[str, List[Dict[str, Any]]] = {}
        for name, reqs in self.pendingRequests.items():
            pending[name] = [r.dict() for r in reqs if r.status == "pending"]

        comfyui_status = {
            "total": len(self.comfyui_requests),
            "active": len([r for r in self.comfyui_requests.values() if r.status in ("pending", "processing")]),
            "completed": len([r for r in self.comfyui_requests.values() if r.status in ("completed", "failed")]),
            "pending": len([r for r in self.comfyui_requests.values() if r.status == "pending"]),
        }

        return QueueStatus(activePods=[], pendingRequests=pending, isRunning=self.isRunning, comfyuiRequests=comfyui_status)

    async def dequeue_pending(self, workflow_name: str, limit: Optional[int] = None) -> List[WorkflowRequest]:
        workflow_key = workflow_name.lower()
        async with self._lock:
            all_requests = self.pendingRequests.get(workflow_key, [])
            pending = [r for r in all_requests if r.status == "pending"]
            to_take = pending if limit is None else pending[: max(0, limit)]
            if not to_take:
                return []
            remaining = [r for r in all_requests if r not in to_take]
            self.pendingRequests[workflow_key] = remaining
            for r in to_take:
                r.status = "processing"
        return to_take

    def get_request(self, request_id: str) -> Optional[WorkflowRequest]:
        return self._requests_index.get(request_id)

    def get_comfyui_request(self, request_id: str) -> Optional[WorkflowRequest]:
        return self.comfyui_requests.get(request_id)

    def mark_request_completed(self, request_id: str, result: Any = None) -> bool:
        req = self._requests_index.get(request_id)
        if not req:
            return False
        req.status = "completed"
        req.result = result
        req.completed_at = datetime.fromtimestamp(time.time())
        return True

    def mark_request_failed(self, request_id: str, error: Optional[str] = None) -> bool:
        req = self._requests_index.get(request_id)
        if not req:
            return False
        req.status = "failed"
        req.error = error
        req.completed_at = datetime.fromtimestamp(time.time())
        return True

    # --- compatibility helpers with legacy manager ---
    def get_all_comfyui_requests(self) -> List[WorkflowRequest]:
        return list(self.comfyui_requests.values())

    def get_active_comfyui_requests(self) -> List[WorkflowRequest]:
        return [r for r in self.comfyui_requests.values() if r.status in ("pending", "processing")]

    def get_completed_comfyui_requests(self) -> List[WorkflowRequest]:
        return [r for r in self.comfyui_requests.values() if r.status in ("completed", "failed")]

    def get_max_queue_size(self, workflow_name: str) -> int:
        if workflow_name in ("llm-mistral", "llm-qwen3-vl"):
            llm_ollama_cfg = RUNPOD_CONFIG.get("workflow", {}).get("llm-ollama", {})
            queue_cfg = llm_ollama_cfg.get(workflow_name, {})
            return int(queue_cfg.get("maxQueueSize", 3))
        wf_cfg = RUNPOD_CONFIG.get("workflow", {}).get(workflow_name, {})
        return int(wf_cfg.get("maxQueueSize", 3))


_manager_instance: Optional[UnifiedQueueManager] = None


def get_queue_manager() -> UnifiedQueueManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = UnifiedQueueManager()
    return _manager_instance


async def _get_active_pods_for_workflow(workflow_name: str) -> List[Dict[str, Any]]:
    """
    Query RunPod API for active pods matching the workflow.
    Returns list of pods that match the workflow by name pattern or template.
    """
    print(f"[runpod][signal] _get_active_pods_for_workflow called for '{workflow_name}'")
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print(f"[runpod][signal] No API key found, returning empty list")
        return []

    try:
        from api.services.ai.runpod.runpod_manager import PodManager
        
        print(f"[runpod][signal] Querying RunPod API for all pods...")
        manager_rest = PodManager(api_key)
        pods_response = await manager_rest.get_pods()
        await manager_rest.close()
        
        print(f"[runpod][signal] RunPod API response type: {type(pods_response)}")
        print(f"[runpod][signal] RunPod API response (first 500 chars): {str(pods_response)[:500]}")
        
        if isinstance(pods_response, list):
            all_pods = pods_response
        elif isinstance(pods_response, dict):
            all_pods = pods_response.get("pods", [])
            if not all_pods and "data" in pods_response:
                all_pods = pods_response.get("data", [])
        else:
            all_pods = []
        print(f"[runpod][signal] Found {len(all_pods)} total pods from RunPod API")
        
        if len(all_pods) > 0:
            print(f"[runpod][signal] Sample pod (first): {str(all_pods[0])[:200] if all_pods else 'N/A'}")
        
        if not all_pods:
            print(f"[runpod][signal] No pods found in response, returning empty list")
            return []

        if workflow_name in ("llm-mistral", "llm-qwen3-vl"):
            wf_settings = RUNPOD_CONFIG.get("workflow", {}).get("llm-ollama", {})
        else:
            wf_settings = RUNPOD_CONFIG.get("workflow", {}).get(workflow_name, {})
        template_id = wf_settings.get("template")
        
        active_pods = []
        name_prefix = f"{workflow_name}-auto-"
        
        print(f"[runpod][signal] Checking pods for workflow '{workflow_name}' (name_prefix='{name_prefix}', template_id='{template_id}')")
        
        for pod in all_pods:
            pod_name = pod.get("name", "")
            pod_template = pod.get("templateId")
            pod_status = pod.get("desiredStatus", "").upper()
            
            matches_name = pod_name.startswith(name_prefix)
            matches_template = template_id and pod_template == template_id
            
            if (matches_name or matches_template) and pod_status in ["RUNNING", "STARTING"]:
                print(f"[runpod][signal] Found active pod: {pod_name} (status: {pod_status}, template: {pod_template})")
                active_pods.append(pod)
            elif matches_name or matches_template:
                print(f"[runpod][signal] Found matching pod but not active: {pod_name} (status: {pod_status})")
        
        print(f"[runpod][signal] Total active pods for '{workflow_name}': {len(active_pods)}")
        return active_pods
    except Exception as e:
        import traceback
        print(f"[runpod][signal] Error querying active pods: {e}")
        print(f"[runpod][signal] Traceback: {traceback.format_exc()}")
        return []


# CENTRAL SIGNAL/HEALTH CHECK
async def compute_pod_signal(workflow_name: str) -> Dict[str, Any]:
    """
    Centralized logic to determine pod availability/scaling action for a workflow
    based on RUNPOD_CONFIG and current queue status.
    """
    if not workflow_name:
        raise ValueError("workflow_name is required")

    print("[runpod][signal] ▶ compute_pod_signal called")
    print(f"[runpod][signal] workflow_name: {workflow_name}")
    manager = get_queue_manager()
    await manager.start()

    if workflow_name in ("llm-mistral", "llm-qwen3-vl"):
        llm_ollama_cfg = RUNPOD_CONFIG.get("workflow", {}).get("llm-ollama", {})
        queue_cfg = llm_ollama_cfg.get(workflow_name, {})
        max_queue_size = int(queue_cfg.get("maxQueueSize", 3))
        max_pods = int(queue_cfg.get("maxConcurrentPods", 1))
    else:
        wf_cfg = RUNPOD_CONFIG.get("workflow", {}).get(workflow_name, {})
        max_queue_size = int(wf_cfg.get("maxQueueSize", 3))
        max_pods = int(wf_cfg.get("maxConcurrentPods", 1))
    print(f"[runpod][signal] config → maxQueueSize={max_queue_size}, maxConcurrentPods={max_pods}")

    status = manager.get_queue_status()
    pending_for_wf = status.pendingRequests.get(workflow_name.lower(), [])
    queue_size = len(pending_for_wf)
    
    active_pods_list = await _get_active_pods_for_workflow(workflow_name)
    active_pods_count = len(active_pods_list)
    print(f"[runpod][signal] queue_size={queue_size}, activePods={active_pods_count}")

    if queue_size < max_queue_size:
        if active_pods_count > 0:
            print(f"[runpod][signal] DECISION: available (below queue threshold, {active_pods_count} active pods exist)")
            return {
                "success": True,
                "message": "Pod available",
                "queue_size": queue_size,
                "maxQueueSize": max_queue_size,
                "maxConcurrentPods": max_pods,
                "action": "available",
            }
        elif max_pods > 0:
            print("[runpod][signal] DECISION: no active pods → attempt creation preemptively")
        else:
            print("[runpod][signal] DECISION: available (below queue threshold)")
            return {
                "success": True,
                "message": "Pod available",
                "queue_size": queue_size,
                "maxQueueSize": max_queue_size,
                "maxConcurrentPods": max_pods,
                "action": "available",
            }

    if max_pods > 0:
        if active_pods_count > 0:
            current_pod_count = active_pods_count
            if current_pod_count < max_pods:
                print(f"[runpod][signal] DECISION: {current_pod_count}/{max_pods} pods active, can create more")
            else:
                print(f"[runpod][signal] DECISION: max pods reached ({current_pod_count}/{max_pods}), no new pod needed")
                return {
                    "success": True,
                    "message": f"Max pods reached ({current_pod_count}/{max_pods})",
                    "queue_size": queue_size,
                    "maxQueueSize": max_queue_size,
                    "maxConcurrentPods": max_pods,
                    "action": "max_pods_reached",
                }
        # Try to actually recruit/start a pod using RunPod REST API if configured
        api_key = os.getenv("RUNPOD_API_KEY")
        print(f"[runpod][signal] scale allowed; has_api_key={bool(api_key)}")
        try:
            if api_key:
                from api.services.ai.runpod.runpod_manager import PodManager
                from api.schemas.ai.runpod import RestPodConfig

                pod_settings = RUNPOD_CONFIG.get("podSettings", {})
                if workflow_name in ("llm-mistral", "llm-qwen3-vl"):
                    wf_settings = RUNPOD_CONFIG.get("workflow", {}).get("llm-ollama", {}) or RUNPOD_CONFIG.get("workflow", {}).get("default", {})
                else:
                    wf_settings = RUNPOD_CONFIG.get("workflow", {}).get(workflow_name, {}) or RUNPOD_CONFIG.get("workflow", {}).get("default", {})
                # Normalize pod settings keys to what RestPodConfig expects
                # Priority: workflow-specific docker_image > default_docker_image
                default_image = (
                    wf_settings.get("docker_image")
                    or pod_settings.get("defaultImage")
                    or pod_settings.get("default_docker_image")
                )
                print(f"[runpod][signal] docker_image (priority: workflow > default): {default_image}")
                default_disk_gb = (
                    pod_settings.get("defaultDiskInGb")
                    or pod_settings.get("default_container_disk_size")
                    or 20
                )
                default_gpu_count = pod_settings.get("defaultGpuCount", 1)
                default_mem_gb = (
                    pod_settings.get("defaultMemoryInGb")
                    or pod_settings.get("default_memory_in_gb")
                )
                default_country = (
                    pod_settings.get("defaultCountryCode")
                    or pod_settings.get("default_region")
                )
                default_vcpu = (
                    pod_settings.get("defaultVcpuCount")
                    or pod_settings.get("vcpuCount")
                    or 4
                )
                default_ports = pod_settings.get("defaultPorts") or pod_settings.get("default_ports")
                template_id = wf_settings.get("template")
                print(f"[runpod][signal] template_id={template_id}, network-volume={wf_settings.get('network-volume')}")
                print(f"[runpod][signal] pod_settings summary: gpu={pod_settings.get('defaultGpuCount')}, mem={pod_settings.get('defaultMemoryInGb')}GB, disk={pod_settings.get('defaultDiskInGb')}GB, ports={pod_settings.get('defaultPorts')}")

                manager_rest = PodManager(api_key)

                # Best-effort config using templateId, optionally gpuTypeIds from config
                raw_gpu_ids = wf_settings.get("gpuTypeIds")
                gpu_type_ids: Optional[List[str]] = None
                if isinstance(raw_gpu_ids, list):
                    if raw_gpu_ids and isinstance(raw_gpu_ids[0], dict):
                        gpu_type_ids = [str(item.get("id")) for item in raw_gpu_ids if item.get("id")]
                    else:
                        gpu_type_ids = [str(x) for x in raw_gpu_ids]

                ports = ["8188/http"]
                if default_ports:
                    if isinstance(default_ports, str):
                        ports = [default_ports]
                    elif isinstance(default_ports, list):
                        ports = [str(p) for p in default_ports if p]

                network_volume_id = wf_settings.get("network-volume") or pod_settings.get("networkVolumeId")
                volume_mount_path = pod_settings.get("defaultVolumeMountPath") or pod_settings.get("default_volume_mount_path") or "/workspace"

                pod_config = RestPodConfig(
                    gpuTypeIds=gpu_type_ids,
                    imageName=default_image,
                    name=f"{workflow_name}-auto-{int(time.time())}",
                    env={
                        "PYTHONUNBUFFERED": "1",
                        "JUPYTER_PASSWORD": "secure-password-123",
                        "OLLAMA_HOST": "0.0.0.0:8188",
                    },
                    containerDiskInGb=int(default_disk_gb),
                    volumeInGb=None if network_volume_id else int(default_disk_gb),
                    volumeMountPath=volume_mount_path,
                    networkVolumeId=network_volume_id,
                    gpuCount=int(default_gpu_count),
                    minMemoryInGb=int(default_mem_gb) if default_mem_gb is not None else None,
                    supportPublicIp=pod_settings.get("supportPublicIp", True),
                    ports=ports,
                    templateId=template_id,
                )

                current_pod_count = len(await _get_active_pods_for_workflow(workflow_name))
                
                if current_pod_count >= max_pods:
                    print(f"[runpod][signal] DECISION: max pods already reached ({current_pod_count}/{max_pods}), skipping creation")
                    await manager_rest.close()
                    return {
                        "success": True,
                        "message": f"Max pods already reached ({current_pod_count}/{max_pods})",
                        "queue_size": queue_size,
                        "maxQueueSize": max_queue_size,
                        "maxConcurrentPods": max_pods,
                        "action": "max_pods_reached",
                    }

                try:
                    print(f"[runpod][signal] ▶ creating pod via RunPod REST... (current: {current_pod_count}/{max_pods})")
                    resp = await manager_rest.create_pod(pod_config)
                    print(f"[runpod][signal] create_pod response: {resp}")
                    await manager_rest.close()
                    action = "created"
                    message = "Pod creation requested"
                except Exception as _e:
                    print(f"[runpod][signal] create_pod failed: {_e}")
                    await manager_rest.close()
                    action = "created"
                    message = f"Pod create attempted: {_e}"

                return {
                    "success": True,
                    "message": message,
                    "queue_size": queue_size,
                    "maxQueueSize": max_queue_size,
                    "maxConcurrentPods": max_pods,
                    "action": action,
                    "runpodResponse": locals().get("resp")
                }
        except Exception as _:
            print(f"[runpod][signal] scale attempt failed, falling back to capacity reached path")
            # Fall through to capacity reached if creation fails
            pass

        print("[runpod][signal] DECISION: created (no API configured; simulated scale)")
        return {
            "success": True,
            "message": "Scale up possible but no API configured",
            "queue_size": queue_size,
            "maxQueueSize": max_queue_size,
            "maxConcurrentPods": max_pods,
            "action": "created",
        }

    print("[runpod][signal] DECISION: max_pods_reached (at capacity)")
    return {
        "success": False,
        "message": f"All pods at capacity. Queue size: {queue_size}/{max_queue_size}",
        "action": "max_pods_reached",
    }
