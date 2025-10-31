#!/usr/bin/env python3
"""
Create a simple test audio file for the welcome flow (without numpy)
"""

import math
import wave
import os
import struct

def create_test_audio():
    # Audio parameters
    sample_rate = 44100
    duration = 3  # 3 seconds
    
    # Generate a simple melody (C major scale)
    frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 to C5
    note_duration = duration / len(frequencies)
    
    # Calculate total samples
    total_samples = int(sample_rate * duration)
    audio_data = []
    
    for i in range(total_samples):
        time = i / sample_rate
        note_index = int(time / note_duration)
        
        if note_index < len(frequencies):
            freq = frequencies[note_index]
            # Generate sine wave with envelope
            envelope = math.exp(-(time % note_duration) * 2)  # Decay envelope
            sample = math.sin(2 * math.pi * freq * time) * 0.3 * envelope
        else:
            sample = 0
        
        # Convert to 16-bit PCM
        audio_data.append(int(sample * 32767))
    
    # Save as WAV file
    output_path = "public/test-audio/welcome-test-song.wav"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Write audio data
        for sample in audio_data:
            wav_file.writeframes(struct.pack('<h', sample))
    
    print(f"✅ Test audio file created: {output_path}")
    print(f"📊 File size: {os.path.getsize(output_path)} bytes")
    print(f"🎵 Duration: {duration} seconds")
    print(f"🎼 Sample rate: {sample_rate} Hz")

if __name__ == "__main__":
    create_test_audio()
