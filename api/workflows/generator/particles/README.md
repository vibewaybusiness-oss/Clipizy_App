# Unified Particle System

A comprehensive particle system that combines all particle types into a single, FastAPI-ready solution for music visualization.

## Features

- **6 Different Particle Types**: Snow, Zen, Enhanced, Bouncing, Continuous Spawning, and No Music
- **Music Responsive**: Bass-triggered effects and audio synchronization
- **FastAPI Integration**: Ready-to-use API endcredits
- **Configurable**: Extensive configuration options for all particle behaviors
- **High Performance**: Optimized for real-time rendering
- **Audio Support**: Automatic audio loading and synchronization

## Particle Types

### 1. Snow Particles (`snow`)
- Snowflake particles with bass-triggered respawning
- Outward movement from center
- Distance-based fading effects
- Rotation and drift effects
- Perfect for atmospheric music visualization

### 2. Zen Particles (`zen`)
- Atmospheric particles with gentle drift
- Pulsing brightness effects
- Screen wrapping for continuous movement
- Calm, meditative visualization

### 3. Enhanced Particles (`enhanced`)
- Advanced particles with multiple features
- Color support with RGB values
- Size changes based on Z-velocity
- Enhanced mode for bass amplification
- Most versatile particle type

### 4. Bouncing Particles (`bouncing`)
- Particles that bounce off screen boundaries
- Physics-based boundary interactions
- Music-responsive movement patterns
- Great for energetic music

### 5. Continuous Spawning (`continuous_spawning`)
- Particles continuously spawn based on bass levels
- Steady spawn rate even without bass
- Particle age tracking and cleanup
- Maximum particle limits for performance
- Ideal for high-energy music

### 6. No Music Particles (`no_music`)
- Static particles without music dependency
- Screen wrapping behavior
- Basic movement patterns
- Perfect for background effects

## Quick Start

### Basic Usage

```python
from unified_particle_system import UnifiedParticleSystem, ParticleType, ParticleConfig

# Create a particle system
system = UnifiedParticleSystem(particle_type=ParticleType.ENHANCED)

# Render particles
system.render_particles("output.mp4", "audio.wav")
```

### Custom Configuration

```python
# Custom configuration
config = ParticleConfig(
    width=1920,
    height=1080,
    fps=30,
    duration=10.0,
    particle_count=200,
    bass_threshold=0.3,
    particle_colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
    enhanced_mode={
        "active": True,
        "threshold": 0.3,
        "factor": 2.0
    }
)

# Create system with custom config
system = UnifiedParticleSystem(particle_type=ParticleType.ENHANCED, config=config)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from routers.particle_router import router

app = FastAPI()
app.include_router(router)

# Available endcredits:
# POST /particles/create - Create particle system
# GET /particles/types - List particle types
# GET /particles/systems - List active systems
# PUT /particles/systems/{id}/config - Update configuration
# POST /particles/systems/{id}/render - Start rendering
# GET /particles/jobs/{id} - Check render status
```

## Configuration Options

### ParticleConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | int | 1920 | Video width |
| `height` | int | 1080 | Video height |
| `fps` | int | 30 | Frames per second |
| `x_position` | float | 0.5 | Center X position (0.0-1.0) |
| `y_position` | float | 0.5 | Center Y position (0.0-1.0) |
| `particle_count` | int | 200 | Number of particles |
| `duration` | float | 10.0 | Video duration in seconds |
| `bass_threshold` | float | 0.3 | Bass threshold for effects |
| `outer_movement_strength` | float | 2.0 | Outward movement strength |
| `inner_movement_strength` | float | 1.0 | Inward movement strength |
| `particle_colors` | List[Tuple] | [(255,255,255)] | RGB color list |
| `speed_x` | float | 0 | X velocity (0=random) |
| `speed_y` | float | 0 | Y velocity (0=random) |
| `speed_z` | float | 0 | Z velocity for size changes |
| `bounce` | bool | False | Bounce off screen edges |
| `steady_spawn_rate` | float | 0.5 | Particles per frame (continuous) |
| `max_particles` | int | 1000 | Maximum particles (continuous) |
| `enhanced_mode` | Dict | See below | Enhanced mode settings |
| `spawn_center_x` | float | 0.5 | Spawn center X (continuous) |
| `spawn_center_y` | float | 0.5 | Spawn center Y (continuous) |
| `spawn_area_width` | float | 0.0 | Spawn area width (continuous) |
| `spawn_area_height` | float | 0.0 | Spawn area height (continuous) |

### Enhanced Mode Settings

```python
enhanced_mode = {
    "active": True,        # Enable enhanced mode
    "threshold": 0.3,      # Bass threshold (0.0-1.0)
    "factor": 2.0          # Amplification factor
}
```

## API Endcredits

### Particle System Management

- `POST /particles/create` - Create new particle system
- `GET /particles/systems` - List all active systems
- `GET /particles/systems/{id}` - Get system status
- `PUT /particles/systems/{id}/config` - Update configuration
- `PUT /particles/systems/{id}/type/{type}` - Change particle type
- `DELETE /particles/systems/{id}` - Delete system

### Audio Management

- `POST /particles/systems/{id}/load-audio` - Load audio file

### Rendering

- `POST /particles/systems/{id}/render` - Start rendering job
- `GET /particles/jobs` - List render jobs
- `GET /particles/jobs/{id}` - Get job status
- `GET /particles/download/{id}` - Download rendered video
- `GET /particles/systems/{id}/preview` - Generate preview

### Information

- `GET /particles/types` - List available particle types
- `GET /particles/health` - Health check

## Examples

### Example 1: Snow Particles with Audio

```python
# Create snow particle system
config = ParticleConfig(
    width=1280,
    height=720,
    duration=15.0,
    particle_count=100,
    bass_threshold=0.2
)

system = UnifiedParticleSystem(particle_type=ParticleType.SNOW, config=config)
system.load_audio("music.wav")
system.render_particles("snow_visualization.mp4", "music.wav")
```

### Example 2: Colored Bouncing Particles

```python
# Create bouncing particles with colors
config = ParticleConfig(
    particle_colors=[
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
    ],
    bounce=True,
    speed_z=0.1  # Size changes
)

system = UnifiedParticleSystem(particle_type=ParticleType.BOUNCING, config=config)
system.render_particles("colored_bouncing.mp4")
```

### Example 3: Continuous Spawning

```python
# Create continuous spawning system
config = ParticleConfig(
    max_particles=500,
    steady_spawn_rate=1.0,
    spawn_area_width=0.1,
    spawn_area_height=0.1,
    enhanced_mode={
        "active": True,
        "threshold": 0.3,
        "factor": 1.5
    }
)

system = UnifiedParticleSystem(particle_type=ParticleType.CONTINUOUS_SPAWNING, config=config)
system.load_audio("electronic_music.wav")
system.render_particles("continuous_spawning.mp4", "electronic_music.wav")
```

## Performance Tips

1. **Particle Count**: Start with 50-100 particles and increase as needed
2. **Resolution**: Lower resolution (640x360) for faster rendering
3. **FPS**: Use 15-24 FPS for previews, 30+ for final output
4. **Duration**: Shorter durations for testing
5. **Continuous Spawning**: Set reasonable `max_particles` limits

## Dependencies

- `numpy` - Numerical computations
- `opencv-python` - Video rendering
- `librosa` - Audio processing
- `fastapi` - API framework (optional)
- `pydantic` - Data validation (optional)

## File Structure

```
particles/
├── unified_particle_system.py    # Main particle system class
├── example_usage.py              # Usage examples
├── README.md                     # This documentation
└── [original files]              # Original particle implementations
```

## Migration from Original Files

The unified system combines functionality from:
- `particlesTrapNationSnow.py` → Snow particles
- `ParticlesZen.py` → Zen particles  
- `particlesTrapNationEnhanced.py` → Enhanced particles
- `ParticlesBouncing.py` → Bouncing particles
- `particlesTrapNationNoMusic.py` → No music particles
- `particlesSnowSpeed.py` → Continuous spawning

All original functionality is preserved while adding FastAPI integration and improved configuration management.

## Troubleshooting

### Common Issues

1. **Audio not loading**: Check file path and format (WAV recommended)
2. **Slow rendering**: Reduce particle count or resolution
3. **Memory issues**: Lower `max_particles` for continuous spawning
4. **No particles visible**: Check particle count and screen boundaries

### Debug Mode

Enable debug output by setting environment variable:
```bash
export PARTICLE_DEBUG=1
```

## License

This unified particle system is part of the clipizy project and follows the same licensing terms.
