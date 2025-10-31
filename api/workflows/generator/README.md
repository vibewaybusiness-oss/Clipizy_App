# Unified Visualizer System

A comprehensive audio visualizer system for the clipizy API backend, providing multiple visualization styles for music videos.

## Features

- **Multiple Visualizer Types**: Linear bars, dots, waveforms, bass circles, and trap nation styles
- **FastAPI Integration**: RESTful API endcredits for creating visualizers
- **Configurable Parameters**: Extensive customization options for all visualizer types
- **Background Processing**: Asynchronous job processing with status tracking
- **High Performance**: Optimized for real-time audio processing

## Visualizer Types

### 1. Linear Bars (`linear_bars`)
Classic frequency bar visualization with customizable height, thickness, and positioning.

### 2. Linear Dots (`linear_dots`)
Dot-based visualization with high-quality anti-aliased rendering.

### 3. Waveform (`waveform`)
Smooth waveform visualization with fill areas and smooth curves.

### 4. Bass Circle (`bass_circle`)
Circular visualization with dots positioned around a center point.

### 5. Trap Nation (`trap_nation`)
Radial bar visualization extending from center outward.

## API Endcredits

### Get Available Visualizers
```
GET /api/visualizers/types
```
Returns available visualizer types and configuration schema.

### Create Visualizer (Simple)
```
POST /api/visualizers/create
```
Create a visualizer with form parameters.

**Parameters:**
- `audio_file`: Audio file upload
- `visualizer_type`: Type of visualizer (linear_bars, linear_dots, etc.)
- `width`, `height`: Video dimensions (default: 1920x1080)
- `fps`: Frames per second (default: 30)
- `color`: RGB color as "R,G,B" string (default: "255,50,100")
- And many more customization options...

### Create Visualizer (Advanced)
```
POST /api/visualizers/create-from-request
```
Create a visualizer with detailed JSON request body.

### Get Job Status
```
GET /api/visualizers/status/{job_id}
```
Check the status of a visualizer job.

### Download Result
```
GET /api/visualizers/download/{job_id}
```
Download the completed visualizer video.

### List Jobs
```
GET /api/visualizers/jobs
```
List all visualizer jobs.

### Delete Job
```
DELETE /api/visualizers/job/{job_id}
```
Delete a visualizer job and its output file.

## Configuration Options

### Basic Settings
- `width`, `height`: Video resolution
- `fps`: Frames per second
- `n_segments`: Number of frequency segments
- `fadein`, `fadeout`: Fade durations in seconds
- `duration_intro`: Skip intro duration
- `time_in`: Time offset before visualizer appears

### Visual Settings
- `height_percent`, `width_percent`: Visualizer size as percentage of screen
- `x_position`, `y_position`: Position as percentage of screen
- `color`: RGB color tuple
- `transparency`: Whether opacity depends on audio values
- `smoothness`: Smoothness level (0-100)

### Bar/Dot Settings
- `bar_thickness`: Thickness of bars
- `bar_count`: Number of bars to display
- `bar_height_min`, `bar_height_max`: Height limits as percentage
- `mirror_right`: Mirror bars to the right side
- `dot_size`: Size of dots in pixels
- `dot_filled`: Whether to draw filled dots

### Waveform Settings
- `fill_alpha`: Alpha value for filled areas
- `border_alpha`: Alpha value for borders
- `smooth_arcs`: Whether to use smooth curves
- `top_active`, `bottom_active`: Which parts to draw

### Enhanced Mode
- `enhanced_mode.active`: Enable enhanced mode
- `enhanced_mode.threshold`: Minimum value to trigger enhancement
- `enhanced_mode.factor`: Enhancement factor multiplier

## Usage Examples

### Python API Usage
```python
from unified_visualizers import UnifiedVisualizerService, VisualizerConfig, VisualizerType

# Initialize service
service = UnifiedVisualizerService()

# Create configuration
config = VisualizerConfig(
    visualizer_type=VisualizerType.LINEAR_BARS,
    width=1920,
    height=1080,
    fps=30,
    n_segments=60,
    bar_thickness=3,
    mirror_right=True,
    color=(255, 50, 100),
    enhanced_mode={"active": True, "threshold": 0.3, "factor": 2.0}
)

# Render visualizer
output_path = service.render_visualizer(
    audio_path="input.wav",
    output_path="output.mp4",
    config=config
)
```

### HTTP API Usage
```bash
# Create a linear bars visualizer
curl -X POST "http://localhost:8000/api/visualizers/create" \
  -F "audio_file=@music.wav" \
  -F "visualizer_type=linear_bars" \
  -F "width=1920" \
  -F "height=1080" \
  -F "color=255,50,100" \
  -F "mirror_right=true"

# Check job status
curl "http://localhost:8000/api/visualizers/status/{job_id}"

# Download result
curl "http://localhost:8000/api/visualizers/download/{job_id}" -o output.mp4
```

## Dependencies

- OpenCV (`cv2`)
- PyTorch (`torch`)
- Librosa (`librosa`)
- Pydub (`AudioSegment`)
- MoviePy (`VideoFileClip`, `AudioFileClip`)
- FastAPI
- NumPy

## File Structure

```
api/processing/music/generator/
├── unified_visualizers.py      # Main visualizer system
├── example_usage.py            # Usage examples
├── README.md                   # This documentation
└── visualizers/                # Individual visualizer files
    ├── visualizer.py
    ├── bassCircle.py
    └── trapNationBassVisualizer*.py
```

## Performance Notes

- The system uses background processing to avoid blocking the API
- Jobs are tracked in memory (use Redis for production)
- Temporary files are cleaned up automatically
- Audio processing is optimized with configurable smoothness levels
- FFT processing uses PyTorch for better performance

## Error Handling

- Invalid visualizer types return 400 Bad Request
- Missing audio files return 400 Bad Request
- Job not found returns 404 Not Found
- Processing errors are tracked in job status
- All errors include descriptive messages

## Future Enhancements

- Database integration for job persistence
- Redis for distributed job tracking
- More visualizer types
- Real-time preview
- Batch processing
- Custom visualizer plugins
