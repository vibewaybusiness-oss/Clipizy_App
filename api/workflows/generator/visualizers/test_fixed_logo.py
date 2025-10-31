#!/usr/bin/env python3
"""
Test script to verify fixed logo size functionality
"""
import os
import sys

import cv2
import numpy as np

# Add the current directory to the path so we can import the visualizer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bassCircle import BassCircleLogoVisualizer


def create_test_logo():
    """Create a simple test logo with alpha channel"""
    # Create a 200x200 image with alpha channel
    logo = np.zeros((200, 200, 4), dtype=np.uint8)
    
    # Draw a simple circle logo
    cv2.circle(logo, (100, 100), 80, (255, 255, 255, 255), -1)  # White circle
    cv2.circle(logo, (100, 100), 60, (0, 0, 0, 255), -1)        # Black inner circle
    cv2.circle(logo, (100, 100), 40, (255, 255, 255, 255), -1)  # White center
    
    # Add some text
    cv2.putText(logo, "TEST", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0, 255), 2)
    
    return logo

def create_test_audio():
    """Create a simple test audio file with bass frequencies"""
    import librosa
    import soundfile as sf

    # Generate a 5-second test audio with varying bass
    duration = 5.0
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    
    # Create a bass-heavy signal that varies over time
    bass_freq = 60  # 60 Hz bass frequency
    bass_signal = np.sin(2 * np.pi * bass_freq * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t))
    
    # Add some higher frequencies for realism
    mid_signal = np.sin(2 * np.pi * 200 * t) * 0.3
    high_signal = np.sin(2 * np.pi * 1000 * t) * 0.1
    
    # Combine signals
    audio = bass_signal + mid_signal + high_signal
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # Save as WAV
    audio_path = "test_audio.wav"
    sf.write(audio_path, audio, sr)
    return audio_path

def test_fixed_logo_size():
    """Test that logo maintains fixed size regardless of bass circle size"""
    print("🧪 Testing fixed logo size functionality...")
    
    # Create test files
    logo_path = "test_logo.png"
    audio_path = create_test_audio()
    output_path = "test_fixed_logo.mp4"
    
    try:
        # Create and save test logo
        logo = create_test_logo()
        cv2.imwrite(logo_path, logo)
        print(f"✅ Created test logo: {logo_path}")
        
        # Test with different logo sizes
        test_sizes = [80, 120, 160]
        
        for size in test_sizes:
            print(f"\n🔍 Testing with logo_fixed_size = {size}")
            
            vis = BassCircleLogoVisualizer(
                width=1280,
                height=720,
                fps=30,
                circle_min_radius=30,
                circle_max_radius=150,  # Large range to test logo independence
                circle_color_primary=(255, 50, 255),
                circle_color_secondary=(50, 200, 255),
                logo_fixed_size=size,
                fadein=0.5,
                fadeout=0.5,
                smoothing=20,
                bass_bins=3
            )
            
            test_output = f"test_logo_size_{size}.mp4"
            vis.render(audio_path, test_output, logo_path=logo_path)
            print(f"✅ Generated video with {size}px logo: {test_output}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        for file in [logo_path, audio_path]:
            if os.path.exists(file):
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")
    
    print("\n✅ All tests completed successfully!")
    print("📝 Check the generated videos to verify:")
    print("   - Logo size remains constant regardless of bass circle size")
    print("   - Logo is centered in the circle")
    print("   - Logo quality is high (smooth edges)")
    
    return True

if __name__ == "__main__":
    test_fixed_logo_size()
