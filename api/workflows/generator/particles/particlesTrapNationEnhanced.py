import math
import os
import shutil
import subprocess
import time

import cv2
import librosa
import numpy as np


class TrapNationParticles:
    """
    Trap Nation inspired particle system with continuous bass-based spawning:
    - Particles spawn from center, move outward and disappear at edges
    - Continuous spawning based on bass levels (speed calculation)
    - Steady spawning even without bass to prevent gaps
    - Bass-responsive particle count and movement speed
    - Distance-based fading effects
    """

    def __init__(
        self,
        width=1920,
        height=1080,
        fps=30,
        x_position=0.5,
        y_position=0.5,
        base_particle_count=200,
        duration=10.0,
        bass_threshold=0.3,
        outer_movement_strength=2.0,
        inner_movement_strength=1.0,
        steady_spawn_rate=0.5,  # Particles per frame without bass
        max_particles=1000,  # Maximum particles to prevent performance issues
        enhanced_mode={"active": True, "threshold": 0.3, "factor": 1.20},
        spawn_center_x=0.5,  # Center X position for spawning area (0.0-1.0)
        spawn_center_y=0.5,  # Center Y position for spawning area (0.0-1.0)
        spawn_area_width=0.0,  # Width of spawning area as percentage (0.0-1.0)
        spawn_area_height=0.0,  # Height of spawning area as percentage (0.0-1.0)
    ):
        self.W = width
        self.H = height
        self.fps = int(fps)
        
        # Position
        self.x_pos = float(x_position)
        self.y_pos = float(y_position)
        self.cx = int(self.W * self.x_pos)
        self.cy = int(self.H * self.y_pos)
        
        # Particle settings
        self.base_particle_count = int(base_particle_count)
        self.duration = float(duration)
        self.steady_spawn_rate = float(steady_spawn_rate)
        self.max_particles = int(max_particles)
        
        # Music-dependent settings
        self.bass_threshold = float(bass_threshold)
        self.outer_movement_strength = float(outer_movement_strength)
        self.inner_movement_strength = float(inner_movement_strength)
        
        # Enhanced mode settings
        self.enhanced_mode = enhanced_mode
        
        # Spawning area settings
        self.spawn_center_x = float(spawn_center_x)
        self.spawn_center_y = float(spawn_center_y)
        self.spawn_area_width = float(spawn_area_width)
        self.spawn_area_height = float(spawn_area_height)
        
        # Calculate spawning area bounds
        self.spawn_center_px_x = int(self.W * self.spawn_center_x)
        self.spawn_center_px_y = int(self.H * self.spawn_center_y)
        self.spawn_area_px_width = int(self.W * self.spawn_area_width)
        self.spawn_area_px_height = int(self.H * self.spawn_area_height)
        
        # Audio data
        self.audio_data = None
        self.sample_rate = None
        self.bass_frequencies = None
        
        # Pre-allocate black frame
        self.black_frame = np.zeros((self.H, self.W, 3), dtype=np.uint8)
        
        # Particle system - start with empty list for continuous spawning
        self.particles = []
        
        # Spawning tracking
        self.spawn_accumulator = 0.0  # Accumulator for fractional spawning

    def _spawn_new_particle(self, bass_level=0.0):
        """Spawn a new particle with bass-responsive properties from spawning area"""
        # Start from spawning area (random position within area)
        if self.spawn_area_width > 0 and self.spawn_area_height > 0:
            # Spawn randomly within the spawning area
            x = self.spawn_center_px_x + np.random.uniform(-self.spawn_area_px_width/2, self.spawn_area_px_width/2)
            y = self.spawn_center_px_y + np.random.uniform(-self.spawn_area_px_height/2, self.spawn_area_px_height/2)
        else:
            # Spawn at center if no area specified
            x = self.spawn_center_px_x
            y = self.spawn_center_px_y
        
        # Bass-responsive speed and direction using enhanced mode factor
        base_speed = np.random.uniform(0.5, 2.0)
        speed_factor = self.enhanced_mode.get("factor", 1.0) if self.enhanced_mode.get("active", False) else 1.0
        speed_multiplier = 1.0 + bass_level * speed_factor  # Bass increases speed based on factor
        speed = base_speed * speed_multiplier
        
        # Random direction
        angle = np.random.uniform(0, 2 * np.pi)
        vx = speed * np.cos(angle)
        vy = speed * np.sin(angle)
        
        # Bass-responsive size and brightness
        base_size = np.random.uniform(1, 3)
        size_multiplier = 1.0 + bass_level * 0.5  # Bass increases size up to 1.5x
        size = base_size * size_multiplier
        
        base_brightness = np.random.uniform(0.4, 0.8)
        brightness_multiplier = 1.0 + bass_level * 0.5  # Bass increases brightness
        brightness = min(1.0, base_brightness * brightness_multiplier)
        
        return {
            'x': x, 'y': y,
            'vx': vx,
            'vy': vy,
            'size': size,
            'brightness': brightness,
            'pulse_phase': np.random.uniform(0, 2 * np.pi),
            'life': 1.0,
            'age': 0,  # Track particle age
        }

    def load_audio(self, audio_path):
        """Load audio file and extract bass frequencies"""
        print(f"🎵 Loading audio: {audio_path}")
        self.audio_data, self.sample_rate = librosa.load(audio_path, sr=None, mono=True)
        print(f"📊 Audio loaded: {len(self.audio_data)} samples at {self.sample_rate}Hz")
        
        # Extract bass frequencies (0-250 Hz)
        self.bass_frequencies = self._extract_bass_frequencies()
        print(f"🎸 Bass frequencies extracted: {len(self.bass_frequencies)} frames")

    def _extract_bass_frequencies(self):
        """Extract bass frequency energy for each frame"""
        if self.audio_data is None:
            return np.zeros(int(self.duration * self.fps))
        
        # Calculate samples per frame
        samples_per_frame = max(1, int(self.sample_rate / self.fps))
        total_frames = int(self.duration * self.fps)
        
        # Create window for FFT
        window = np.hanning(samples_per_frame).astype(np.float32)
        bass_frequencies = np.zeros(total_frames, dtype=np.float32)
        
        # Bass frequency range (0-250 Hz)
        bass_low = 0
        bass_high = 250
        
        for i in range(total_frames):
            start_idx = i * samples_per_frame
            end_idx = min(start_idx + samples_per_frame, len(self.audio_data))
            
            if start_idx >= len(self.audio_data):
                bass_frequencies[i] = 0.0
                continue
            
            segment = self.audio_data[start_idx:end_idx].astype(np.float32)
            if len(segment) < samples_per_frame:
                segment = np.pad(segment, (0, samples_per_frame - len(segment)), mode="constant")
            
            # Apply window and FFT
            segment_windowed = segment * window
            spec = np.fft.rfft(segment_windowed)
            mag = np.abs(spec)
            
            # Convert frequency bins to Hz
            freqs = np.fft.rfftfreq(samples_per_frame, 1/self.sample_rate)
            
            # Extract bass frequencies
            bass_mask = (freqs >= bass_low) & (freqs <= bass_high)
            if np.any(bass_mask):
                bass_energy = np.mean(mag[bass_mask])
            else:
                bass_energy = 0.0
            
            bass_frequencies[i] = bass_energy
        
        # Normalize bass frequencies
        max_bass = np.max(bass_frequencies)
        if max_bass > 0:
            bass_frequencies = bass_frequencies / max_bass
        
        return bass_frequencies

    def _get_bass_level_at_frame(self, frame_idx):
        """Get bass level at specific frame"""
        if self.bass_frequencies is None or frame_idx >= len(self.bass_frequencies):
            return 0.0
        return float(self.bass_frequencies[frame_idx])

    def _apply_enhanced_mode(self, bass_level):
        """Apply enhanced mode processing to bass level"""
        if not self.enhanced_mode or not self.enhanced_mode.get("active", False):
            return bass_level
        
        # Get enhanced mode parameters
        threshold = self.enhanced_mode.get("threshold", 0.3)
        factor = self.enhanced_mode.get("factor", 2.0)
        
        # Apply threshold and enhancement
        if bass_level >= threshold:
            # Apply enhancement factor to values above threshold
            enhanced_bass = min(1.0, bass_level * factor)
        else:
            # Keep values below threshold as they are
            enhanced_bass = bass_level
        
        return enhanced_bass

    def _calculate_spawn_rate(self, bass_level):
        """Calculate particles to spawn based on bass level, proportional to max_particles"""
        # Base steady spawn rate proportional to max_particles
        base_spawn = self.steady_spawn_rate * (self.max_particles / 1000.0)
        
        # Bass-responsive spawn rate proportional to max_particles
        if bass_level > self.bass_threshold:
            # High bass: much more aggressive spawning based on speed
            bass_spawn = bass_level * 12.0 * (self.max_particles / 1000.0)  # Proportional to max_particles
        else:
            # Low bass: still significant spawn rate increase
            bass_spawn = bass_level * 3.0 * (self.max_particles / 1000.0)  # Proportional to max_particles
        
        return base_spawn + bass_spawn

    def _update_particles(self, t, frame_idx):
        """Update particle system with continuous bass-based spawning"""
        # Get current bass level
        raw_bass_level = self._get_bass_level_at_frame(frame_idx)
        bass_level = self._apply_enhanced_mode(raw_bass_level)
        
        # Calculate spawn rate based on bass
        spawn_rate = self._calculate_spawn_rate(bass_level)
        
        # Add to spawn accumulator
        self.spawn_accumulator += spawn_rate
        
        # Spawn new particles
        while self.spawn_accumulator >= 1.0 and len(self.particles) < self.max_particles:
            new_particle = self._spawn_new_particle(bass_level)
            self.particles.append(new_particle)
            self.spawn_accumulator -= 1.0
        
        # Update existing particles
        particles_to_remove = []
        
        for i, particle in enumerate(self.particles):
            # Add bass-responsive movement using enhanced mode factor
            if bass_level > self.bass_threshold:
                # High bass: increase speed using enhanced mode factor
                speed_factor = self.enhanced_mode.get("factor", 1.0) if self.enhanced_mode.get("active", False) else 1.0
                speed_multiplier = 1.0 + bass_level * speed_factor * 0.1  # Scale down for movement updates
                particle['vx'] *= speed_multiplier
                particle['vy'] *= speed_multiplier
            
            # Apply gentle air resistance
            particle['vx'] *= 0.998
            particle['vy'] *= 0.998
            
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Update age
            particle['age'] += 1
            
            # Update pulse phase and brightness
            particle['pulse_phase'] += 0.05 + bass_level * 0.1
            base_brightness = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(particle['pulse_phase']))
            particle['brightness'] = base_brightness * (0.7 + 0.3 * bass_level)
            
            # Fade out particles as they get further from center
            distance_from_center = np.sqrt((particle['x'] - self.cx)**2 + (particle['y'] - self.cy)**2)
            max_distance = np.sqrt(self.W**2 + self.H**2) / 2
            fade_factor = max(0.1, 1.0 - (distance_from_center / max_distance))
            particle['life'] = fade_factor
            
            # Remove particles that are outside frame or too old
            if (particle['x'] < -50 or particle['x'] > self.W + 50 or 
                particle['y'] < -50 or particle['y'] > self.H + 50 or
                particle['age'] > 1000):  # Remove very old particles
                particles_to_remove.append(i)
        
        # Remove particles (in reverse order to maintain indices)
        for i in reversed(particles_to_remove):
            self.particles.pop(i)

    def _draw_particles(self, frame):
        """Draw particles with life fading"""
        for particle in self.particles:
            x, y = int(particle['x']), int(particle['y'])
            if 0 <= x < self.W and 0 <= y < self.H:
                size = int(particle['size'])
                # Apply life fading
                final_brightness = particle['brightness'] * particle['life']
                brightness = int(255 * final_brightness)
                
                # Draw circular particles
                cv2.circle(frame, (x, y), size, (brightness, brightness, brightness), -1)
        return frame

    def _draw_bass_indicator(self, frame, frame_idx):
        """Draw bass level indicator and spawn rate info"""
        raw_bass_level = self._get_bass_level_at_frame(frame_idx)
        enhanced_bass_level = self._apply_enhanced_mode(raw_bass_level)
        spawn_rate = self._calculate_spawn_rate(enhanced_bass_level)
        
        # Draw bass level bar at top of screen
        bar_width = 400
        bar_height = 20
        bar_x = (self.W - bar_width) // 2
        bar_y = 50
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        # Bass level bar (use enhanced level for display)
        level_width = int(bar_width * enhanced_bass_level)
        if enhanced_bass_level > self.bass_threshold:
            # High bass - red color
            color = (0, 0, 255)  # Red
            text = "HIGH BASS - INCREASED SPAWNING"
        else:
            # Low bass - blue color
            color = (255, 0, 0)  # Blue
            text = "LOW BASS - STEADY SPAWNING"
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + level_width, bar_y + bar_height), color, -1)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 0.6, 2)[0]
        text_x = (self.W - text_size[0]) // 2
        text_y = bar_y + bar_height + 30
        cv2.putText(frame, text, (text_x, text_y), font, 0.6, color, 2)
        
        # Add spawn rate info
        spawn_text = f"Spawn Rate: {spawn_rate:.2f} particles/frame | Active Particles: {len(self.particles)}"
        spawn_text_size = cv2.getTextSize(spawn_text, font, 0.4, 1)[0]
        spawn_text_x = (self.W - spawn_text_size[0]) // 2
        spawn_text_y = text_y + 25
        cv2.putText(frame, spawn_text, (spawn_text_x, spawn_text_y), font, 0.4, (255, 255, 255), 1)
        
        # Add enhanced mode indicator
        if self.enhanced_mode.get("active", False) and raw_bass_level >= self.enhanced_mode.get("threshold", 0.3):
            enhanced_text = f"ENHANCED! (x{self.enhanced_mode.get('factor', 2.0)})"
            enhanced_text_size = cv2.getTextSize(enhanced_text, font, 0.5, 2)[0]
            enhanced_text_x = (self.W - enhanced_text_size[0]) // 2
            enhanced_text_y = spawn_text_y + 20
            cv2.putText(frame, enhanced_text, (enhanced_text_x, enhanced_text_y), font, 0.5, (0, 255, 255), 2)
        
        # Add bass level percentages (raw and enhanced)
        level_text = f"Raw: {raw_bass_level:.2f} ({raw_bass_level*100:.0f}%) | Enhanced: {enhanced_bass_level:.2f} ({enhanced_bass_level*100:.0f}%)"
        level_text_size = cv2.getTextSize(level_text, font, 0.4, 1)[0]
        level_text_x = (self.W - level_text_size[0]) // 2
        level_text_y = spawn_text_y + 45
        cv2.putText(frame, level_text, (level_text_x, level_text_y), font, 0.4, (255, 255, 255), 1)
        
        return frame

    def render_particles_test(self, output_path, audio_path=None):
        """Render particles test on black background with optional audio"""
        start_time = time.time()
        print("🚀 Starting Trap Nation continuous spawning particles test render...")
        
        # Load audio if provided
        if audio_path and os.path.exists(audio_path):
            self.load_audio(audio_path)
        else:
            print("⚠️ No audio file provided or file not found, using default movement")
        
        # Calculate total frames
        total_frames = int(self.duration * self.fps)
        frame_times = np.arange(total_frames, dtype=np.float32) / self.fps
        
        # Video writer
        writer_start = time.time()
        tmp_out = output_path + ".temp.mp4"
        self._ensure_dir(os.path.dirname(output_path))
        writer = cv2.VideoWriter(tmp_out, cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (self.W, self.H))
        if not writer.isOpened():
            raise RuntimeError("Failed to open video writer")
        writer_time = time.time() - writer_start
        print(f"📝 Video writer setup: {writer_time:.3f}s")
        
        # Performance tracking
        render_time_total = 0
        write_time_total = 0
        
        # Main rendering loop
        render_start = time.time()
        for i in range(total_frames):
            t = frame_times[i]
            
            # Start with black frame
            frame = self.black_frame.copy()
            
            # Update particles with frame index for bass analysis
            self._update_particles(t, i)
            
            # Draw particles
            render_start_frame = time.time()
            frame = self._draw_particles(frame)
            
            # Draw bass level indicator
            frame = self._draw_bass_indicator(frame, i)
            
            render_time_total += time.time() - render_start_frame
            
            # Write frame
            write_start = time.time()
            writer.write(frame)
            write_time_total += time.time() - write_start
            
            # Progress reporting
            if total_frames > 0 and i % max(1, total_frames // 10) == 0:
                elapsed = time.time() - render_start
                fps_actual = (i + 1) / elapsed if elapsed > 0 else 0
                print(f"Progress: {int(100 * i / total_frames)}% | Elapsed: {elapsed:.1f}s | FPS: {fps_actual:.1f} | Particles: {len(self.particles)}")

        render_time = time.time() - render_start
        print(f"🎬 Frame rendering: {render_time:.3f}s ({render_time/total_frames*1000:.1f}ms per frame)")

        writer.release()

        # Finalize
        finalize_start = time.time()
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(tmp_out, output_path)
        finalize_time = time.time() - finalize_start
        print(f"📁 File operations: {finalize_time:.3f}s")
        
        # Audio muxing
        if audio_path and os.path.exists(audio_path):
            audio_mux_start = time.time()
            self._mux_audio(output_path, audio_path)
            audio_mux_time = time.time() - audio_mux_start
            print(f"🔊 Audio muxing: {audio_mux_time:.3f}s")
        
        # Performance summary
        total_time = time.time() - start_time
        realtime_ratio = self.duration / total_time if total_time > 0 else 0
        
        print("\n" + "="*60)
        print("📊 TRAP NATION CONTINUOUS SPAWNING PARTICLES PERFORMANCE")
        print("="*60)
        print(f"🎬 Frame rendering:      {render_time:6.3f}s ({render_time/total_time*100:5.1f}%)")
        print(f"📝 Video writer setup:   {writer_time:6.3f}s ({writer_time/total_time*100:5.1f}%)")
        print(f"📁 File operations:      {finalize_time:6.3f}s ({finalize_time/total_time*100:5.1f}%)")
        print("-"*60)
        print(f"⏱️  Total time:           {total_time:6.3f}s")
        print(f"🎬 Video duration:       {self.duration:6.1f}s")
        print(f"⚡ Speed ratio:          {realtime_ratio:6.2f}x realtime")
        print(f"🎯 Avg FPS:              {total_frames/total_time:6.1f} fps")
        print(f"✨ Max particles:        {self.max_particles}")
        print(f"📈 Steady spawn rate:    {self.steady_spawn_rate} particles/frame")
        print("="*60)
        print(f"✅ Done: {output_path}")

    def _mux_audio(self, video_path, audio_path):
        """Mux audio into video using ffmpeg"""
        if not audio_path or not os.path.exists(audio_path):
            print("⚠️ No audio file provided for muxing")
            return
            
        temp_out = video_path + ".with_audio.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "320k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",  # End when shortest stream ends
            temp_out
        ]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode == 0 and os.path.exists(temp_out) and os.path.getsize(temp_out) > 0:
                os.remove(video_path)
                shutil.move(temp_out, video_path)
                print("🔊 Audio muxed into video.")
            else:
                if os.path.exists(temp_out):
                    os.remove(temp_out)
                print("⚠️ ffmpeg failed; leaving video without audio.")
        except Exception as e:
            print(f"⚠️ ffmpeg not available or error occurred: {e}. Leaving video without audio.")

    @staticmethod
    def _ensure_dir(d):
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)


def test_trap_nation_particles():
    """
    Test function to create a music-dependent particles video with continuous bass-based spawning
    """
    OUTPUT = "trap_nation_continuous_spawning_particles_test.mp4"
    AUDIO = "song.wav"
    
    # Create continuous spawning particles visualizer
    particles = TrapNationParticles(
        width=1920,
        height=1080,
        fps=30,
        x_position=0.5,
        y_position=0.5,
        base_particle_count=30,  # Base count (continuous spawning will add more)
        duration=15.0,  # 15 seconds test
        bass_threshold=0.3,  # Bass threshold for increased spawning
        outer_movement_strength=2.0,  # Strength of outward movement during bass
        inner_movement_strength=1.0,  # Not used in continuous spawning mode
        steady_spawn_rate=0.5,  # 0.5 particles per frame without bass
        max_particles=1000,  # Maximum particles to prevent performance issues
        enhanced_mode={"active": True, "threshold": 0.3, "factor": 1.20},
        spawn_center_x=0.5,  # Center X position for spawning area
        spawn_center_y=0.5,  # Center Y position for spawning area
        spawn_area_width=0.1,  # Width of spawning area (10% of screen)
        spawn_area_height=0.1,  # Height of spawning area (10% of screen)
    )
    
    # Render the test with audio
    particles.render_particles_test(OUTPUT, audio_path=AUDIO)
    
    print(f"\n🎉 Trap Nation continuous spawning particles test completed!")
    print(f"📹 Output video: {OUTPUT}")
    print(f"🎵 Audio source: {AUDIO}")
    print(f"✨ Features:")
    print(f"   - Continuous spawning from center based on bass levels")
    print(f"   - Steady spawning ({particles.steady_spawn_rate} particles/frame) even without bass")
    print(f"   - Bass-responsive spawn rate (up to 12x during high bass)")
    print(f"   - Bass-responsive particle properties (speed controlled by factor: {particles.enhanced_mode.get('factor', 1.0)}, size, brightness)")
    print(f"   - Particles disappear at edges (no bouncing)")
    print(f"   - Distance-based fading effects")
    print(f"   - Maximum particle limit: {particles.max_particles}")
    print(f"   - Spawning area: center=({particles.spawn_center_x:.1f}, {particles.spawn_center_y:.1f}), size=({particles.spawn_area_width:.1f}, {particles.spawn_area_height:.1f})")
    print(f"   - Enhanced Mode: {particles.enhanced_mode}")
    print(f"   - {particles.duration}s duration at {particles.fps} FPS")


if __name__ == "__main__":
    test_trap_nation_particles()
