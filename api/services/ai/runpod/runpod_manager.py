from typing import Any, Dict, List, Optional

import httpx

from api.schemas.ai.runpod import RestPodConfig


class PodManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rest_url = "https://rest.runpod.io/v1"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=30.0,
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def _request(self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Any:
        try:
            response = await self.client.request(method, f"{self.rest_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json() if response.content else {}
        except httpx.HTTPStatusError as e:
            # Include response text to aid debugging (e.g., 400 error details)
            detail = None
            try:
                detail = e.response.json()
            except Exception:
                try:
                    detail = e.response.text
                except Exception:
                    detail = None
            raise httpx.HTTPStatusError(
                f"{str(e)} | body={detail}", request=e.request, response=e.response
            )

    async def get_pods(self) -> Any:
        return await self._request("/pods")

    async def get_pod_by_id(self, pod_id: str) -> Any:
        return await self._request(f"/pods/{pod_id}")

    async def create_pod(self, pod_config: RestPodConfig) -> Any:
        config_dict = pod_config.model_dump(by_alias=True, exclude_none=True)
        return await self._request("/pods", method="POST", data=config_dict)

    async def update_pod(self, pod_id: str, update_data: Dict[str, Any]) -> Any:
        return await self._request(f"/pods/{pod_id}", method="PATCH", data=update_data)

    async def start_pod(self, pod_id: str) -> Any:
        return await self._request(f"/pods/{pod_id}/start", method="POST")

    async def stop_pod(self, pod_id: str) -> Any:
        return await self._request(f"/pods/{pod_id}/stop", method="POST")

    async def restart_pod(self, pod_id: str) -> Any:
        return await self._request(f"/pods/{pod_id}/restart", method="POST")

    async def terminate_pod(self, pod_id: str) -> Any:
        return await self._request(f"/pods/{pod_id}", method="DELETE")

    async def get_network_volumes(self) -> Any:
        return await self._request("/networkvolumes")

    async def get_network_volume_by_id(self, volume_id: str) -> Any:
        return await self._request(f"/networkvolumes/{volume_id}")

    async def expose_http_ports(self, pod_id: str, ports: List[int]) -> Any:
        return await self._request(f"/pods/{pod_id}", method="PATCH", data={"exposeHttpPorts": ports})


