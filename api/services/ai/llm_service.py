import os
import base64
import logging
from typing import Any, Dict, Optional, List

import httpx

logger = logging.getLogger(__name__)


async def debug_image_to_base64(image_url: str) -> Dict[str, Any]:
    """
    DEBUG FUNCTION: CONVERT IMAGE URL TO BASE64
    Downloads image from URL and converts to base64, with detailed logging
    Returns diagnostic information about the conversion process
    """
    logger.info("=" * 80)
    logger.info("DEBUG: Starting image to base64 conversion")
    logger.info(f"Image URL: {image_url[:200]}...")
    
    try:
        logger.info("Step 1: Downloading image from URL...")
        async with httpx.AsyncClient(timeout=30.0) as img_client:
            img_resp = await img_client.get(image_url)
            img_resp.raise_for_status()
            
            logger.info(f"Step 2: Image downloaded - Status: {img_resp.status_code}")
            logger.info(f"Step 3: Content-Type: {img_resp.headers.get('content-type', 'unknown')}")
            
            image_bytes = img_resp.content
            logger.info(f"Step 4: Image size: {len(image_bytes)} bytes")
            
            logger.info("Step 5: Encoding to base64...")
            image_base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
            
            logger.info(f"Step 6: Base64 length: {len(image_base64_encoded)} characters")
            logger.info(f"Step 7: Base64 preview (first 100 chars): {image_base64_encoded[:100]}...")
            logger.info(f"Step 8: Base64 preview (last 100 chars): ...{image_base64_encoded[-100:]}")
            
            result = {
                "success": True,
                "image_url": image_url,
                "image_bytes_size": len(image_bytes),
                "base64_length": len(image_base64_encoded),
                "base64_preview_start": image_base64_encoded[:100],
                "base64_preview_end": image_base64_encoded[-100:],
                "content_type": img_resp.headers.get("content-type", "unknown"),
            }
            
            logger.info("=" * 80)
            logger.info("DEBUG: Image to base64 conversion completed successfully")
            logger.info("=" * 80)
            
            return result
            
    except httpx.HTTPStatusError as e:
        logger.error(f"DEBUG: HTTP error downloading image: {e.response.status_code}")
        logger.error(f"DEBUG: Response text: {e.response.text[:500]}")
        raise
    except Exception as e:
        logger.error(f"DEBUG: Failed to convert image to base64: {e}")
        logger.error(f"DEBUG: Exception type: {type(e).__name__}")
        raise


def _get_runpod_base_url(pod_id: str) -> str:
    """
    GET RUNPOD BASE URL FROM POD ID
    Requires pod_id - NO FALLBACKS. Pod ID must come from queue system.
    """
    if not pod_id:
        raise ValueError("pod_id is required. Cannot use fallback pod ID. Pod must be obtained from queue system.")
    return f"https://{pod_id}-8188.proxy.runpod.net"


async def _download_image_bytes(image_url: str) -> bytes:
    """
    DOWNLOAD IMAGE BYTES FROM URL
    Helper function to download image data
    """
    async with httpx.AsyncClient(timeout=30.0) as img_client:
        img_resp = await img_client.get(image_url)
        img_resp.raise_for_status()
        return img_resp.content


async def check_runpod_pod_health(pod_id: Optional[str] = None, base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    CHECK RUNPOD POD HEALTH AND AVAILABILITY
    Returns information about pod connectivity and available endpoints
    
    Args:
        pod_id: Pod ID from queue system (required if base_url not provided)
        base_url: Direct URL to check (optional, overrides pod_id)
    """
    if base_url is None:
        if not pod_id:
            return {
                "base_url": None,
                "accessible": False,
                "available_endpoints": [],
                "error": "No pod_id provided. Pod must be obtained from queue system."
            }
        base_url = _get_runpod_base_url(pod_id)
    
    health_info = {
        "base_url": base_url,
        "accessible": False,
        "available_endpoints": [],
        "root_response": None,
        "errors": []
    }
    
    health_endpoints = ["/", "/health", "/api/health", "/status", "/api/version", "/api/tags"]
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in health_endpoints:
            try:
                resp = await client.get(f"{base_url}{endpoint}")
                if resp.status_code < 500:
                    health_info["accessible"] = True
                    health_info["available_endpoints"].append(f"{endpoint} ({resp.status_code})")
                    if endpoint == "/":
                        try:
                            health_info["root_response"] = resp.text[:500]
                        except:
                            health_info["root_response"] = f"Status: {resp.status_code}"
            except Exception as e:
                health_info["errors"].append(f"{endpoint}: {str(e)}")
    
    return health_info


async def generate_prompt(
    prompt: str,
    *,
    image_file_path: Optional[str] = None,
    image_base64: Optional[str] = None,
    image_url: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    pod_id: Optional[str] = None,
    timeout_seconds: int = 300,
) -> str:
    """
    GENERATE PROMPT USING LLM SERVICE
    
    Args:
        prompt: The prompt text
        image_file_path: Optional path to image file
        image_base64: Optional base64-encoded image
        image_url: Optional URL to image (will be downloaded and converted to base64)
        model: Optional model name (defaults to qwen3-vl for images)
        base_url: Optional direct base URL (overrides pod_id)
        pod_id: Pod ID from queue system (REQUIRED if base_url not provided - NO FALLBACKS)
        timeout_seconds: Request timeout
    
    Raises:
        ValueError: If pod_id is not provided and base_url is not provided
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt is required")

    if base_url is None:
        if not pod_id:
            raise ValueError(
                "pod_id is required. Cannot use fallback pod ID. "
                "Pod ID must be obtained from queue system via get_active_pod_for_workflow(). "
                "If calling directly, you must pass a valid pod_id parameter."
            )
        base_url = _get_runpod_base_url(pod_id)

    # Quick connectivity check
    try:
        async with httpx.AsyncClient(timeout=5.0) as test_client:
            test_resp = await test_client.get(f"{base_url}/", follow_redirects=True)
            if test_resp.status_code >= 500:
                logger.warning(f"Pod at {base_url} returned {test_resp.status_code}, but continuing anyway")
    except httpx.RequestError as e:
        raise Exception(
            f"Cannot connect to RunPod pod at {base_url}. "
            f"Error: {str(e)}. "
            f"Please verify:\n"
            f"1. The pod is running in RunPod console\n"
            f"2. The pod ID is correct: {pod_id or 'NOT PROVIDED - Pod must come from queue system'}\n"
            f"3. Port 8188 is exposed and the service is running"
        )

    images_payload: Optional[list[str]] = None
    if image_url:
        try:
            # Download and encode image with debug logging
            logger.info("=" * 80)
            logger.info("DEBUG: Converting image URL to base64 for LLM request")
            logger.info(f"Image URL: {image_url[:200]}...")
            
            logger.info("Step 1: Downloading image from URL...")
            image_bytes = await _download_image_bytes(image_url)
            logger.info(f"Step 2: Image downloaded - {len(image_bytes)} bytes")
            
            logger.info("Step 3: Encoding to base64...")
            image_base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
            logger.info(f"Step 4: Base64 encoded - {len(image_base64_encoded)} characters")
            logger.info(f"Step 5: Base64 preview (first 100 chars): {image_base64_encoded[:100]}...")
            logger.info("=" * 80)
            
            images_payload = [image_base64_encoded]
            logger.info(f"Image ready for LLM request (base64: {len(image_base64_encoded)} chars)")
        except Exception as e:
            logger.error(f"Failed to download/encode image from URL {image_url}: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to download image from URL: {str(e)}")
    elif image_base64:
        images_payload = [image_base64]
    elif image_file_path:
        with open(image_file_path, "rb") as f:
            images_payload = [base64.b64encode(f.read()).decode("utf-8")]

    chosen_model = model or ("qwen3-vl" if images_payload else "qwen3-vl")

    payload: Dict[str, Any] = {
        "model": chosen_model,
        "prompt": prompt,
    }
    if images_payload:
        payload["images"] = images_payload
        logger.info(f"Sending request to {base_url}/api/generate with model={chosen_model}, prompt_length={len(prompt)}, has_image=True")
    else:
        logger.info(f"Sending request to {base_url}/api/generate with model={chosen_model}, prompt_length={len(prompt)}, has_image=False")

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        result = None
        endpoints_to_try = ["/api/generate", "/api/chat", "/v1/chat/completions", "/chat/completions"]
        last_error = None
        
        for endpoint in endpoints_to_try:
            try:
                full_url = f"{base_url}{endpoint}"
                logger.info(f"Trying endpoint: {full_url}")
                resp = await client.post(full_url, json=payload)
                
                if resp.status_code == 404:
                    logger.warning(f"Endpoint {endpoint} returned 404, trying next endpoint...")
                    last_error = f"HTTP 404: Endpoint {endpoint} not found"
                    continue
                
                resp.raise_for_status()
                result = resp.json()
                logger.info(f"Successfully received response from {endpoint}")
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404 and endpoint != endpoints_to_try[-1]:
                    last_error = f"HTTP 404: Endpoint {endpoint} not found"
                    continue
                error_detail = f"HTTP {e.response.status_code}"
                try:
                    error_body = e.response.json()
                    if isinstance(error_body, dict):
                        if "error" in error_body:
                            error_detail += f": {error_body['error']}"
                        elif "message" in error_body:
                            error_detail += f": {error_body['message']}"
                        elif "detail" in error_body:
                            error_detail += f": {error_body['detail']}"
                except:
                    error_text = e.response.text[:200] if e.response.text else "No error details"
                    error_detail += f": {error_text}"
                raise Exception(f"LLM API request failed - {error_detail}")
            except httpx.RequestError as e:
                raise Exception(f"LLM API connection error: {str(e)}. Cannot reach RunPod pod at {base_url}. Please verify the pod is running.")
        
        if result is None:
            health_info = await check_runpod_pod_health(base_url)
            error_msg = (
                f"All endpoints failed. Last error: {last_error}.\n"
                f"RunPod pod: {base_url}\n"
                f"Pod accessible: {health_info['accessible']}\n"
                f"Available endpoints: {', '.join(health_info['available_endpoints']) if health_info['available_endpoints'] else 'None'}\n"
                f"Tried endpoints: {', '.join(endpoints_to_try)}\n"
            )
            if health_info.get("root_response"):
                error_msg += f"Root response preview: {health_info['root_response']}\n"
            error_msg += "\n"
            
            if not health_info["accessible"]:
                error_msg += (
                    f"Cannot reach the RunPod pod. Please verify:\n"
                    f"1. The pod is running in RunPod console (https://www.runpod.io/console/pods)\n"
                    f"2. The pod ID is correct: {pod_id or 'NOT PROVIDED - Pod must come from queue system'}\n"
                    f"3. Port 8188 is exposed in the pod configuration\n"
                    f"4. The LLM service (Ollama/qwen3-vl) is started and listening on port 8188\n"
                )
            else:
                error_msg += (
                    f"The pod is accessible but the LLM service endpoints are not found.\n\n"
                    f"Troubleshooting steps:\n"
                    f"1. Check if Ollama is running: curl {base_url}/api/tags\n"
                    f"2. Try manually: curl {base_url}/api/generate -d '{{\"model\":\"qwen3-vl\",\"prompt\":\"test\"}}'\n"
                    f"3. Verify the service has started (wait 2-5 minutes after pod creation)\n"
                    f"4. Check RunPod pod logs to see if the service started correctly\n"
                    f"5. Ensure Ollama is configured to listen on 0.0.0.0:8188\n"
                    f"6. Verify the model 'qwen3-vl' is available in Ollama\n\n"
                    f"If using a custom LLM service, verify it implements the /api/generate endpoint.\n"
                )
            raise Exception(error_msg)

    if isinstance(result, dict):
        if "response" in result and isinstance(result["response"], str):
            return result["response"]
        if "text" in result and isinstance(result["text"], str):
            return result["text"]
        if "message" in result and isinstance(result["message"], str):
            return result["message"]
        choices = result.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0] or {}
            msg = first.get("message") if isinstance(first, dict) else None
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"]
    raise Exception("No text response returned from model")