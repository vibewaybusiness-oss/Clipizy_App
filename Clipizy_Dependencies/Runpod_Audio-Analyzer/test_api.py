"""
Test script for Audio Analyzer API
"""

import requests
import json

API_URL = "http://localhost:8188"

def test_analyze():
    """Test the /analyze endpoint."""
    
    payload = {
        "project_uid": f"test_{int(__import__('time').time())}",
        "s3_url": "https://example.com/audio.wav",
        "llm_analysis": True,
        "llm_analysis_prompt": "Describe this audio in detail.",
        "segment_analysis": True,
        "segment_analysis_prompt": "Analyze the musical characteristics of this segment."
    }
    
    print("Sending request to /analyze...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=600
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_health():
    """Test the /health endpoint."""
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Health Check: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Audio Analyzer API")
    print("=" * 60)
    print()
    
    print("[1/2] Testing health endpoint...")
    test_health()
    print()
    
    print("[2/2] Testing analyze endpoint...")
    print("Note: This requires a valid S3 URL and configured Qwen model")
    print()
    test_analyze()

