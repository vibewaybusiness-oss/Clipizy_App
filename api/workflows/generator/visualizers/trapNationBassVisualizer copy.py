# trap_nation_bass_visualizer.py
import os
import shutil
import subprocess
import time

import cv2
import librosa
import numpy as np

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy import VideoFileClip
    except ImportError:
        VideoFileClip = None


class TrapNationBassVisualizer:
    """
    Trap Nation inspired bass visualizer with green circle:
    - Central filled black circle with frequency visualizer
    - Green frequency-based circle with proper mirroring
    - Circular waveform around the circle
    - Logo cutout in center with cityscape background
    """

    def __init__(
        self,
        width=1920,
        height=1080,
        fps=30,
        circle_min_radius=60,
        circle_max_radius=120,
        x_position=0.5,
        y_position=0.5,
        logo_scale_factor=1.0,
        logo_scale_to_circle=True,
        fadein=3.0,
        fadeout=0.0,
        delay_outro=0.0,
        time_in=0.0,
        duration_intro=0.0,
        bass_bins=5,
        smoothing=60,
        wave_amplitude=30,
        wave_frequency=8,
        outline_thickness=8,
        energy_intensity=0.8,
        enhanced_mode=None,
        scale_factor=1.0,
        waveform_scale_factor=1.2,
    ):
        self.W = width
        self.H = height
        self.fps = int(fps)
        self.cmin = int(circle_min_radius)
        self.cmax = int(circle_max_radius)

        # Position
        self.x_pos = float(x_position)
        self.y_pos = float(y_position)
        self.cx = int(self.W * self.x_pos)
        self.cy = int(self.H * self.y_pos)

        # Logo settings
        self.logo_scale = float(logo_scale_factor)
        self.logo_scale_to_circle = bool(logo_scale_to_circle)

        # Timing
        self.fadein = float(fadein)
        self.fadeout = float(fadeout)
        self.delay_outro = float(delay_outro)
        self.time_in = float(time_in)
        self.duration_intro = float(duration_intro)

        # Audio processing
        self.bass_bins = int(bass_bins)
        self.smoothing = max(0, min(100, int(smoothing)))

        # Visual effects
        self.wave_amplitude = int(wave_amplitude)
        self.wave_frequency = int(wave_frequency)
        self.outline_thickness = int(outline_thickness)
        self.energy_intensity = float(energy_intensity)

        # Enhanced mode
        self.enhanced_mode = enhanced_mode

        # Circle scaling parameters
        self.waveform_scale_factor = float(waveform_scale_factor)

        # Frame history for anti-flickering
        self.frame_history = []
        self.max_history = 3

        # Circle configuration with colors and scale factors (BGR format)
        # First in list = top z-index, last = bottom z-index
        self.circles = {
            'white': {'color': (255, 255, 255), 'scale': 1.0},      # Top layer
            'green': {'color': (0, 255, 0), 'scale': 1.12},        # Second layer
            'pink': {'color': (203, 192, 255), 'scale': 1.24},     # Third layer
            'blue': {'color': (255, 0, 0), 'scale': 1.36},        # Fourth layer
            'white_outer': {'color': (255, 255, 255), 'scale': 1.55}  # Bottom layer
        }

        # Keep colors list for frequency bands compatibility
        self.colors = [
            (0, 255, 0),      # Green (outermost)
            (255, 0, 0),      # Blue
            (255, 255, 0),    # Cyan
            (255, 0, 255),    # Magenta
            (0, 0, 255),      # Red
            (0, 255, 255),    # Yellow
            (255, 255, 255),  # White (innermost)
        ]

        # Pre-compute constants
        self.radius_range = self.cmax - self.cmin
        self.ease_power = 1.4

        # Pre-allocate black frame
        self.black_frame = np.zeros((self.H, self.W, 3), dtype=np.uint8)

        # Logo cache
        self._logo_cache = None
        self._logo_alpha_cache = None
        self._logo_size_cache = None


    def _apply_enhanced_mode(self, frequency_bands, circle_min_radius, circle_max_radius, height):
        """Apply enhanced mode processing to frequency bands based on radius increase threshold"""
        if not self.enhanced_mode or not self.enhanced_mode.get("active", False):
            return frequency_bands

        # Get enhanced mode parameters with defaults
        threshold = self.enhanced_mode.get("threshold", 0.3)
        factor = self.enhanced_mode.get("factor", 2.0)

        # Calculate radius range
        min_radius = circle_min_radius
        max_radius = circle_max_radius
        radius_range = max_radius - min_radius

        # Calculate threshold in terms of radius increase
        radius_threshold = radius_range * threshold

        # Apply threshold and enhancement based on radius increase
        enhanced_bands = frequency_bands.copy()
        for i in range(len(enhanced_bands)):
            # Calculate current radius increase
            current_radius_increase = enhanced_bands[i] * radius_range

            if current_radius_increase >= radius_threshold:
                # Apply enhancement factor to values above threshold
                enhanced_bands[i] = min(1.0, enhanced_bands[i] * factor)
            else:
                # Keep values below threshold as they are (stand in place)
                enhanced_bands[i] = enhanced_bands[i]

        return enhanced_bands

    def _apply_enhanced_mode_smooth(self, frequency_bands, frame_idx):
        """Apply enhanced mode processing with anti-flickering smoothing"""
        if not self.enhanced_mode or not self.enhanced_mode.get("active", False):
            return frequency_bands

        # Get enhanced mode parameters with defaults
        threshold = self.enhanced_mode.get("threshold", 0.3)
        factor = self.enhanced_mode.get("factor", 2.0)

        # Calculate radius range
        min_radius = self.cmin
        max_radius = self.cmax
        radius_range = max_radius - min_radius

        # Calculate threshold in terms of radius increase
        radius_threshold = radius_range * threshold

        # Add current frame to history
        self.frame_history.append(frequency_bands.copy())
        if len(self.frame_history) > self.max_history:
            self.frame_history.pop(0)

        # Apply enhanced mode with frame history smoothing
        enhanced_bands = frequency_bands.copy()

        for i in range(len(enhanced_bands)):
            # Calculate current radius increase
            current_radius_increase = enhanced_bands[i] * radius_range

            if current_radius_increase >= radius_threshold:
                # Apply enhancement factor
                enhanced_value = min(1.0, enhanced_bands[i] * factor)

                # Apply frame history smoothing to reduce flickering
                if len(self.frame_history) > 1:
                    # Use moving average of last few frames for smoother transitions
                    history_values = [frame[i] for frame in self.frame_history[:-1]]  # Exclude current frame
                    if history_values:
                        avg_history = np.mean(history_values)
                        # Blend enhanced value with historical average
                        smoothing_factor = 0.7  # 70% enhanced, 30% historical
                        enhanced_bands[i] = smoothing_factor * enhanced_value + (1 - smoothing_factor) * avg_history
                    else:
                        enhanced_bands[i] = enhanced_value
                else:
                    enhanced_bands[i] = enhanced_value
            else:
                # Keep values below threshold as they are (stand in place)
                enhanced_bands[i] = enhanced_bands[i]

        return enhanced_bands


    def render(self, audio_path, output_path, logo_path=None, background_video_path=None):
        """Render the Trap Nation style visualizer"""
        start_time = time.time()
        print("🚀 Starting Trap Nation visualizer render...")

        # Background setup
        bg_start = time.time()
        bg = self._open_background(background_video_path)
        bg_time = time.time() - bg_start
        print(f"📹 Background setup: {bg_time:.3f}s")

        # Logo loading
        logo_start = time.time()
        if logo_path:
            logo = self._load_logo(logo_path)
            self._preprocess_logo(logo)
        else:
            logo = None
        logo_time = time.time() - logo_start
        print(f"🖼️ Logo loading: {logo_time:.3f}s")

        # Audio processing
        audio_start = time.time()
        frequency_bands, total_frames, duration = self._compute_frequency_bands(audio_path)
        audio_time = time.time() - audio_start
        print(f"🎵 Audio processing: {audio_time:.3f}s ({total_frames} frames, {duration:.1f}s duration)")

        # Video writer
        writer_start = time.time()
        tmp_out = output_path + ".temp.mp4"
        self._ensure_dir(os.path.dirname(output_path))
        writer = cv2.VideoWriter(tmp_out, cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (self.W, self.H))
        if not writer.isOpened():
            raise RuntimeError("Failed to open video writer")
        writer_time = time.time() - writer_start
        print(f"📝 Video writer setup: {writer_time:.3f}s")

        # Pre-compute opacity values
        precompute_start = time.time()
        opacity_values = self._compute_opacity_vectorized(total_frames)
        frame_times = np.arange(total_frames, dtype=np.float32) / self.fps
        precompute_time = time.time() - precompute_start
        print(f"⚡ Pre-computations: {precompute_time:.3f}s")

        # Initialize smoothing for each frequency band
        prev_frequencies = [0.0] * len(self.colors)

        # Performance tracking
        bg_time_total = 0
        visualizer_time_total = 0
        logo_time_total = 0
        write_time_total = 0

        # Main rendering loop
        render_start = time.time()
        for i in range(total_frames):
            t = frame_times[i]

            # Background
            bg_start = time.time()
            frame = self._get_background_frame(bg, t)
            bg_time_total += time.time() - bg_start

            # Opacity check
            opacity = opacity_values[i]
            if opacity <= 0:
                write_start = time.time()
                writer.write(frame)
                write_time_total += time.time() - write_start
                continue

            # Apply smoothing to each frequency band first (before enhanced mode)
            current_frequencies = frequency_bands[i] * opacity
            smoothed_frequencies = []

            for j, freq in enumerate(current_frequencies):
                freq = min(1.0, max(0.0, freq))
                if self.smoothing > 0:
                    alpha = 0.9 - (self.smoothing / 100.0) * 0.8
                    if i == 0:
                        smoothed_freq = freq
                    else:
                        smoothed_freq = alpha * freq + (1 - alpha) * prev_frequencies[j]
                    prev_frequencies[j] = smoothed_freq
                else:
                    smoothed_freq = freq
                smoothed_frequencies.append(smoothed_freq)

            # Apply enhanced mode processing after smoothing to reduce flickering
            enhanced_frequencies = self._apply_enhanced_mode_smooth(smoothed_frequencies, i)

            # Draw visualizer
            visualizer_start = time.time()
            frame = self._draw_trap_nation_visualizer(frame, enhanced_frequencies, t)
            visualizer_time_total += time.time() - visualizer_start

            # Logo cutout
            if logo is not None:
                logo_start = time.time()
                frame = self._apply_logo_cutout(frame, logo, i, bg)
                logo_time_total += time.time() - logo_start

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
        if bg is not None:
            bg.close()

        # Finalize
        finalize_start = time.time()
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(tmp_out, output_path)
        finalize_time = time.time() - finalize_start
        print(f"📁 File operations: {finalize_time:.3f}s")

        # Audio muxing
        audio_mux_start = time.time()
        self._mux_audio(output_path, audio_path)
        audio_mux_time = time.time() - audio_mux_start
        print(f"🔊 Audio muxing: {audio_mux_time:.3f}s")

        # Performance summary
        total_time = time.time() - start_time
        realtime_ratio = duration / total_time if total_time > 0 else 0

        print("\n" + "="*60)
        print("📊 TRAP NATION VISUALIZER PERFORMANCE")
        print("="*60)
        print(f"🎵 Audio processing:     {audio_time:6.3f}s ({audio_time/total_time*100:5.1f}%)")
        print(f"⚡ Pre-computations:     {precompute_time:6.3f}s ({precompute_time/total_time*100:5.1f}%)")
        print(f"🎬 Frame rendering:      {render_time:6.3f}s ({render_time/total_time*100:5.1f}%)")
        print(f"📝 Video writer setup:   {writer_time:6.3f}s ({writer_time/total_time*100:5.1f}%)")
        print(f"📁 File operations:      {finalize_time:6.3f}s ({finalize_time/total_time*100:5.1f}%)")
        print(f"🔊 Audio muxing:         {audio_mux_time:6.3f}s ({audio_mux_time/total_time*100:5.1f}%)")
        print(f"📹 Background setup:     {bg_time:6.3f}s ({bg_time/total_time*100:5.1f}%)")
        print(f"🖼️ Logo loading:         {logo_time:6.3f}s ({logo_time/total_time*100:5.1f}%)")
        print("-"*60)
        print(f"⏱️  Total time:           {total_time:6.3f}s")
        print(f"🎬 Video duration:       {duration:6.1f}s")
        print(f"⚡ Speed ratio:          {realtime_ratio:6.2f}x realtime")
        print(f"🎯 Avg FPS:              {total_frames/total_time:6.1f} fps")
        print("="*60)
        print(f"✅ Done: {output_path}")

    def _draw_trap_nation_visualizer(self, frame, frequency_bands, t):
        """Draw the simplified visualizer with multiple circles and waveform"""
        # Keep core circle static - no scaling or enhanced mode applied
        r_core = self.cmin
        self.r_core = r_core

        # Draw multiple circles in reverse order (bottom to top)
        # Bottom layer first, top layer last (before black circle)
        circle_order = ['white_outer', 'blue', 'pink', 'green', 'white']

        for circle_name in circle_order:
            circle_config = self.circles[circle_name]
            frame = self._draw_frequency_circle(frame, r_core, frequency_bands, circle_config)

        # Draw waveform around the circles (left half + mirrored right half)
        frame = self._draw_circular_waveform(frame, r_core, frequency_bands, t)

        # Draw central black circle on top (always last)
        frame = self._draw_central_logo_area(frame, r_core, frequency_bands)

        return frame


    def _draw_circular_waveform(self, frame, r_core, frequency_bands, t):
        """Draw perfectly circular waveform around the circle using circle radius as x-axis, left half mirrored to right"""
        # Use the circle radius as the x-axis for waveform positioning with circle scale factor
        waveform_radius = r_core * self.waveform_scale_factor  # Position waveform outside the green circle

        # Create many more credits for perfectly smooth circular waveform
        num_credits = 360  # 360 credits for smooth circle (1 degree per point)
        angles = np.linspace(0, 2 * np.pi, num_credits)

        # Create waveform based on frequency bands - interpolate to match num_credits
        freq_interpolated = np.interp(np.linspace(0, 1, num_credits),
                                    np.linspace(0, 1, len(frequency_bands)),
                                    frequency_bands)

        # Create waveform offsets for smooth circular motion
        waveform_offsets = []
        for i, freq_strength in enumerate(freq_interpolated):
            # Scale the frequency strength to create waveform amplitude
            amplitude = 15 + freq_strength * 25  # Base amplitude + frequency response
            # Add smooth wave motion
            wave_motion = 3 * np.sin(t * 3 + i * 0.1)
            waveform_offsets.append(amplitude + wave_motion)

        # Create left half waveform (from -π/2 to π/2)
        left_angles = angles[(num_credits//4):(3*num_credits//4)]  # -π/2 to π/2
        left_offsets = waveform_offsets[(num_credits//4):(3*num_credits//4)]

        # Convert to cartesian coordinates for left half
        left_x = []
        left_y = []
        for angle, offset in zip(left_angles, left_offsets):
            radius = waveform_radius + offset
            x = self.cx + radius * np.cos(angle)
            y = self.cy + radius * np.sin(angle)
            left_x.append(x)
            left_y.append(y)

        # Mirror the waveform for right half (from π/2 to 3π/2)
        right_angles = np.concatenate([
            angles[(3*num_credits//4):],  # π/2 to 2π
            angles[:num_credits//4]       # 0 to π/2
        ])
        right_offsets = np.concatenate([
            left_offsets[::-1],  # Reverse the left offsets
            left_offsets[::-1]   # Repeat for the 0 to π/2 section
        ])

        right_x = []
        right_y = []
        for angle, offset in zip(right_angles, right_offsets):
            radius = waveform_radius + offset
            x = self.cx + radius * np.cos(angle)
            y = self.cy + radius * np.sin(angle)
            right_x.append(x)
            right_y.append(y)

        # Combine left and right halves
        all_x = left_x + right_x
        all_y = left_y + right_y

        # Draw the waveform as connected lines with anti-aliasing
        credits = np.column_stack((all_x, all_y)).astype(np.int32)

        # Color based on overall energy
        overall_energy = sum(frequency_bands) / len(frequency_bands)
        intensity = int(255 * (0.6 + overall_energy * 0.4))
        color = (intensity, intensity // 2, intensity // 3)  # Warm color

        # Draw the waveform with smooth lines
        for i in range(len(credits) - 1):
            cv2.line(frame, tuple(credits[i]), tuple(credits[i + 1]), color, 2, lineType=cv2.LINE_AA)

        # Close the circle smoothly
        cv2.line(frame, tuple(credits[-1]), tuple(credits[0]), color, 2, lineType=cv2.LINE_AA)

        return frame

    def _draw_colorful_outline(self, frame, r_core, frequency_bands, t):
        """Draw frequency-based waves that always cover the entire frequency span in half circle"""
        # Calculate dynamic thickness based on overall energy
        overall_energy = sum(frequency_bands) / len(frequency_bands)
        thickness = self.outline_thickness + int(overall_energy * 4)

        # Draw each color layer - always visible, covering entire frequency span
        for i, (color, freq_strength) in enumerate(zip(self.colors, frequency_bands)):
            # Calculate wave radius - always visible with frequency-based expansion
            base_radius = r_core + (i + 1) * 15  # Spacing between waves
            wave_radius = base_radius + int(freq_strength * 40)  # Expand based on frequency strength

            # Add energy pulse effect
            energy_pulse = 1.0 + 0.3 * np.sin(t * 4 + i * np.pi/3) * freq_strength
            final_radius = int(wave_radius * energy_pulse)

            # Draw symmetric wave pattern (half circle + mirrored half) - always visible
            if i == len(self.colors) - 1:  # Innermost white layer - filled
                cv2.circle(frame, (self.cx, self.cy), int(final_radius), color, thickness=-1, lineType=cv2.LINE_AA)
            else:  # Other layers - symmetric wave outline
                self._draw_symmetric_wave_outline(frame, final_radius, color, thickness, freq_strength, t, i)

        return frame

    def _draw_symmetric_wave_outline(self, frame, radius, color, thickness, freq_strength, t, layer_index):
        """Draw symmetric wave outline - left half with mirrored right half (Y-axis symmetry)"""
        # Create wave pattern for left half circle (-π/2 to π/2)
        num_credits = 64
        angles = np.linspace(-np.pi/2, np.pi/2, num_credits)

        # Create wave pattern based on frequency strength and time - always visible
        wave_amplitude = 10 + freq_strength * 15  # Always have some amplitude
        wave_phase = t * 3 + layer_index * np.pi/4

        # Add multiple wave harmonics for more complex pattern
        wave_offset = 0
        for harmonic in range(1, 4):  # 3 harmonics
            harmonic_amp = wave_amplitude / harmonic
            harmonic_freq = 2 + layer_index * 0.5  # Fixed frequency, no wave_frequency dependency
            harmonic_phase = wave_phase + harmonic * np.pi/3
            wave_offset += harmonic_amp * np.sin(angles * harmonic_freq + harmonic_phase) * (0.3 + 0.7 * freq_strength) / harmonic

        # Add some randomness for organic feel
        noise_factor = 0.2 * freq_strength
        noise = noise_factor * np.sin(angles * 5 + t * 6) * np.sin(angles * 8 + t * 4)
        wave_offset += noise

        # Ensure minimum visibility
        min_offset = 5
        wave_offset = np.maximum(wave_offset, min_offset * freq_strength)

        left_radii = radius + wave_offset

        # Convert to cartesian coordinates for left half
        left_x = self.cx + left_radii * np.cos(angles)
        left_y = self.cy + left_radii * np.sin(angles)

        # Mirror the pattern for right half (π/2 to 3π/2)
        right_angles = np.linspace(np.pi/2, 3*np.pi/2, num_credits)
        right_radii = radius + wave_offset[::-1]  # Reverse the wave pattern
        right_x = self.cx + right_radii * np.cos(right_angles)
        right_y = self.cy + right_radii * np.sin(right_angles)

        # Combine left and right halves
        all_x = np.concatenate([left_x, right_x])
        all_y = np.concatenate([left_y, right_y])

        # Draw the symmetric wave outline
        credits = np.column_stack((all_x, all_y)).astype(np.int32)

        # Draw as connected line segments with varying thickness
        for i in range(len(credits) - 1):
            # Vary thickness based on wave amplitude
            current_thickness = max(1, int(thickness * (0.8 + 0.2 * abs(wave_offset[i % len(wave_offset)]) / wave_amplitude)))
            cv2.line(frame, tuple(credits[i]), tuple(credits[i + 1]), color, current_thickness, lineType=cv2.LINE_AA)

        # Close the circle by connecting last point to first
        cv2.line(frame, tuple(credits[-1]), tuple(credits[0]), color, thickness, lineType=cv2.LINE_AA)

    def _add_jagged_effect(self, radius, freq_strength, t, layer_index):
        """Add jagged/dripping effect to circle edges"""
        # Create jagged pattern based on frequency strength and time
        jagged_factor = 0.1 + freq_strength * 0.2
        frequency = 2 + layer_index * 0.5

        # Generate jagged credits around the circle
        num_credits = 64
        angles = np.linspace(0, 2 * np.pi, num_credits)
        jagged_radius = radius * (1 + jagged_factor * np.sin(angles * frequency + t * 4))

        return np.mean(jagged_radius)  # Return average for circle drawing

    def _draw_sound_waves(self, frame, r_core, overall_energy, t):
        """Draw integrated sound wave patterns around the main element with Y-axis symmetric patterns"""
        # Calculate wave parameters based on overall energy - always visible
        wave_amp = 20 + overall_energy * 30  # Always have some amplitude

        # Draw multiple wave rings with Y-axis symmetric patterns
        for ring in range(3):
            ring_radius = r_core + 40 + ring * 30
            ring_amp = wave_amp * (1.0 - ring * 0.2)

            # Generate Y-axis symmetric wave pattern
            num_credits = 120
            angles = np.linspace(-np.pi/2, np.pi/2, num_credits // 2)

            # Create wave pattern for left half - always visible
            wave_freq = 2 + ring * 0.5  # Fixed frequency, no wave_frequency dependency
            wave_offset = ring_amp * np.sin(angles * wave_freq + t * 4 + ring * np.pi/4)
            left_radii = ring_radius + wave_offset

            # Convert to cartesian coordinates for left half
            left_x = self.cx + left_radii * np.cos(angles)
            left_y = self.cy + left_radii * np.sin(angles)

            # Mirror the pattern for right half
            right_angles = np.linspace(np.pi/2, 3*np.pi/2, num_credits // 2)
            right_radii = ring_radius + wave_offset[::-1]  # Reverse the wave pattern
            right_x = self.cx + right_radii * np.cos(right_angles)
            right_y = self.cy + right_radii * np.sin(right_angles)

            # Combine left and right halves
            all_x = np.concatenate([left_x, right_x])
            all_y = np.concatenate([left_y, right_y])

            # Draw wave as connected credits
            credits = np.column_stack((all_x, all_y)).astype(np.int32)

            # Color based on ring and energy
            intensity = int(255 * (0.7 + overall_energy * 0.3))
            color = (intensity, intensity // 2, intensity // 3)  # Warm color

            # Draw the Y-axis symmetric wave
            for i in range(len(credits) - 1):
                cv2.line(frame, tuple(credits[i]), tuple(credits[i + 1]), color, 2, lineType=cv2.LINE_AA)

            # Close the circle
            cv2.line(frame, tuple(credits[-1]), tuple(credits[0]), color, 2, lineType=cv2.LINE_AA)

        return frame

    def _draw_frequency_circle(self, frame, base_radius, frequency_bands, circle_config):
        """Draw a single frequency-based circle with given color and scale factor"""
        # Create many credits for smooth circular visualization
        num_credits = 360  # 360 credits for smooth circle (1 degree per point)
        angles = np.linspace(0, 2 * np.pi, num_credits)

        # Map frequency bands to angular positions
        # Bass (0) -> π/2, Mid (3) -> π, High (6) -> 3π/2
        freq_angles = [
            np.pi/2,      # Bass at π/2 (top)
            np.pi/2 + np.pi/6,  # Low-mid
            np.pi/2 + np.pi/3,  # Mid-low
            np.pi,        # Mid at π (left)
            np.pi + np.pi/6,    # Mid-high
            np.pi + np.pi/3,    # High-mid
            3*np.pi/2     # High at 3π/2 (bottom)
        ]

        # Apply enhanced mode and scaling to frequency bands
        enhanced_frequency_bands = self._apply_enhanced_mode_smooth(frequency_bands, 0)

        # Create frequency-based radius offsets
        radius_offsets = np.zeros(num_credits)

        for i, (freq_strength, target_angle) in enumerate(zip(enhanced_frequency_bands, freq_angles)):
            # Calculate distance from each angle to the target frequency angle
            angle_diff = np.abs(angles - target_angle)
            # Handle wraparound at 2π
            angle_diff = np.minimum(angle_diff, 2*np.pi - angle_diff)

            # Create Gaussian-like distribution around the target angle
            sigma = np.pi/10  # Width of the frequency band
            weight = np.exp(-(angle_diff**2) / (2 * sigma**2))

            # Scale by frequency strength and circle scale factor (only affects growth, not base radius)
            base_amplitude = 0
            scaled_amplitude = (self.radius_range - self.r_core)  * circle_config['scale']
            radius_offsets += weight * scaled_amplitude

        # Create perfect Y-axis symmetry by mirroring the left half to the right half
        # Left half: π/2 to 3π/2 (top to bottom, left side)
        # Right half: 3π/2 to π/2 (bottom to top, right side) - mirrored

        # Create left half pattern (π/2 to 3π/2)
        left_mask = (angles >= np.pi/2) & (angles <= 3*np.pi/2)
        left_angles = angles[left_mask]
        left_offsets = radius_offsets[left_mask]

        # Create right half by mirroring left half across Y-axis
        # For each right angle, find its mirrored left angle
        right_angles = []
        right_offsets = []

        # Generate right half angles (3π/2 to 2π, then 0 to π/2)
        right_angle_range = np.concatenate([
            np.linspace(3*np.pi/2, 2*np.pi, len(left_angles)//2),  # 3π/2 to 2π
            np.linspace(0, np.pi/2, len(left_angles) - len(left_angles)//2)  # 0 to π/2
        ])

        for right_angle in right_angle_range:
            # Mirror across Y-axis: right_angle -> π - right_angle (but handle wraparound)
            if right_angle <= np.pi/2:
                # 0 to π/2 maps to π/2 to π
                mirrored_angle = np.pi/2 + (np.pi/2 - right_angle)
            else:
                # 3π/2 to 2π maps to π to 3π/2
                mirrored_angle = np.pi + (2*np.pi - right_angle)

            # Find closest left angle and use its offset
            closest_idx = np.argmin(np.abs(left_angles - mirrored_angle))
            right_angles.append(right_angle)
            right_offsets.append(left_offsets[closest_idx])

        right_angles = np.array(right_angles)
        right_offsets = np.array(right_offsets)

        # Combine left and right halves
        all_angles = np.concatenate([left_angles, right_angles])
        all_offsets = np.concatenate([left_offsets, right_offsets])

        # Sort by angle for proper drawing order
        sort_indices = np.argsort(all_angles)
        all_angles = all_angles[sort_indices]
        all_offsets = all_offsets[sort_indices]

        # Calculate final radii - same base radius for all circles, only growth differs
        final_radii = base_radius + all_offsets

        # Convert to cartesian coordinates
        x_coords = self.cx + final_radii * np.cos(all_angles)
        y_coords = self.cy + final_radii * np.sin(all_angles)

        # Draw the frequency-based circle as connected credits
        credits = np.column_stack((x_coords, y_coords)).astype(np.int32)

        # Use the circle's defined color
        color = circle_config['color']

        # Draw the frequency-based circle as filled polygon
        cv2.fillPoly(frame, [credits], color, lineType=cv2.LINE_AA)

        return frame

    def _draw_central_logo_area(self, frame, r_core, frequency_bands):
        """Draw the central black circle area for logo placement"""
        # Draw filled black circle on top
        cv2.circle(frame, (self.cx, self.cy), r_core, (0, 0, 0), thickness=-1, lineType=cv2.LINE_AA)

        return frame



    def _open_background(self, video_path):
        """Open background video if provided"""
        if not video_path or VideoFileClip is None:
            return None
        try:
            clip = VideoFileClip(video_path)
            return clip
        except Exception as e:
            print(f"⚠️ Failed to open background video: {e}")
            return None

    def _get_background_frame(self, bg, t):
        """Get background frame at time t"""
        if bg is None:
            return self.black_frame.copy()

        try:
            t_clamped = min(max(0.0, t), max(0.0, bg.duration - 1e-3))
            img = bg.get_frame(t_clamped)

            if img.dtype != np.uint8:
                img = (np.clip(img, 0.0, 1.0) * 255).astype(np.uint8)

            img = img[:, :, ::-1]  # RGB -> BGR

            if img.shape[:2] != (self.H, self.W):
                img = cv2.resize(img, (self.W, self.H), interpolation=cv2.INTER_AREA)

            return img
        except Exception:
            return self.black_frame.copy()

    def _compute_frequency_bands(self, audio_path):
        """Compute frequency band values for each frame - each band corresponds to a color ring"""
        y, sr = librosa.load(audio_path, sr=None, mono=True)

        if self.duration_intro > 0:
            start = int(self.duration_intro * sr)
            y = y[start:]

        duration = len(y) / sr
        total_frames = max(1, int(duration * self.fps))
        samples_per_frame = max(1, int(sr / self.fps))

        window = np.hanning(samples_per_frame).astype(np.float32)
        num_bands = len(self.colors)
        frequency_bands = np.zeros((total_frames, num_bands), dtype=np.float32)

        # Define frequency ranges for each band (from low to high frequencies)
        # Each band covers a different frequency range
        band_ranges = [
            (0, 60),      # Green - Sub-bass (0-60 Hz)
            (60, 250),    # Blue - Bass (60-250 Hz)
            (250, 500),   # Cyan - Low-mid (250-500 Hz)
            (500, 2000),  # Magenta - Mid (500-2000 Hz)
            (2000, 4000), # Red - High-mid (2000-4000 Hz)
            (4000, 8000), # Yellow - High (4000-8000 Hz)
            (8000, sr//2) # White - Very high (8000+ Hz)
        ]

        for i in range(total_frames):
            start_idx = i * samples_per_frame
            end_idx = min(start_idx + samples_per_frame, len(y))

            if start_idx >= len(y):
                frequency_bands[i] = 0.0
                continue

            segment = y[start_idx:end_idx].astype(np.float32)
            if len(segment) < samples_per_frame:
                segment = np.pad(segment, (0, samples_per_frame - len(segment)), mode="constant")

            segment_windowed = segment * window
            spec = np.fft.rfft(segment_windowed)
            mag = np.abs(spec)

            # Convert frequency bins to Hz
            freqs = np.fft.rfftfreq(samples_per_frame, 1/sr)

            # Calculate energy for each frequency band
            for band_idx, (low_freq, high_freq) in enumerate(band_ranges):
                # Find frequency bins in this range
                freq_mask = (freqs >= low_freq) & (freqs <= high_freq)
                if np.any(freq_mask):
                    band_energy = np.mean(mag[freq_mask])
                else:
                    band_energy = 0.0

                frequency_bands[i, band_idx] = band_energy

            # Normalize each frame
            max_energy = np.max(frequency_bands[i])
            if max_energy > 0:
                frequency_bands[i] = frequency_bands[i] / max_energy

        # Apply smoothing to each band
        if self.smoothing > 0:
            for band_idx in range(num_bands):
                frequency_bands[:, band_idx] = self._apply_smoothing(frequency_bands[:, band_idx])

        return frequency_bands, total_frames, duration

    def _apply_smoothing(self, bass_series):
        """Apply smoothing to bass series"""
        if self.smoothing == 0 or len(bass_series) < 3:
            return bass_series

        smooth_factor = self.smoothing / 100.0
        alpha = 0.9 - (smooth_factor * 0.8)
        alpha = max(0.01, min(0.9, alpha))

        smoothed = np.zeros_like(bass_series)
        smoothed[0] = bass_series[0]

        for i in range(1, len(bass_series)):
            smoothed[i] = alpha * bass_series[i] + (1 - alpha) * smoothed[i-1]

        return np.clip(smoothed, 0.0, 1.0)

    def _compute_opacity_vectorized(self, total_frames):
        """Compute opacity for all frames"""
        fi = int(self.fadein * self.fps)
        fo = int(self.fadeout * self.fps)
        do = int(self.delay_outro * self.fps)
        start = int(self.time_in * self.fps)
        end = max(0, total_frames - fo - do)

        i = np.arange(total_frames, dtype=np.float32)
        opacity = np.zeros(total_frames, dtype=np.float32)

        before_start = i < start
        opacity[before_start] = 0.0

        if fi > 0:
            fadein_mask = (i >= start) & (i < start + fi)
            opacity[fadein_mask] = (i[fadein_mask] - start) / fi

        full_mask = (i >= start + fi) & (i < end)
        opacity[full_mask] = 1.0

        if fo > 0:
            fadeout_mask = i >= end
            opacity[fadeout_mask] = np.maximum(0.0, 1.0 - (i[fadeout_mask] - end) / max(1, fo))

        return opacity

    def _preprocess_logo(self, logo_rgba):
        """Preprocess logo for optimal performance"""
        if logo_rgba is None:
            return

        if self.logo_scale_to_circle:
            target = int(self.cmin * 1.6 * self.logo_scale)
        else:
            target = 120

        if target <= 0:
            return

        h0, w0 = logo_rgba.shape[:2]
        aspect = w0 / max(1, h0)
        if aspect >= 1:
            w = target
            h = int(w / aspect)
        else:
            h = target
            w = int(h * aspect)

        if w <= 0 or h <= 0:
            return

        logo = cv2.resize(logo_rgba, (w, h), interpolation=cv2.INTER_AREA)

        if logo.shape[2] == 4:
            alpha = logo[:, :, 3].astype(np.float32) / 255.0
        else:
            gray = cv2.cvtColor(logo[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.float32)
            alpha = gray / 255.0
            alpha = np.clip((alpha - 0.1) / 0.8, 0.0, 1.0)

        alpha = cv2.GaussianBlur(alpha, (3, 3), 0.5)

        self._logo_cache = logo
        self._logo_alpha_cache = alpha
        self._logo_size_cache = (w, h)

    def _apply_logo_cutout(self, frame, logo_rgba, frame_idx, bg_clip):
        """Apply logo cutout effect"""
        if self._logo_cache is None or self._logo_alpha_cache is None or self._logo_size_cache is None:
            return frame

        w, h = self._logo_size_cache
        alpha = self._logo_alpha_cache

        x0 = int(self.cx - w // 2)
        y0 = int(self.cy - h // 2)

        x0_clamp = max(0, min(x0, self.W - w))
        y0_clamp = max(0, min(y0, self.H - h))
        w_clamp = min(w, self.W - x0_clamp)
        h_clamp = min(h, self.H - y0_clamp)
        if w_clamp <= 0 or h_clamp <= 0:
            return frame

        roi = frame[y0_clamp:y0_clamp + h_clamp, x0_clamp:x0_clamp + w_clamp].copy()
        alpha_roi = alpha[:h_clamp, :w_clamp]

        if bg_clip is not None:
            t = frame_idx / self.fps
            bg_img = self._get_background_frame(bg_clip, t)
            bg_roi = bg_img[y0_clamp:y0_clamp + h_clamp, x0_clamp:x0_clamp + w_clamp]

            alpha_3d = np.stack([alpha_roi] * 3, axis=2)
            roi = (1.0 - alpha_3d) * roi.astype(np.float32) + alpha_3d * bg_roi.astype(np.float32)
            roi = np.clip(roi, 0, 255).astype(np.uint8)
        else:
            alpha_3d = np.stack([alpha_roi] * 3, axis=2)
            roi = (1.0 - alpha_3d) * roi.astype(np.float32)
            roi = np.clip(roi, 0, 255).astype(np.uint8)

        frame[y0_clamp:y0_clamp + h_clamp, x0_clamp:x0_clamp + w_clamp] = roi
        return frame

    @staticmethod
    def _ensure_dir(d):
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)

    @staticmethod
    def _load_logo(path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Logo not found: {path}")
        return img

    @staticmethod
    def _mux_audio(video_path, audio_path):
        """Mux audio into video using ffmpeg"""
        temp_out = video_path + ".with_audio.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "320k",
            "-map", "0:v:0", "-map", "1:a:0",
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


if __name__ == "__main__":
    """
    Example usage of Trap Nation Bass Visualizer
    """
    AUDIO = "song.wav"
    OUTPUT = "trap_nation_visualizer.mp4"
    LOGO = "logo.png"
    BACKGROUND = "background.mp4"

    visualizer = TrapNationBassVisualizer(
        width=1920,
        height=1080,
        fps=30,
        circle_min_radius=80,
        circle_max_radius=140,
        x_position=0.5,
        y_position=0.5,
        logo_scale_factor=1.2,
        logo_scale_to_circle=True,
        fadein=3.0,
        fadeout=1.0,
        bass_bins=5,
        smoothing=80,
        wave_amplitude=60,
        wave_frequency=0,
        outline_thickness=10,
        energy_intensity=0.8,
        enhanced_mode={"active": True, "threshold": 0.5, "factor": 2.0},
        scale_factor=1.50,
        waveform_scale_factor=1.2,
    )

    visualizer.render(AUDIO, OUTPUT, logo_path=LOGO, background_video_path=BACKGROUND)
