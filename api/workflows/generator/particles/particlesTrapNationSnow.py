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
    Trap Nation inspired snowflake particle system with bass-triggered respawning:
    - Particles spawn from center, move outward and fade with distance
    - Bass-triggered respawning: particles respawn when bass hits threshold
    - Higher bass intensity = higher respawn probability and more new particles
    - Speed-responsive appearance: faster particles = higher spawn rate and respawn chance
    - Snowflake cross pattern rendering
    - Bass-responsive flow intensity and movement speed
    - Gentle drift and rotation effects
    - Distance-based fading
    """

    def __init__(
        self,
        width=1920,
        height=1080,
        fps=30,
        x_position=0.5,
        y_position=0.5,
        particle_count=500,
        duration=10.0,
        bass_threshold=0.3,
        outer_movement_strength=2.0,
        inner_movement_strength=1.0,
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
        self.particle_count = int(particle_count)
        self.duration = float(duration)

        # Music-dependent settings
        self.bass_threshold = float(bass_threshold)
        self.outer_movement_strength = float(outer_movement_strength)
        self.inner_movement_strength = float(inner_movement_strength)

        # Enhanced mode settings
        self.enhanced_mode = {
            "active": True,
            "threshold": 0.3,  # 30% of max bass level
            "factor": 2.0      # Multiplication factor when threshold is reached
        }

        # Audio data
        self.audio_data = None
        self.sample_rate = None
        self.bass_frequencies = None

        # Pre-allocate black frame
        self.black_frame = np.zeros((self.H, self.W, 3), dtype=np.uint8)

        # Particle system
        self.particles = self._init_particles()

    def _init_particles(self):
        """Initialize particle system for snowflake effects with outward movement"""
        particles = []
        for _ in range(self.particle_count):
            # Outward mode: start from center, move outward and disappear
            x = self.cx
            y = self.cy
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(0.5, 2.0)
            vx = speed * np.cos(angle)
            vy = speed * np.sin(angle)

            particles.append({
                'x': x, 'y': y,
                'vx': vx,
                'vy': vy,
                'size': np.random.uniform(1, 4),  # Snowflake size variation
                'brightness': np.random.uniform(0.6, 1.0),  # Brighter for snowflakes
                'pulse_phase': np.random.uniform(0, 2 * np.pi),
                'rotation': np.random.uniform(0, 2 * np.pi),  # Rotation for snowflakes
                'rotation_speed': np.random.uniform(-0.1, 0.1),  # Slow rotation
                'drift_x': np.random.uniform(-0.2, 0.2),  # Gentle horizontal drift
                'drift_y': np.random.uniform(-0.1, 0.1),  # Gentle vertical drift
                'life': 1.0,  # Life value for fading
            })
        return particles

    def _spawn_new_particle(self):
        """Spawn a new snowflake particle with outward movement"""
        # Outward mode: start from center, move outward
        x = self.cx
        y = self.cy
        angle = np.random.uniform(0, 2 * np.pi)
        speed = np.random.uniform(0.5, 2.0)
        vx = speed * np.cos(angle)
        vy = speed * np.sin(angle)

        return {
            'x': x, 'y': y,
            'vx': vx,
            'vy': vy,
            'size': np.random.uniform(1, 4),
            'brightness': np.random.uniform(0.6, 1.0),
            'pulse_phase': np.random.uniform(0, 2 * np.pi),
            'rotation': np.random.uniform(0, 2 * np.pi),
            'rotation_speed': np.random.uniform(-0.1, 0.1),
            'drift_x': np.random.uniform(-0.2, 0.2),
            'drift_y': np.random.uniform(-0.1, 0.1),
            'life': 1.0,
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

    def _update_particles(self, t, frame_idx):
        """Update snowflake particle system with bass-triggered respawning"""
        # Get current bass level for intensity effects
        raw_bass_level = self._get_bass_level_at_frame(frame_idx)
        bass_level = self._apply_enhanced_mode(raw_bass_level)

        # Process particles and handle bass-triggered respawning
        particles_to_respawn = []

        for i, particle in enumerate(self.particles):
            # Handle outward mode
            # Add gentle drift (snowflake floating effect)
            particle['vx'] += particle['drift_x'] * 0.01
            particle['vy'] += particle['drift_y'] * 0.01

            # Add bass-responsive intensity to movement
            if bass_level > self.bass_threshold:
                speed_multiplier = 1.0 + bass_level * 0.5
                particle['vx'] *= speed_multiplier
                particle['vy'] *= speed_multiplier

            # Apply gentle air resistance
            particle['vx'] *= 0.999
            particle['vy'] *= 0.999

            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            # BASS-TRIGGERED RESPAWNING: Respawn particles when bass is high
            # Instead of respawning at boundaries, respawn when bass hits
            if bass_level > self.bass_threshold:
                # Calculate probability of respawn based on bass intensity and particle speed
                particle_speed = np.sqrt(particle['vx']**2 + particle['vy']**2)
                speed_multiplier = 1.0 + (particle_speed / 5.0)  # Speed increases respawn chance

                base_respawn_probability = (bass_level - self.bass_threshold) * 0.3  # 0-30% base chance
                respawn_probability = base_respawn_probability * speed_multiplier  # Speed multiplies respawn chance

                if np.random.random() < respawn_probability:
                    particles_to_respawn.append(i)

            # Update rotation for snowflake effect
            particle['rotation'] += particle['rotation_speed']

            # Update pulse phase and brightness
            particle['pulse_phase'] += 0.05 + bass_level * 0.1
            base_brightness = 0.6 + 0.4 * (0.5 + 0.5 * np.sin(particle['pulse_phase']))
            particle['brightness'] = base_brightness * (0.8 + 0.2 * bass_level)

            # Fade out particles as they get further from center
            distance_from_center = np.sqrt((particle['x'] - self.cx)**2 + (particle['y'] - self.cy)**2)
            max_distance = np.sqrt(self.W**2 + self.H**2) / 2
            fade_factor = max(0.1, 1.0 - (distance_from_center / max_distance))
            particle['life'] = fade_factor

        # Handle bass-triggered respawning (in reverse order to maintain indices)
        for i in reversed(particles_to_respawn):
            self.particles[i] = self._spawn_new_particle()

        # Calculate average particle speed for spawn rate adjustment
        if self.particles:
            total_speed = 0
            for particle in self.particles:
                speed = np.sqrt(particle['vx']**2 + particle['vy']**2)
                total_speed += speed
            avg_speed = total_speed / len(self.particles)
            # Normalize speed factor (0-2x multiplier based on speed)
            speed_factor = min(2.0, avg_speed / 2.0)  # Cap at 2x multiplier
        else:
            speed_factor = 1.0

        # Spawn additional particles based on bass intensity and particle speed
        # Higher bass = more particles spawning
        # Higher speed = even more particles spawning
        base_spawn_rate = 0.5 + bass_level * 3.0  # 0.5-3.5 particles per frame based on bass
        spawn_rate = base_spawn_rate * (1.0 + speed_factor)  # Speed multiplies the spawn rate

        for _ in range(int(spawn_rate)):
            if len(self.particles) < self.particle_count * 2:  # Limit max particles
                self.particles.append(self._spawn_new_particle())

    def _draw_particles(self, frame):
        """Draw circular particles with life fading"""
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
        """Draw bass level indicator on screen"""
        raw_bass_level = self._get_bass_level_at_frame(frame_idx)
        enhanced_bass_level = self._apply_enhanced_mode(raw_bass_level)

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
            text = "HIGH BASS - INCREASED SNOWFLAKE FLOW"
        else:
            # Low bass - blue color
            color = (255, 0, 0)  # Blue
            text = "LOW BASS - NORMAL SNOWFLAKE FLOW"

        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + level_width, bar_y + bar_height), color, -1)

        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 0.6, 2)[0]
        text_x = (self.W - text_size[0]) // 2
        text_y = bar_y + bar_height + 30
        cv2.putText(frame, text, (text_x, text_y), font, 0.6, color, 2)

        # Add enhanced mode indicator
        if self.enhanced_mode.get("active", False) and raw_bass_level >= self.enhanced_mode.get("threshold", 0.3):
            enhanced_text = f"ENHANCED! (x{self.enhanced_mode.get('factor', 2.0)})"
            enhanced_text_size = cv2.getTextSize(enhanced_text, font, 0.5, 2)[0]
            enhanced_text_x = (self.W - enhanced_text_size[0]) // 2
            enhanced_text_y = text_y + 25
            cv2.putText(frame, enhanced_text, (enhanced_text_x, enhanced_text_y), font, 0.5, (0, 255, 255), 2)

        # Add bass level percentages (raw and enhanced)
        level_text = f"Raw: {raw_bass_level:.2f} ({raw_bass_level*100:.0f}%) | Enhanced: {enhanced_bass_level:.2f} ({enhanced_bass_level*100:.0f}%)"
        level_text_size = cv2.getTextSize(level_text, font, 0.4, 1)[0]
        level_text_x = (self.W - level_text_size[0]) // 2
        level_text_y = text_y + 50
        cv2.putText(frame, level_text, (level_text_x, level_text_y), font, 0.4, (255, 255, 255), 1)

        return frame

    def render_particles_test(self, output_path, audio_path=None):
        """Render particles test on black background with optional audio"""
        start_time = time.time()
        print("🚀 Starting Trap Nation particles test render...")

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
                print(f"Progress: {int(100 * i / total_frames)}% | Elapsed: {elapsed:.1f}s | FPS: {fps_actual:.1f}")

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
        print("📊 TRAP NATION PARTICLES TEST PERFORMANCE")
        print("="*60)
        print(f"🎬 Frame rendering:      {render_time:6.3f}s ({render_time/total_time*100:5.1f}%)")
        print(f"📝 Video writer setup:   {writer_time:6.3f}s ({writer_time/total_time*100:5.1f}%)")
        print(f"📁 File operations:      {finalize_time:6.3f}s ({finalize_time/total_time*100:5.1f}%)")
        print("-"*60)
        print(f"⏱️  Total time:           {total_time:6.3f}s")
        print(f"🎬 Video duration:       {self.duration:6.1f}s")
        print(f"⚡ Speed ratio:          {realtime_ratio:6.2f}x realtime")
        print(f"🎯 Avg FPS:              {total_frames/total_time:6.1f} fps")
        print(f"✨ Particle count:       {self.particle_count}")
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
    Test function to create a music-dependent snowflake particles video with bass-triggered respawning
    """
    OUTPUT = "trap_nation_snowflake_particles_test.mp4"
    AUDIO = "song.wav"

    # Create snowflake particles visualizer with music-dependent settings
    particles = TrapNationParticles(
        width=1920,
        height=1080,
        fps=30,
        x_position=0.5,
        y_position=0.5,
        particle_count=50,  # Base particle count (continuous spawning will add more)
        duration=15.0,  # 15 seconds test
        bass_threshold=0.3,  # Bass threshold for respawn triggering
        outer_movement_strength=2.0,  # Strength of outward movement during bass
        inner_movement_strength=1.0,  # Not used in snowflake mode
    )

    # Render the test with audio
    particles.render_particles_test(OUTPUT, audio_path=AUDIO)

    print(f"\n❄️ Trap Nation snowflake particles test completed!")
    print(f"📹 Output video: {OUTPUT}")
    print(f"🎵 Audio source: {AUDIO}")
    print(f"✨ Features:")
    print(f"   - Outward movement: spawn from center → move outward → fade with distance")
    print(f"   - Bass-triggered respawning: particles respawn when bass hits threshold")
    print(f"   - Higher bass intensity = higher respawn probability and more new particles")
    print(f"   - Speed-responsive appearance: faster particles = higher spawn rate and respawn chance")
    print(f"   - Snowflake cross pattern rendering")
    print(f"   - Bass-responsive flow intensity (threshold: {particles.bass_threshold})")
    print(f"   - Distance-based fading effects")
    print(f"   - Enhanced Mode: {particles.enhanced_mode}")
    print(f"   - {particles.duration}s duration at {particles.fps} FPS")


if __name__ == "__main__":
    test_trap_nation_particles()
