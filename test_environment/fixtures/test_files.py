#!/usr/bin/env python3
"""
Test File Generator
Creates test files for various testing scenarios
"""

import os
import tempfile
import wave
import struct
from pathlib import Path

class TestFileGenerator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.generated_files = []

    def create_test_audio_mp3(self, filename="test_audio.mp3", duration=30):
        """Create a test MP3 file"""
        file_path = os.path.join(self.temp_dir, filename)
        
        # Create a simple audio file (fake MP3 content)
        with open(file_path, 'wb') as f:
            # MP3 header
            f.write(b'\xff\xfb\x90\x00')
            # Fake audio data
            for i in range(duration * 1000):  # 30 seconds of fake data
                f.write(b'\x00' * 100)
        
        self.generated_files.append(file_path)
        return file_path

    def create_test_audio_wav(self, filename="test_audio.wav", duration=30):
        """Create a test WAV file"""
        file_path = os.path.join(self.temp_dir, filename)
        
        # WAV file parameters
        sample_rate = 44100
        num_channels = 2
        bits_per_sample = 16
        num_samples = int(sample_rate * duration)
        
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(bits_per_sample // 8)
            wav_file.setframerate(sample_rate)
            
            # Generate simple sine wave
            for i in range(num_samples):
                # Generate a simple sine wave
                sample = int(32767 * 0.1 * (i % 100) / 100)
                wav_file.writeframes(struct.pack('<h', sample))
                wav_file.writeframes(struct.pack('<h', sample))  # Stereo
        
        self.generated_files.append(file_path)
        return file_path

    def create_test_image_jpg(self, filename="test_image.jpg", width=1920, height=1080):
        """Create a test JPG file"""
        file_path = os.path.join(self.temp_dir, filename)
        
        # Create a simple JPG file (fake content)
        with open(file_path, 'wb') as f:
            # JPG header
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00')
            # Fake image data
            f.write(b'\xff\xd9')  # JPG end marker
        
        self.generated_files.append(file_path)
        return file_path

    def create_test_image_png(self, filename="test_image.png", width=1920, height=1080):
        """Create a test PNG file"""
        file_path = os.path.join(self.temp_dir, filename)
        
        # Create a simple PNG file (fake content)
        with open(file_path, 'wb') as f:
            # PNG signature
            f.write(b'\x89PNG\r\n\x1a\n')
            # Fake PNG data
            f.write(b'\x00\x00\x00\rIHDR\x00\x00\x07\x80\x00\x00\x04\x38\x08\x02\x00\x00\x00')
            f.write(b'\x00\x00\x00\x00IEND\xaeB`\x82')
        
        self.generated_files.append(file_path)
        return file_path

    def create_test_video_mp4(self, filename="test_video.mp4", duration=30):
        """Create a test MP4 file"""
        file_path = os.path.join(self.temp_dir, filename)
        
        # Create a simple MP4 file (fake content)
        with open(file_path, 'wb') as f:
            # MP4 header
            f.write(b'\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp41mp42')
            # Fake video data
            for i in range(duration * 10):  # 30 seconds of fake data
                f.write(b'\x00' * 1000)
        
        self.generated_files.append(file_path)
        return file_path

    def create_test_text_file(self, filename="test_file.txt", content="Test file content"):
        """Create a test text file"""
        file_path = os.path.join(self.temp_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        self.generated_files.append(file_path)
        return file_path

    def create_all_test_files(self):
        """Create all test files"""
        files = {}
        
        files['audio_mp3'] = self.create_test_audio_mp3()
        files['audio_wav'] = self.create_test_audio_wav()
        files['image_jpg'] = self.create_test_image_jpg()
        files['image_png'] = self.create_test_image_png()
        files['video_mp4'] = self.create_test_video_mp4()
        files['text_file'] = self.create_test_text_file()
        
        return files

    def cleanup(self):
        """Clean up generated files"""
        for file_path in self.generated_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass
        
        try:
            os.rmdir(self.temp_dir)
        except:
            pass

    def get_file_info(self, file_path):
        """Get information about a test file"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'size': stat.st_size,
            'filename': os.path.basename(file_path),
            'extension': os.path.splitext(file_path)[1]
        }

def main():
    """Main function to generate test files"""
    print("🧪 Generating Test Files...")
    
    generator = TestFileGenerator()
    
    try:
        files = generator.create_all_test_files()
        
        print("✅ Generated test files:")
        for file_type, file_path in files.items():
            info = generator.get_file_info(file_path)
            if info:
                print(f"  - {file_type}: {info['filename']} ({info['size']} bytes)")
        
        print(f"\n📁 Test files created in: {generator.temp_dir}")
        print("💡 Use these files for testing file upload functionality")
        
    except Exception as e:
        print(f"❌ Error generating test files: {e}")
    finally:
        # Don't cleanup in main - let tests use the files
        pass

if __name__ == "__main__":
    main()
