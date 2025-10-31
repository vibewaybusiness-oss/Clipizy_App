#!/usr/bin/env python3
"""
Create a simple test audio file for the welcome flow
"""

import numpy as np
import wave
import os

def create_test_audio():
    # Audio parameters
    sample_rate = 44100
    duration = 3  # 3 seconds
    frequency = 440  # A4 note
    
    # Generate a simple melody (C major scale)
    frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 to C5
    note_duration = duration / len(frequencies)
    
    # Create time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate audio
    audio = np.zeros_like(t)
    
    for i, freq in enumerate(frequencies):
        start_time = i * note_duration
        end_time = (i + 1) * note_duration
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        
        # Generate sine wave with envelope
        note_t = t[start_sample:end_sample]
        envelope = np.exp(-(note_t - start_time) * 2)  # Decay envelope
        note_audio = np.sin(2 * np.pi * freq * note_t) * 0.3 * envelope
        
        audio[start_sample:end_sample] = note_audio
    
    # Convert to 16-bit PCM
    audio_16bit = (audio * 32767).astype(np.int16)
    
    # Save as WAV file
    output_path = "public/test-audio/welcome-test-song.wav"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_16bit.tobytes())
    
    print(f"✅ Test audio file created: {output_path}")
    print(f"📊 File size: {os.path.getsize(output_path)} bytes")
    print(f"🎵 Duration: {duration} seconds")
    print(f"🎼 Sample rate: {sample_rate} Hz")

if __name__ == "__main__":
    create_test_audio()
