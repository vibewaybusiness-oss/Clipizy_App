#!/usr/bin/env python3
"""
Example usage of the Unified Particle System for FastAPI integration.

This script demonstrates how to use the unified particle system
with different particle types and configurations.
"""

import os
import sys
from pathlib import Path

# Add the API directory to the Python path
api_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(api_dir))

from processing.music.generator.particles.unified_particle_system import (
    ParticleConfig,
    ParticleType,
    UnifiedParticleSystem,
)


def example_basic_usage():
    """Basic usage example with default configuration"""
    print("🎬 Basic Usage Example")
    print("=" * 50)
    
    # Create a basic particle system
    system = UnifiedParticleSystem(particle_type=ParticleType.ENHANCED)
    
    # Print system status
    status = system.get_status()
    print(f"Particle Type: {status['particle_type']}")
    print(f"Particle Count: {status['particle_count']}")
    print(f"Resolution: {status['config']['width']}x{status['config']['height']}")
    print(f"FPS: {status['config']['fps']}")
    print(f"Duration: {status['config']['duration']}s")
    
    # Render without audio
    output_path = "example_basic_particles.mp4"
    system.render_particles(output_path)
    print(f"✅ Rendered: {output_path}")


def example_snow_particles():
    """Snow particles example with custom configuration"""
    print("\n❄️ Snow Particles Example")
    print("=" * 50)
    
    # Custom configuration for snow particles
    config = ParticleConfig(
        width=1280,
        height=720,
        fps=30,
        duration=10.0,
        particle_count=100,
        bass_threshold=0.2,
        enhanced_mode={
            "active": True,
            "threshold": 0.2,
            "factor": 1.5
        }
    )
    
    # Create snow particle system
    system = UnifiedParticleSystem(particle_type=ParticleType.SNOW, config=config)
    
    # Load audio if available
    audio_path = "song.wav"
    if os.path.exists(audio_path):
        system.load_audio(audio_path)
        print(f"🎵 Audio loaded: {audio_path}")
    else:
        print("⚠️ No audio file found, using default movement")
    
    # Render with audio
    output_path = "example_snow_particles.mp4"
    system.render_particles(output_path, audio_path if os.path.exists(audio_path) else None)
    print(f"✅ Rendered: {output_path}")


def example_continuous_spawning():
    """Continuous spawning particles example"""
    print("\n🔄 Continuous Spawning Example")
    print("=" * 50)
    
    # Configuration for continuous spawning
    config = ParticleConfig(
        width=1920,
        height=1080,
        fps=30,
        duration=15.0,
        base_particle_count=50,
        max_particles=500,
        steady_spawn_rate=1.0,
        bass_threshold=0.3,
        spawn_center_x=0.5,
        spawn_center_y=0.5,
        spawn_area_width=0.1,
        spawn_area_height=0.1,
        enhanced_mode={
            "active": True,
            "threshold": 0.3,
            "factor": 1.2
        }
    )
    
    # Create continuous spawning system
    system = UnifiedParticleSystem(particle_type=ParticleType.CONTINUOUS_SPAWNING, config=config)
    
    # Load audio if available
    audio_path = "song.wav"
    if os.path.exists(audio_path):
        system.load_audio(audio_path)
        print(f"🎵 Audio loaded: {audio_path}")
    
    # Render
    output_path = "example_continuous_spawning.mp4"
    system.render_particles(output_path, audio_path if os.path.exists(audio_path) else None)
    print(f"✅ Rendered: {output_path}")


def example_colored_particles():
    """Colored particles example"""
    print("\n🌈 Colored Particles Example")
    print("=" * 50)
    
    # Configuration with multiple colors
    config = ParticleConfig(
        width=1280,
        height=720,
        fps=30,
        duration=8.0,
        particle_count=150,
        particle_colors=[
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
        ],
        speed_x=0,
        speed_y=0,
        speed_z=0.1,  # Size changes
        bounce=True,  # Bounce off edges
        bass_threshold=0.25
    )
    
    # Create enhanced particle system with colors
    system = UnifiedParticleSystem(particle_type=ParticleType.ENHANCED, config=config)
    
    # Load audio if available
    audio_path = "song.wav"
    if os.path.exists(audio_path):
        system.load_audio(audio_path)
        print(f"🎵 Audio loaded: {audio_path}")
    
    # Render
    output_path = "example_colored_particles.mp4"
    system.render_particles(output_path, audio_path if os.path.exists(audio_path) else None)
    print(f"✅ Rendered: {output_path}")


def example_dynamic_configuration():
    """Example of dynamic configuration changes"""
    print("\n⚙️ Dynamic Configuration Example")
    print("=" * 50)
    
    # Start with basic configuration
    system = UnifiedParticleSystem(particle_type=ParticleType.ZEN)
    print(f"Initial particle count: {system.particle_count}")
    
    # Update configuration
    new_config = {
        "particle_count": 200,
        "bass_threshold": 0.4,
        "enhanced_mode": {
            "active": True,
            "threshold": 0.4,
            "factor": 2.5
        }
    }
    system.update_config(new_config)
    print(f"Updated particle count: {system.particle_count}")
    print(f"Updated bass threshold: {system.bass_threshold}")
    
    # Change particle type
    system.change_particle_type(ParticleType.BOUNCING)
    print(f"Changed to: {system.particle_type.value}")
    
    # Render with new configuration
    output_path = "example_dynamic_config.mp4"
    system.render_particles(output_path)
    print(f"✅ Rendered: {output_path}")


def example_all_particle_types():
    """Example showing all particle types"""
    print("\n🎭 All Particle Types Example")
    print("=" * 50)
    
    # Basic configuration for all types
    config = ParticleConfig(
        width=640,
        height=360,
        fps=15,
        duration=3.0,
        particle_count=30
    )
    
    # Test all particle types
    for particle_type in ParticleType:
        print(f"\nTesting {particle_type.value} particles...")
        
        # Create system
        system = UnifiedParticleSystem(particle_type=particle_type, config=config)
        
        # Get particle type info
        info = system.get_particle_type_info(particle_type)
        print(f"  Name: {info['name']}")
        print(f"  Description: {info['description']}")
        print(f"  Features: {', '.join(info['features'])}")
        
        # Render
        output_path = f"example_{particle_type.value}_particles.mp4"
        system.render_particles(output_path)
        print(f"  ✅ Rendered: {output_path}")


def example_fastapi_simulation():
    """Simulate FastAPI usage patterns"""
    print("\n🚀 FastAPI Simulation Example")
    print("=" * 50)
    
    # Simulate creating multiple systems
    systems = {}
    
    # Create different particle systems
    particle_types = [
        ParticleType.SNOW,
        ParticleType.ENHANCED,
        ParticleType.CONTINUOUS_SPAWNING
    ]
    
    for i, particle_type in enumerate(particle_types):
        system_id = f"system_{i+1}"
        config = ParticleConfig(
            width=1280,
            height=720,
            fps=30,
            duration=5.0,
            particle_count=50 + i * 25
        )
        systems[system_id] = UnifiedParticleSystem(particle_type=particle_type, config=config)
        print(f"Created {system_id}: {particle_type.value}")
    
    # Simulate getting system statuses
    print("\nSystem Statuses:")
    for system_id, system in systems.items():
        status = system.get_status()
        print(f"  {system_id}: {status['particle_type']} - {status['particle_count']} particles")
    
    # Simulate configuration updates
    print("\nUpdating configurations...")
    for system_id, system in systems.items():
        new_config = {
            "bass_threshold": 0.2,
            "enhanced_mode": {
                "active": True,
                "threshold": 0.2,
                "factor": 1.8
            }
        }
        system.update_config(new_config)
        print(f"  Updated {system_id}")
    
    # Simulate rendering
    print("\nRendering systems...")
    for system_id, system in systems.items():
        output_path = f"fastapi_sim_{system_id}.mp4"
        system.render_particles(output_path)
        print(f"  ✅ Rendered {system_id}: {output_path}")


def main():
    """Run all examples"""
    print("🎬 Unified Particle System Examples")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("examples_output", exist_ok=True)
    os.chdir("examples_output")
    
    try:
        # Run examples
        example_basic_usage()
        example_snow_particles()
        example_continuous_spawning()
        example_colored_particles()
        example_dynamic_configuration()
        example_all_particle_types()
        example_fastapi_simulation()
        
        print("\n🎉 All examples completed successfully!")
        print(f"📁 Output files saved in: {os.getcwd()}")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
