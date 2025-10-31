#!/usr/bin/env python3
"""
Example usage of the unified visualizer system
"""

import os
import sys
from pathlib import Path

# Add the api directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from unified_visualizers import (
    UnifiedVisualizerService,
    VisualizerConfig,
    VisualizerType,
)


def main():
    # Initialize the visualizer service
    service = UnifiedVisualizerService()
    
    # Example audio file path (you'll need to provide a real audio file)
    audio_path = "song.wav"  # Replace with actual audio file path
    
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        print("Please provide a valid audio file path")
        return
    
    # Example 1: Linear Bars Visualizer
    print("Creating Linear Bars Visualizer...")
    config_bars = VisualizerConfig(
        visualizer_type=VisualizerType.LINEAR_BARS,
        width=1920,
        height=1080,
        fps=30,
        n_segments=60,
        bar_thickness=3,
        bar_count=60,
        mirror_right=True,
        bar_height_min=10,
        bar_height_max=35,
        smoothness=0,
        x_position=50,
        y_position=50,
        color=(255, 50, 100),
        transparency=True,
        enhanced_mode={"active": True, "threshold": 0.3, "factor": 2.0}
    )
    
    output_bars = service.render_visualizer(
        audio_path=audio_path,
        output_path="output_bars.mp4",
        config=config_bars
    )
    print(f"Linear Bars output: {output_bars}")
    
    # Example 2: Linear Dots Visualizer
    print("Creating Linear Dots Visualizer...")
    config_dots = VisualizerConfig(
        visualizer_type=VisualizerType.LINEAR_DOTS,
        width=1920,
        height=1080,
        fps=30,
        n_segments=60,
        bar_thickness=3,
        bar_count=60,
        mirror_right=True,
        bar_height_min=10,
        bar_height_max=35,
        smoothness=10,
        x_position=50,
        y_position=50,
        color=(100, 200, 255),
        dot_size=3,
        dot_filled=True,
        transparency=False,
        top_active=False,
        bottom_active=True,
        enhanced_mode={"active": True, "threshold": 0.3, "factor": 2.0}
    )
    
    output_dots = service.render_visualizer(
        audio_path=audio_path,
        output_path="output_dots.mp4",
        config=config_dots
    )
    print(f"Linear Dots output: {output_dots}")
    
    # Example 3: Waveform Visualizer
    print("Creating Waveform Visualizer...")
    config_waveform = VisualizerConfig(
        visualizer_type=VisualizerType.WAVEFORM,
        width=1920,
        height=1080,
        fps=30,
        n_segments=120,
        bar_thickness=2,
        bar_count=120,
        mirror_right=True,
        bar_height_min=0,
        bar_height_max=40,
        smoothness=20,
        x_position=50,
        y_position=50,
        color=(100, 200, 255),
        fill_alpha=0.5,
        border_alpha=1.0,
        transparency=True,
        top_active=True,
        bottom_active=True,
        smooth_arcs=True,
        enhanced_mode={"active": True, "threshold": 0.3, "factor": 2.0}
    )
    
    output_waveform = service.render_visualizer(
        audio_path=audio_path,
        output_path="output_waveform.mp4",
        config=config_waveform
    )
    print(f"Waveform output: {output_waveform}")
    
    # Example 4: Bass Circle Visualizer
    print("Creating Bass Circle Visualizer...")
    config_circle = VisualizerConfig(
        visualizer_type=VisualizerType.BASS_CIRCLE,
        width=1920,
        height=1080,
        fps=30,
        n_segments=60,
        x_position=50,
        y_position=50,
        color=(255, 100, 200),
        dot_size=5,
        dot_filled=True,
        transparency=True
    )
    
    output_circle = service.render_visualizer(
        audio_path=audio_path,
        output_path="output_circle.mp4",
        config=config_circle
    )
    print(f"Bass Circle output: {output_circle}")
    
    # Example 5: Trap Nation Visualizer
    print("Creating Trap Nation Visualizer...")
    config_trap = VisualizerConfig(
        visualizer_type=VisualizerType.TRAP_NATION,
        width=1920,
        height=1080,
        fps=30,
        n_segments=60,
        bar_thickness=2,
        x_position=50,
        y_position=50,
        color=(200, 50, 255),
        transparency=True
    )
    
    output_trap = service.render_visualizer(
        audio_path=audio_path,
        output_path="output_trap.mp4",
        config=config_trap
    )
    print(f"Trap Nation output: {output_trap}")
    
    print("\nAll visualizers created successfully!")
    print("Available visualizer types:")
    for viz in service.get_available_visualizers():
        print(f"  - {viz['name']} ({viz['type']})")

if __name__ == "__main__":
    main()
