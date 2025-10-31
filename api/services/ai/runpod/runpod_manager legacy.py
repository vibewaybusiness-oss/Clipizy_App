# runpod_manager.py
# RunPod Pod Management Service with Integrated API Client
# ----------------------------------------------------------

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import httpx
except ImportError:
    httpx = None
    print("Warning: httpx not available. Install with: pip install httpx")

try:
    import aiohttp
except ImportError:
    aiohttp = None
    print("Warning: aiohttp not available. Install with: pip install aiohttp")

from api.schemas.ai.comfyui import ActivePod, WorkflowRequest
from api.schemas.ai.runpod import (
    CloudType,
    GpuType,
    NetworkVolume,
    RestPodConfig,
    RunPodApiResponse,
    RunPodPod,
    RunPodUser,
)

# GPU Priority List (A40 -> 4090 -> 5090 as requested)
GPU_PRIORITY_LIST: List[str] = [
    "NVIDIA A40",
]

# Load configuration
CWD = Path(os.getcwd())
# Handle both cases: running from root or from api directory
RUNPOD_CONFIG_PATH = CWD / "api" / "config" / "json" / "runpod_config.json"

with RUNPOD_CONFIG_PATH.open("r", encoding="utf-8") as f:
    RUNPOD_CONFIG: Dict[str, Any] = json.load(f)
    
class PodManager:
    """Enhanced RunPod Pod Manager with integrated API client"""

    def __init__(self, api_key: Optional[str] = None):
        if httpx is None:
            raise ImportError("httpx is required but not installed. Install with: pip install httpx")

        self.api_key = api_key or self._get_api_key()
        self.graphql_url = "https://api.runpod.io/graphql"
        self.rest_url = "https://rest.runpod.io/v1"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, timeout=30.0
        )
        self.active_pods: Dict[str, ActivePod] = {}
        self._load_config()

    def _get_api_key(self) -> str:
        """Get API key from environment or file"""
        api_key = os.getenv("RUNPOD_API_KEY")
        if api_key:
            return api_key

        # Try different possible key file locations and names
        possible_files = [
            os.path.join(os.path.dirname(__file__), "..", "runpod", "runpod_api_privatekey"),
            os.path.join(os.path.dirname(__file__), "..", "runpod", "runpod_api_key"),
            os.path.join(os.path.dirname(__file__), "..", "runpod", "api_key"),
            "runpod_api_key",
            "runpod_api_privatekey",
        ]

        for key_file in possible_files:
            if os.path.exists(key_file):
                with open(key_file, "r") as f:
                    content = f.read().strip()
                    # Check if it's an SSH key (starts with -----BEGIN)
                    if content.startswith("-----BEGIN"):
                        print(f"⚠️ Found SSH key at {key_file}, but need RunPod API key")
                        continue
                    # Check if it looks like a RunPod API key (alphanumeric, reasonable length)
                    if len(content) > 20 and content.replace("-", "").replace("_", "").isalnum():
                        return content

        raise ValueError(
            "RunPod API key not found. Please:\n"
            "1. Set RUNPOD_API_KEY environment variable, or\n"
            "2. Create a file with your RunPod API key in one of these locations:\n"
            "   - api/runpod/runpod_api_privatekey\n"
            "   - api/runpod/runpod_api_key\n"
            "   - api/runpod/api_key\n"
            "   - runpod_api_key (in project root)\n"
            "   - runpod_api_privatekey (in project root)\n"
            "\n"
            "Get your API key from: https://runpod.io/console/user/settings"
        )

    def _load_config(self):
        """Load configuration from all config files"""
        # Pod settings from RunPod config
        ps = RUNPOD_CONFIG.get("podSettings", {})
        self.default_image = ps.get("defaultImage")
        self.default_gpu = ps.get("defaultGpuCount", 1)
        self.default_mem_gb = ps.get("defaultMemoryInGb", 8)
        self.default_vcpu = ps.get("defaultVcpuCount", 4)
        self.default_disk_gb = ps.get("defaultDiskInGb", 20)
        self.support_public_ip = bool(ps.get("supportPublicIp", True))
        self.default_ports = ps.get("defaultPorts", [])

        # Workflow settings from ComfyUI config
        self.workflow_configs = RUNPOD_CONFIG.get("workflow", {})
        self.default_config = RUNPOD_CONFIG.get("defaults", {})

    def get_workflow_config(self, workflow_name: str) -> Dict[str, Any]:
        """Get configuration for a specific workflow"""
        return self.workflow_configs.get(workflow_name, self.default_config)

    def get_max_queue_size(self, workflow_name: str) -> int:
        """Get maximum queue size for a workflow"""
        config = self.get_workflow_config(workflow_name)
        return config.get("maxQueueSize", self.default_config.get("maxQueueSize", 3))

    def get_workflow_timeouts(self, workflow_name: str) -> Tuple[int, int]:
        """Get pause and terminate timeouts for a workflow"""
        # Check ComfyUI config first
        comfyui_config = self.get_workflow_config(workflow_name)
        if "timeouts" in comfyui_config:
            to = comfyui_config.get("timeouts", {})
            return int(to.get("pause", 60)), int(to.get("terminate", 300))

        # Fallback to RunPod config
        wf = RUNPOD_CONFIG.get("workflow", {})
        wfc = wf.get(workflow_name, wf.get("default", {}))
        to = wfc.get("timeouts", {})
        return int(to.get("pause", 60)), int(to.get("terminate", 300))

    def get_workflow_network_volume(self, workflow_name: str) -> Optional[str]:
        """Get network volume for a workflow"""
        # Check ComfyUI config first
        comfyui_config = self.get_workflow_config(workflow_name)
        if "network-volume" in comfyui_config:
            return comfyui_config.get("network-volume")

        # Fallback to RunPod config
        wf = RUNPOD_CONFIG.get("workflow", {})
        wfc = wf.get(workflow_name, wf.get("default", {}))
        return wfc.get("network-volume")

    def get_workflow_template(self, workflow_name: str) -> Optional[str]:
        """Get the template ID for a specific workflow"""
        comfyui_config = self.get_workflow_config(workflow_name)
        
        if "template" in comfyui_config:
            return comfyui_config.get("template")

        wf = RUNPOD_CONFIG.get("workflow", {})
        wfc = wf.get(workflow_name, wf.get("default", {}))
        return wfc.get("template")

    def _get_ports_config(self) -> List[str]:
        """Get ports configuration - only include essential ComfyUI port 8188"""
        # Only include ComfyUI port 8188 for faster pod readiness
        return ["8188/http"]

    async def check_network_volume_availability(self) -> bool:
        """Check if network volume is available"""
        try:
            result = await self.get_network_volumes()
            return bool(result.success and result.data)
        except Exception:
            return False

    # ============================================================================
    # API CLIENT METHODS (MERGED FROM runpod_client.py)
    # ============================================================================

    async def _gql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> RunPodApiResponse:
        """Make a GraphQL request"""
        try:
            request_payload = {"query": query, "variables": variables or {}}

            response = await self.client.post(self.graphql_url, json=request_payload)

            response.raise_for_status()
            result = response.json()

            if result.get("errors") and len(result["errors"]) > 0:
                return RunPodApiResponse(
                    success=False, error=", ".join([e.get("message", "Unknown error") for e in result["errors"]])
                )

            return RunPodApiResponse(success=True, data=result.get("data"))

        except httpx.HTTPError as e:
            return RunPodApiResponse(success=False, error=f"HTTP error: {str(e)}")
        except Exception as e:
            return RunPodApiResponse(success=False, error=f"Request failed: {str(e)}")

    async def make_request(
        self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None
    ) -> RunPodApiResponse:
        """Make a REST API request"""
        try:
            response = await self.client.request(
                method,
                f"{self.rest_url}{endpoint}",
                json=data,
            )

            if response.status_code >= 400:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                print(f"❌ RunPod API error: {error_msg}")
                return RunPodApiResponse(success=False, error=error_msg)

            text = response.text or ""
            if not text:
                return RunPodApiResponse(success=True, data={})

            try:
                json_data = response.json()
                return RunPodApiResponse(success=True, data=json_data)
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse JSON: {str(e)[:100]}"
                print(f"❌ JSON decode error: {error_msg}")
                return RunPodApiResponse(success=False, error=error_msg)
        except Exception as e:
            error_msg = str(e)[:200]
            print(f"❌ Request exception: {error_msg}")
            return RunPodApiResponse(success=False, error=error_msg)

    async def get_account_info(self) -> RunPodApiResponse[RunPodUser]:
        """Get account information using GraphQL"""
        query = """
        query {
            myself {
                id
                email
                minBalance
            }
        }
        """
        result = await self._gql(query)
        if result.success and result.data:
            user_data = result.data["myself"]
            return RunPodApiResponse(
                success=True,
                data=RunPodUser(
                    id=user_data["id"], email=user_data.get("email"), min_balance=user_data.get("minBalance", 0.0)
                ),
            )
        return result

    async def get_pods(self) -> RunPodApiResponse[List[RunPodPod]]:
        """Get all pods"""
        result = await self.make_request("/pods")
        return result

    async def get_pod_by_id(self, pod_id: str) -> RunPodApiResponse[RunPodPod]:
        """Get pod by ID"""
        result = await self.make_request(f"/pods/{pod_id}")

        if result and result.success and result.data:
            raw = result.data
            pod = RunPodPod(
                id=raw.get("id"),
                name=raw.get("name"),
                image_name=raw.get("imageName"),
                uptime_seconds=raw.get("uptimeSeconds") or 0,
                cost_per_hr=raw.get("costPerHr") or 0.0,
                created_at=raw.get("createdAt"),
                status=raw.get("desiredStatus") or raw.get("status"),
                desired_status=raw.get("desiredStatus"),
                ip=raw.get("ip"),
                public_ip=raw.get("publicIp"),
                machine_id=raw.get("machineId"),
                gpu_count=raw.get("gpuCount"),
                memory_in_gb=raw.get("memoryInGb"),
                vcpu_count=raw.get("vcpuCount"),
                last_started_at=raw.get("lastStartedAt"),
                port_mappings=raw.get("portMappings"),
                ports=raw.get("ports"),
                network_volume_id=raw.get("networkVolumeId"),
                volume_in_gb=raw.get("volumeInGb"),
                volume_mount_path=raw.get("volumeMountPath"),
            )
            return RunPodApiResponse(success=True, data=pod)
        return result

    async def create_pod(self, pod_config: RestPodConfig) -> RunPodApiResponse[RunPodPod]:
        """Create a new pod using REST API"""
        # Convert to camelCase for RunPod API
        config_dict = pod_config.model_dump(by_alias=True, exclude_none=True)
        print(f"🔧 DEBUG: Sending config_dict to API: {config_dict}")
        return await self.make_request("/pods", "POST", config_dict)

    async def stop_pod(self, pod_id: str) -> RunPodApiResponse[Dict[str, bool]]:
        """Stop a pod"""
        result = await self.make_request(f"/pods/{pod_id}/stop", "POST")
        return result

    async def start_pod(self, pod_id: str) -> RunPodApiResponse[Dict[str, bool]]:
        """Start a pod"""
        result = await self.make_request(f"/pods/{pod_id}/start", "POST")
        return result

    async def restart_pod(self, pod_id: str) -> RunPodApiResponse[Dict[str, bool]]:
        """Restart a pod"""
        result = await self.make_request(f"/pods/{pod_id}/restart", "POST")
        return result

    async def update_pod(self, pod_id: str, update_data: Dict[str, Any]) -> RunPodApiResponse[RunPodPod]:
        """Update a pod"""
        result = await self.make_request(f"/pods/{pod_id}", "PATCH", update_data)
        return result

    async def pause_pod(self, pod_id: str) -> RunPodApiResponse[Dict[str, bool]]:
        """Pause a pod (same as stop)"""
        return await self.stop_pod(pod_id)

    async def terminate_pod(self, pod_id: str) -> RunPodApiResponse[Dict[str, bool]]:
        """Terminate a pod"""
        result = await self.make_request(f"/pods/{pod_id}", "DELETE")
        return result

    async def get_network_volumes(self) -> RunPodApiResponse[List[NetworkVolume]]:
        """Get network volumes"""
        result = await self.make_request("/networkvolumes")
        return result

    async def get_network_volume_by_id(self, volume_id: str) -> RunPodApiResponse[NetworkVolume]:
        """Get network volume by ID"""
        result = await self.make_request(f"/networkvolumes/{volume_id}")
        return result

    async def get_templates(
        self, include_public: bool = False, include_runpod: bool = False, include_endpoint_bound: bool = False
    ) -> RunPodApiResponse[List[Dict[str, Any]]]:
        """Get templates"""
        params = []
        if include_public:
            params.append("includePublicTemplates=true")
        if include_runpod:
            params.append("includeRunpodTemplates=true")
        if include_endpoint_bound:
            params.append("includeEndpointBoundTemplates=true")

        query_string = "&".join(params)
        endpoint = f"/templates?{query_string}" if query_string else "/templates"

        result = await self.make_request(endpoint)
        return result

    async def get_gpu_types(self) -> RunPodApiResponse[List[Dict[str, Any]]]:
        """Get available GPU types"""
        # Mock implementation - RunPod REST API doesn't have this endpoint
        return RunPodApiResponse(
            success=True,
            data=[
                {"id": "NVIDIA A40", "memoryInGb": 48}
            ],
        )

    async def expose_http_ports(self, pod_id: str, ports: List[int]) -> RunPodApiResponse[Dict[str, Any]]:
        """Expose HTTP ports on a pod"""
        return await self.make_request(f"/pods/{pod_id}", "PATCH", {"exposeHttpPorts": ports})

    async def recruit_pod(self, config: RestPodConfig) -> Dict[str, Any]:
        """Recruit a pod with the given configuration"""
        try:
            result = await self.create_pod(config)
            if result.success and result.data:
                return {
                    "success": True,
                    "pod": result.data,
                    "gpuType": config.gpu_type_ids[0] if config.gpu_type_ids else None,
                }
            return {"success": False, "error": result.error or "Failed to create pod"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_pod_for_workflow(self, workflow_name: str) -> Optional[ActivePod]:
        """Create a new pod for a workflow using GPU priority list"""
        print(f"\n🚀 ===== POD RECRUITMENT STARTED =====")
        print(f"📋 Workflow: {workflow_name}")

        # Get workflow-specific template
        template_id = self.get_workflow_template(workflow_name)
        if template_id:
            print(f"🎯 Template ID: {template_id}")
        else:
            print(f"⚠️ No template configured for workflow {workflow_name}, using default settings")

        # Get network volume information
        network_volume_id = self.get_workflow_network_volume(workflow_name)
        if network_volume_id:
            print(f"💾 Network Volume ID: {network_volume_id}")
        else:
            print(f"⚠️ No network volume configured for workflow {workflow_name}")

        # Check network volume availability
        print(f"🔍 Checking network volume availability...")
        volume_available = await self.check_network_volume_availability()
        print(f"📊 Network volume available: {volume_available}")

        # Get timeout settings
        pause_s, term_s = self.get_workflow_timeouts(workflow_name)
        print(f"⏰ Timeouts - Pause: {pause_s}s, Terminate: {term_s}s")

        print(f"📋 GPU Priority List: {' > '.join(GPU_PRIORITY_LIST)}")

        # Try each GPU type in priority order
        for gpu_type in GPU_PRIORITY_LIST:
            print(f"\n🔄 ===== TRYING GPU: {gpu_type} =====")

            # Create pod recruitment config with current GPU type - using old working approach
            pod_config = RestPodConfig(
                gpu_type_ids=[gpu_type],
                image_name="runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
                name=f"{workflow_name}-pod-{int(time.time()*1000)}",
                container_disk_in_gb=20,
                gpu_count=1,
                support_public_ip=True,
                ports=self._get_ports_config(),  # Use proper port configuration
                network_volume_id=network_volume_id,
                template_id=template_id,
                env={
                    "JUPYTER_PASSWORD": "secure-password-123",
                    "OLLAMA_HOST": "0.0.0.0:8188",
                    "RUNPOD_POD_ID": "will-be-set-by-runpod",
                },
                # Additional fields from old working approach
                cloud_type="SECURE",
                compute_type="GPU",
                vcpu_count=4,
                data_center_priority="availability",
                gpu_type_priority="availability",
                cpu_flavor_priority="availability",
                min_ram_per_gpu=8,
                min_vcpu_per_gpu=2,
                interruptible=False,
                locked=False,
                global_networking=True,
                # Volume configuration
                volume_in_gb=0 if network_volume_id else 20,
                volume_mount_path="/workspace",
            )

            # Log complete pod configuration
            print(f"📝 Pod Configuration:")
            config_dict = pod_config.model_dump(by_alias=True)
            for key, value in config_dict.items():
                print(f"   {key}: {value}")

            # Use recruit_pod method to create the pod
            print(f"🚀 Sending pod creation request to RunPod...")
            result = await self.recruit_pod(pod_config)

            print(f"📊 RunPod Response:")
            print(f"   Success: {result['success']}")
            print(f"   Data: {result.get('pod')}")
            print(f"   Error: {result.get('error')}")

            if result["success"] and result.get("pod"):
                now = int(time.time() * 1000)
                pod_data = result["pod"]

                # Ensure ComfyUI port 8188 is exposed before waiting for readiness
                print(f"🔧 Ensuring ComfyUI port 8188 is exposed...")
                try:
                    await self.expose_comfyui_port(pod_data["id"])
                    print(f"✅ ComfyUI port 8188 exposed successfully")
                except Exception as e:
                    print(f"⚠️ Failed to expose ComfyUI port 8188: {e}")

                # Wait for pod to be ready with ComfyUI port 8188
                print(f"⏳ Waiting for pod {pod_data['id']} to be ready with ComfyUI port 8188...")
                wait_result = await self.wait_for_pod_ready(pod_data["id"])

                if wait_result.get("success"):
                    print(f"✅ Pod {pod_data['id']} is ready with ComfyUI port 8188")
                    active = ActivePod(
                        id=pod_data["id"],
                        workflow_name=workflow_name,
                        created_at=now,
                        last_used_at=now,
                        pause_timeout_at=now + pause_s * 1000,
                        terminate_timeout_at=now + term_s * 1000,
                        status="running",
                    )
                    self.active_pods[active.id] = active
                    print(f"✅ ===== POD CREATED SUCCESSFULLY =====")
                    print(f"   Pod ID: {active.id}")
                    print(f"   Workflow: {workflow_name}")
                    print(f"   GPU Type: {gpu_type}")
                    print(f"   Template: {template_id}")
                    print(f"   Network Volume: {network_volume_id}")
                    print(f"   Status: {active.status}")
                    print(f"   Created At: {active.created_at}")
                    print(f"   Pause Timeout: {active.pause_timeout_at}")
                    print(f"   Terminate Timeout: {active.terminate_timeout_at}")

                    return active
                else:
                    print(f"❌ Pod {pod_data['id']} created but not ready: {wait_result.get('error')}")
                    # Terminate the pod since it's not ready
                    try:
                        await self.release_pod(pod_data["id"])
                    except Exception as e:
                        print(f"⚠️ Failed to terminate unready pod: {e}")
                    continue
            else:
                print(f"❌ Pod creation failed with {gpu_type}")
                if result.get("error"):
                    print(f"   Error details: {result['error']}")
                # Continue to next GPU type
                continue

        print(f"❌ ===== POD RECRUITMENT FAILED =====")
        print(f"   Failed to create pod with any GPU type from priority list")
        print(f"   Tried GPUs: {', '.join(GPU_PRIORITY_LIST)}")
        return None

    async def get_pod_connection_info(self, pod_id: str) -> Dict[str, Any]:
        """Get pod connection information"""
        try:
            result = await self.get_pod_by_id(pod_id)
            if result.success and result.data:
                pod_data = result.data
                # Check both status and desired_status for readiness
                actual_status = pod_data.desired_status or pod_data.status
                is_ready = actual_status == "RUNNING"

                return {
                    "success": True,
                    "podInfo": {
                        "ip": pod_data.public_ip or pod_data.ip,
                        "port": 8188,  # Default ComfyUI port
                        "status": actual_status,
                        "ready": is_ready,
                    },
                }
            return {"success": False, "error": "Pod not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def wait_for_pod_ready(self, pod_id: str, max_attempts: int = 30) -> Dict[str, Any]:
        """Wait for pod to be ready with IP and ComfyUI port 8188, and verify port 8188 actually running"""
        print(f"⏳ Waiting for pod {pod_id} to be ready with ComfyUI port 8188...")

        # First phase: Wait for pod to be running with port configured
        for attempt in range(1, max_attempts + 1):
            try:
                pod_status = await self.get_pod_by_id(pod_id)
                if pod_status and pod_status.success and pod_status.data:
                    pod = pod_status.data
                    status = pod.desired_status or pod.status

                    # readiness checks - only check for ComfyUI port 8188
                    # Check if port 8188 is configured in the ports array (RunPod proxy system)
                    has_comfyui_port = bool(pod.ports and "8188/http" in pod.ports)
                    # For RunPod proxy system, we don't need a traditional public IP
                    # The proxy URL works as long as the port is configured
                    has_public_ip = has_comfyui_port  # If port is configured, proxy is available

                    print(
                        f"📊 Pod status (attempt {attempt}/{max_attempts}): {status} (IP: {'Yes' if has_public_ip else 'No'}, ComfyUI Port 8188: {'Yes' if has_comfyui_port else 'No'})"
                    )

                    if status == "RUNNING":
                        # Only check for ComfyUI port 8188 - no uptime requirement
                        if has_public_ip and has_comfyui_port:
                            print(f"✅ Pod {pod_id} is ready with ComfyUI port 8188")

                            # Second phase: Wait for ComfyUI to actually be running
                            print(f"🔍 Verifying port 8188 actually running on pod {pod_id}...")
                            comfyui_ready = await self._wait_for_comfyui_ready(pod_id, max_attempts=20)

                            if comfyui_ready:
                                return {
                                    "success": True,
                                    "finalStatus": status,
                                    "podInfo": {
                                        "id": pod_id,
                                        "ip": pod.public_ip or pod.ip or "",
                                        "port": 8188,  # ComfyUI port
                                        "status": status or "",
                                        "ready": True,
                                    },
                                }
                            else:
                                print(f"⏳ port 8188 not ready on pod {pod_id}, continuing to wait...")
                        else:
                            reason = "Pod is running but not ready:"
                            if not has_public_ip:
                                reason += " no public IP"
                            if not has_comfyui_port:
                                reason += " ComfyUI port 8188 not available via proxy"
                            print(f"⏳ {reason}")
                    elif status in {"FAILED", "TERMINATED", "EXITED"}:
                        return {
                            "success": False,
                            "error": f"Pod failed to start - status: {status}",
                            "finalStatus": status,
                        }
                    elif status in {"STOPPED", "PAUSED"}:
                        print(f"⏸️ Pod is {status}, waiting for it to start...")
                else:
                    error_msg = pod_status.error if pod_status else "No response from API"
                    print(f"❌ Failed to get pod status (attempt {attempt}): {error_msg}")
                await asyncio.sleep(5)  # Wait 5 seconds between attempts
            except Exception as e:
                print(f"❌ Error checking pod status (attempt {attempt}): {e}")
                await asyncio.sleep(5)

        return {
            "success": False,
            "error": f"Pod did not become ready with ComfyUI port 8188 within {max_attempts * 5} seconds",
            "finalStatus": "TIMEOUT",
        }

    async def _wait_for_comfyui_ready(self, pod_id: str, max_attempts: int = 20) -> bool:
        """Wait for ComfyUI to actually be running and responding"""
        print(f"⏳ Waiting for ComfyUI to be ready on pod {pod_id}...")

        for attempt in range(1, max_attempts + 1):
            try:
                comfyui_ready = await self._check_port_8188_ready(pod_id)
                if comfyui_ready:
                    print(f"✅ port 8188 now ready on pod {pod_id}")
                    return True
                else:
                    print(f"⏳ port 8188 not ready yet (attempt {attempt}/{max_attempts})")
                    await asyncio.sleep(10)  # Wait 10 seconds between ComfyUI checks
            except Exception as e:
                print(f"❌ Error checking ComfyUI readiness (attempt {attempt}): {e}")
                await asyncio.sleep(10)

        print(f"❌ ComfyUI did not become ready on pod {pod_id} within {max_attempts * 10} seconds")
        return False

    async def _check_port_8188_ready(self, pod_id: str) -> bool:
        """Check if port 8188 actually running on the pod"""
        try:
            if aiohttp is None:
                print(f"⚠️ aiohttp not available, skipping ComfyUI check for pod {pod_id}")
                return False

            comfyui_url = f"https://{pod_id}-8188.proxy.runpod.net"

            async with aiohttp.ClientSession() as session:
                # Try multiple endpoints to ensure port 8188 fully ready
                endpoints_to_check = ["/system_stats", "/history", "/"]

                for endpoint in endpoints_to_check:
                    try:
                        async with session.get(
                            f"{comfyui_url}{endpoint}", timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                if endpoint == "/system_stats":
                                    data = await response.json()
                                    if "system" in data and "comfyui_version" in data.get("system", {}):
                                        print(
                                            f"✅ port 8188 running on pod {pod_id} (version: {data['system'].get('comfyui_version')})"
                                        )
                                        return True
                                    else:
                                        print(f"⏳ port 8188 not ready on pod {pod_id} (invalid response format)")
                                        return False
                                else:
                                    print(f"✅ port 8188 running on pod {pod_id} (endpoint {endpoint} responding)")
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

    async def pause_pod(self, pod_id: str) -> Dict[str, Any]:
        """Pause a pod"""
        try:
            result = await self.stop_pod(pod_id)
            if result.success:
                # Update local pod status
                if pod_id in self.active_pods:
                    self.active_pods[pod_id].status = "paused"
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def resume_pod(self, pod_id: str) -> Dict[str, Any]:
        """Resume a pod"""
        try:
            result = await self.start_pod(pod_id)
            if result.success:
                # Update local pod status
                if pod_id in self.active_pods:
                    self.active_pods[pod_id].status = "running"
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def release_pod(self, pod_id: str) -> Dict[str, Any]:
        """Release/terminate a pod"""
        try:
            result = await self.terminate_pod(pod_id)
            if result.success:
                # Remove from local tracking
                self.active_pods.pop(pod_id, None)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_pod_public_ip(self, pod_id: str) -> Dict[str, Any]:
        """Get pod public IP"""
        return await self.get_pod_connection_info(pod_id)

    async def expose_comfyui_port(self, pod_id: str) -> None:
        """Expose ComfyUI port (8188) on a pod - only ensure port 8188 is available"""
        try:
            result = await self.get_pod_by_id(pod_id)
            if not result or not result.success or not result.data:
                raise RuntimeError("Failed to get pod configuration")

            current_ports = result.data.port_mappings or {}
            ports_array: List[str] = []

            # Keep existing ports
            for port in current_ports.keys():
                if port == "22":
                    ports_array.append("22/tcp")
                elif port == "8080":
                    ports_array.append("8080/http")
                elif port == "8888":
                    ports_array.append("8888/http")
                elif port == "8188":
                    ports_array.append("8188/http")
                else:
                    ports_array.append(f"{port}/tcp")

            # Only ensure ComfyUI port 8188 is present
            if "8188/http" not in ports_array:
                ports_array.append("8188/http")

            update_result = await self.update_pod(pod_id, {"ports": ports_array})
            if not update_result.success:
                raise RuntimeError("Failed to update pod configuration")
            print(f"✅ ComfyUI port 8188 ensured on pod {pod_id}")
        except Exception as e:
            print(f"❌ Failed to expose ComfyUI port on pod {pod_id}: {e}")
            raise

    def get_active_pods(self) -> Dict[str, ActivePod]:
        """Get all active pods"""
        return self.active_pods

    def get_active_pod_by_id(self, pod_id: str) -> Optional[ActivePod]:
        """Get a specific active pod by ID"""
        return self.active_pods.get(pod_id)

    def find_paused_pod(self, workflow_name: str) -> Optional[ActivePod]:
        """Find a paused pod for a workflow"""
        for pod in self.active_pods.values():
            if pod.workflow_name == workflow_name and pod.status == "paused":
                return pod
        return None

    async def find_available_pod(self, workflow_name: str) -> Optional[ActivePod]:
        """Find an available pod for a workflow. Prioritizes restarting paused pods over creating new ones."""
        paused_pod = self.find_paused_pod(workflow_name)
        if paused_pod:
            print(f"🔄 Found paused pod {paused_pod.id} for {workflow_name}, verifying status and restarting...")
            try:
                pod_status_result = await self.get_pod_by_id(paused_pod.id)
                if pod_status_result.success and pod_status_result.data:
                    actual_status = pod_status_result.data.desired_status or pod_status_result.data.status
                    if actual_status in {"STOPPED", "PAUSED"}:
                        print(f"✅ Confirmed pod {paused_pod.id} is paused ({actual_status}), restarting...")
                        result = await self.resume_pod(paused_pod.id)
                        if result.get("success"):
                            print(f"✅ Successfully restarted paused pod {paused_pod.id}")
                            paused_pod.status = "starting"
                            await asyncio.sleep(2)
                            wait_result = await self.wait_for_pod_ready(paused_pod.id)
                            if wait_result.get("success"):
                                paused_pod.status = "running"
                                paused_pod.paused_at = None
                                print(f"✅ Paused pod {paused_pod.id} is now running and ready")
                                if len(paused_pod.request_queue) < self.get_max_queue_size(workflow_name):
                                    return paused_pod
                            else:
                                print(f"⚠️ Paused pod {paused_pod.id} restarted but not ready: {wait_result.get('error')}")
                                paused_pod.status = "paused"
                        else:
                            print(f"❌ Failed to restart paused pod {paused_pod.id}: {result.get('error')}")
                    elif actual_status == "RUNNING":
                        print(f"ℹ️ Pod {paused_pod.id} is already running, updating local status")
                        paused_pod.status = "running"
                        paused_pod.paused_at = None
                        if len(paused_pod.request_queue) < self.get_max_queue_size(workflow_name):
                            return paused_pod
                    else:
                        print(f"⚠️ Pod {paused_pod.id} has unexpected status: {actual_status}")
                else:
                    print(f"⚠️ Could not verify pod {paused_pod.id} status from API, attempting restart anyway")
                    result = await self.resume_pod(paused_pod.id)
                    if result.get("success"):
                        paused_pod.status = "starting"
                        await asyncio.sleep(2)
                        wait_result = await self.wait_for_pod_ready(paused_pod.id)
                        if wait_result.get("success"):
                            paused_pod.status = "running"
                            paused_pod.paused_at = None
                            if len(paused_pod.request_queue) < self.get_max_queue_size(workflow_name):
                                return paused_pod
            except Exception as e:
                print(f"❌ Error restarting paused pod {paused_pod.id}: {e}")
        
        for pod in self.active_pods.values():
            if (
                pod.workflow_name == workflow_name
                and pod.status == "running"
                and len(pod.request_queue) < self.get_max_queue_size(workflow_name)
            ):
                return pod
        return None

    def get_workflow_pod_count(self, workflow_name: str) -> int:
        """Get the number of active pods for a specific workflow"""
        return sum(1 for pod in self.active_pods.values() if pod.workflow_name == workflow_name)

    def get_max_pods_per_workflow(self, workflow_name: str) -> int:
        """Get the maximum number of pods allowed per workflow"""
        # Check ComfyUI config first, then RunPod config
        comfyui_config = self.get_workflow_config(workflow_name)
        if "maxPods" in comfyui_config:
            return int(comfyui_config.get("maxPods", 1))

        # Fallback to RunPod config
        wf = RUNPOD_CONFIG.get("workflow", {})
        wfc = wf.get(workflow_name, wf.get("default", {}))
        return int(wfc.get("maxPods", 1))

    async def check_pod_timeouts(self) -> None:
        """Check and handle pod timeouts"""
        now = int(time.time() * 1000)
        for pod_id, pod in list(self.active_pods.items()):
            if pod.status == "running" and len(pod.request_queue) == 0 and now > pod.pause_timeout_at:
                # pause
                pod.status = "paused"
                pod.paused_at = now
                try:
                    await self.pause_pod(pod_id)
                except Exception:
                    pass
            elif pod.status == "paused" and pod.paused_at and now > pod.terminate_timeout_at:
                # terminate
                pod.status = "terminated"
                try:
                    await self.release_pod(pod_id)
                except Exception:
                    pass
                self.active_pods.pop(pod_id, None)

    async def close(self):
        """Close the pod manager and clean up resources"""
        # Terminate all active pods
        for pod_id in list(self.active_pods.keys()):
            try:
                await self.release_pod(pod_id)
            except Exception:
                pass
        self.active_pods.clear()
        await self.client.aclose()


# Singleton instance
_pod_manager_instance: Optional[PodManager] = None


def get_pod_manager() -> PodManager:
    """Get the singleton pod manager instance"""
    global _pod_manager_instance
    if _pod_manager_instance is None:
        _pod_manager_instance = PodManager()
    return _pod_manager_instance
