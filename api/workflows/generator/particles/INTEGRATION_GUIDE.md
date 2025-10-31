# FastAPI Integration Guide

This guide shows how to integrate the Unified Particle System into your FastAPI application.

## Quick Integration

### 1. Add Router to Main App

In your main FastAPI application file (e.g., `api/main.py`):

```python
from fastapi import FastAPI
from routers.particle_router import router as particle_router

app = FastAPI(title="clipizy API", version="1.0.0")

# Include particle router
app.include_router(particle_router)

# Your existing routes...
```

### 2. Install Dependencies

Add to your `requirements.txt`:

```
numpy>=1.21.0
opencv-python>=4.5.0
librosa>=0.9.0
fastapi>=0.68.0
pydantic>=1.8.0
```

### 3. Create Storage Directories

```bash
mkdir -p api/storage/renders
mkdir -p api/storage/previews
```

## API Usage Examples

### Create a Particle System

```bash
curl -X POST "http://localhost:8000/particles/create" \
  -H "Content-Type: application/json" \
  -d '{
    "particle_type": "snow",
    "config": {
      "width": 1280,
      "height": 720,
      "fps": 30,
      "duration": 10.0,
      "particle_count": 100,
      "bass_threshold": 0.3
    }
  }'
```

### List Available Particle Types

```bash
curl -X GET "http://localhost:8000/particles/types"
```

### Start Rendering

```bash
curl -X POST "http://localhost:8000/particles/systems/{system_id}/render" \
  -H "Content-Type: application/json" \
  -d '{
    "output_path": "my_visualization.mp4",
    "audio_path": "path/to/audio.wav"
  }'
```

### Check Render Status

```bash
curl -X GET "http://localhost:8000/particles/jobs/{job_id}"
```

### Download Rendered Video

```bash
curl -X GET "http://localhost:8000/particles/download/{job_id}" \
  --output "my_video.mp4"
```

## Python Client Example

```python
import requests
import time

# Base URL
BASE_URL = "http://localhost:8000/particles"

# Create particle system
response = requests.post(f"{BASE_URL}/create", json={
    "particle_type": "enhanced",
    "config": {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "duration": 15.0,
        "particle_count": 200,
        "particle_colors": [
            [255, 0, 0],    # Red
            [0, 255, 0],    # Green
            [0, 0, 255]     # Blue
        ],
        "enhanced_mode": {
            "active": True,
            "threshold": 0.3,
            "factor": 2.0
        }
    }
})

system_id = response.json()["system_id"]
print(f"Created system: {system_id}")

# Load audio
requests.post(f"{BASE_URL}/systems/{system_id}/load-audio", 
              params={"audio_path": "path/to/audio.wav"})

# Start rendering
render_response = requests.post(f"{BASE_URL}/systems/{system_id}/render", json={
    "output_path": "my_visualization.mp4",
    "audio_path": "path/to/audio.wav"
})

job_id = render_response.json()["job_id"]
print(f"Started rendering job: {job_id}")

# Wait for completion
while True:
    status_response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    status = status_response.json()
    
    print(f"Status: {status['status']} - Progress: {status['progress']}%")
    
    if status["status"] == "completed":
        print("Rendering completed!")
        break
    elif status["status"] == "failed":
        print(f"Rendering failed: {status.get('error', 'Unknown error')}")
        break
    
    time.sleep(2)

# Download the video
if status["status"] == "completed":
    download_response = requests.get(f"{BASE_URL}/download/{job_id}")
    with open("downloaded_video.mp4", "wb") as f:
        f.write(download_response.content)
    print("Video downloaded successfully!")
```

## WebSocket Integration (Optional)

For real-time particle system updates, you can add WebSocket support:

```python
from fastapi import WebSocket
import json

@app.websocket("/particles/ws/{system_id}")
async def websocket_endpoint(websocket: WebSocket, system_id: str):
    await websocket.accept()
    
    if system_id not in active_systems:
        await websocket.close(code=1008, reason="System not found")
        return
    
    system = active_systems[system_id]
    
    try:
        while True:
            # Send current status
            status = system.get_status()
            await websocket.send_text(json.dumps(status))
            
            # Wait for client message or timeout
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                # Handle client commands
                command = json.loads(data)
                if command.get("action") == "update_config":
                    system.update_config(command.get("config", {}))
            except asyncio.TimeoutError:
                pass  # Continue sending status
                
    except WebSocketDisconnect:
        print(f"Client disconnected from system {system_id}")
```

## Database Integration (Production)

For production use, replace the in-memory storage with a database:

```python
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ParticleSystem(Base):
    __tablename__ = "particle_systems"
    
    id = Column(String, primary_key=True)
    particle_type = Column(String, nullable=False)
    config = Column(JSON)
    created_at = Column(DateTime)
    status = Column(JSON)

class RenderJob(Base):
    __tablename__ = "render_jobs"
    
    id = Column(String, primary_key=True)
    system_id = Column(String, nullable=False)
    output_path = Column(String)
    status = Column(String)
    progress = Column(Integer, default=0)
    created_at = Column(DateTime)
    completed_at = Column(DateTime)
    error = Column(String)

# Database setup
engine = create_engine("sqlite:///particles.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid configuration or particle type
- **404 Not Found**: System or job not found
- **500 Internal Server Error**: Rendering or processing errors

Example error response:
```json
{
    "detail": "Invalid particle type: invalid_type. Available types: ['snow', 'zen', 'enhanced', 'bouncing', 'continuous_spawning', 'no_music']"
}
```

## Performance Considerations

1. **Memory Usage**: Each particle system uses memory proportional to particle count
2. **CPU Usage**: Rendering is CPU-intensive, consider background processing
3. **Storage**: Video files can be large, implement cleanup policies
4. **Concurrent Systems**: Limit the number of active systems based on server capacity

## Security Considerations

1. **File Path Validation**: Validate all file paths to prevent directory traversal
2. **Resource Limits**: Set limits on particle count, resolution, and duration
3. **Authentication**: Add authentication for production use
4. **Rate Limiting**: Implement rate limiting for API endcredits

## Monitoring

Add monitoring for:
- Active particle systems count
- Render job queue length
- Average render time
- Error rates
- Storage usage

Example monitoring endpoint:
```python
@app.get("/particles/metrics")
async def get_metrics():
    return {
        "active_systems": len(active_systems),
        "queued_jobs": len([j for j in render_jobs.values() if j["status"] == "queued"]),
        "rendering_jobs": len([j for j in render_jobs.values() if j["status"] == "rendering"]),
        "completed_jobs": len([j for j in render_jobs.values() if j["status"] == "completed"]),
        "failed_jobs": len([j for j in render_jobs.values() if j["status"] == "failed"])
    }
```

## Testing

Run the test suite:
```bash
cd api/processing/music/generator/particles
python test_unified_system.py
```

Run examples:
```bash
python example_usage.py
```

This integration guide provides everything needed to successfully integrate the Unified Particle System into your FastAPI application.
