# bass_logo_visualizer.py
import math
import os
import shutil
import subprocess
import time

import cv2
import librosa
import numpy as np
from moviepy import VideoFileClip


class BassCircleLogoVisualizer:
    """
    Minimal visualizer: bass-reactive circles + center logo cutout.
    - Background: optional video (resized to output WH). If absent, black frames.
    - Bass: mean of first few FFT bins per frame.
    - Colors: BGR tuples (OpenCV).
    - Spacing: configurable gaps and spacing between circles.
    - Smoothing: 0-100% scale for smoothing and anti-flickering.
    """

    def __init__(
        self,
        width=1920,
        height=1080,
        fps=30,
        circle_min_radius=40,
        circle_max_radius=80,
        circle_color_primary=(255, 50, 255),   # BGR (magenta-ish)
        circle_color_secondary=(50, 200, 255), # BGR (yellow-ish)
        color=None,            # Single color override (BGR tuple) - overrides primary/secondary
        x_position=0.5,        # X position as fraction of width (0.0=left, 0.5=center, 1.0=right)
        y_position=0.5,        # Y position as fraction of height (0.0=top, 0.5=center, 1.0=bottom)
        logo_scale_factor=1.0,
        logo_fixed_size=120,  # Fixed logo size in pixels (width/height) - DEPRECATED
        logo_scale_to_circle=True,  # Scale logo to minimum circle radius
        fadein=3.0,
        fadeout=0.0,
        delay_outro=0.0,
        time_in=0.0,
        duration_intro=0.0,
        bass_bins=3,          # avg of first N FFT bins
        smoothing=50,         # Smoothing and anti-flickering: 0-100 (0=raw, 100=very smooth)
        initial_gap=20,       # Initial gap between core and first outer ring
        max_gap=60,           # Maximum gap between core and outer rings
        outer_ring_spacing=15, # Spacing between outer rings
    ):
        self.W = width
        self.H = height
        self.fps = int(fps)
        self.cmin = int(circle_min_radius)
        self.cmax = int(circle_max_radius)

        # Handle color argument - if provided, use it for both primary and secondary
        if color is not None:
            self.cpri = color
            self.csec = color
        else:
            self.cpri = circle_color_primary
            self.csec = circle_color_secondary

        # Handle position arguments - convert fractions to pixel coordinates
        self.x_pos = float(x_position)
        self.y_pos = float(y_position)
        self.cx = int(self.W * self.x_pos)
        self.cy = int(self.H * self.y_pos)

        self.logo_scale = float(logo_scale_factor)
        self.logo_fixed_size = int(logo_fixed_size)
        self.logo_scale_to_circle = bool(logo_scale_to_circle)
        self.fadein = float(fadein)
        self.fadeout = float(fadeout)
        self.delay_outro = float(delay_outro)
        self.time_in = float(time_in)
        self.duration_intro = float(duration_intro)
        self.bass_bins = int(bass_bins)
        self.smoothing = max(0, min(100, int(smoothing)))
        self.initial_gap = int(initial_gap)
        self.max_gap = int(max_gap)
        self.outer_ring_spacing = int(outer_ring_spacing)

        # Pre-compute constants for performance
        self.radius_range = self.cmax - self.cmin
        self.golden = 1.618
        self.ease_power = 1.3
        self.core_cap = int(self.cmin * 1.3)

        # Pre-compute color interpolation constants
        self.color_diffs = np.array([
            self.csec[0] - self.cpri[0],
            self.csec[1] - self.cpri[1],
            self.csec[2] - self.cpri[2]
        ], dtype=np.float32)

        # Pre-compute outer ring spacing calculations
        self.gap_range = self.max_gap - self.initial_gap
        self.ring_spacings = np.array([
            self.outer_ring_spacing,
            self.outer_ring_spacing * 2,
            self.outer_ring_spacing * 3
        ], dtype=np.float32)

        # Pre-allocate black frame for background
        self.black_frame = np.zeros((self.H, self.W, 3), dtype=np.uint8)

        # Logo processing cache for performance
        self._logo_cache = None
        self._logo_alpha_cache = None
        self._logo_size_cache = None

    # ---------------------------
    # Public API
    # ---------------------------
    def render(self, audio_path, output_path, logo_path=None, background_video_path=None):
        """
        Render the bass circle + logo cutout visualizer with performance timing.
        """
        start_time = time.time()
        print("🚀 Starting visualizer render...")

        # --- background video (optional) ---
        bg_start = time.time()
        bg = self._open_background(background_video_path)
        bg_time = time.time() - bg_start
        print(f"📹 Background setup: {bg_time:.3f}s")

        # --- load and preprocess logo (optional) ---
        logo_start = time.time()
        if logo_path:
            logo = self._load_logo(logo_path)
            self._preprocess_logo(logo)
        else:
            logo = None
        logo_time = time.time() - logo_start
        print(f"🖼️ Logo loading: {logo_time:.3f}s")

        # --- compute per-frame bass values and total frames ---
        audio_start = time.time()
        bass_series, total_frames, duration = self._compute_bass_series(audio_path)
        audio_time = time.time() - audio_start
        print(f"🎵 Audio processing: {audio_time:.3f}s ({total_frames} frames, {duration:.1f}s duration)")

        # --- writer ---
        writer_start = time.time()
        tmp_out = output_path + ".temp.mp4"
        self._ensure_dir(os.path.dirname(output_path))
        writer = cv2.VideoWriter(tmp_out, cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (self.W, self.H))
        if not writer.isOpened():
            raise RuntimeError("Failed to open video writer")
        writer_time = time.time() - writer_start
        print(f"📝 Video writer setup: {writer_time:.3f}s")

        # --- main loop ---
        render_start = time.time()

        # Pre-compute opacity values for all frames (vectorized)
        precompute_start = time.time()
        opacity_values = self._compute_opacity_vectorized(total_frames)

        # Pre-compute frame times
        frame_times = np.arange(total_frames, dtype=np.float32) / self.fps
        precompute_time = time.time() - precompute_start
        print(f"⚡ Pre-computations: {precompute_time:.3f}s")

        # Initialize smoothing variables
        prev_outer_bass = 0.0

        # Performance tracking
        bg_time_total = 0
        circles_time_total = 0
        logo_time_total = 0
        write_time_total = 0

        for i in range(total_frames):
            t = frame_times[i]

            # Background frame timing
            bg_start = time.time()
            frame = self._get_background_frame(bg, t)
            bg_time_total += time.time() - bg_start

            # Fast opacity check
            opacity = opacity_values[i]
            if opacity <= 0:
                write_start = time.time()
                writer.write(frame)
                write_time_total += time.time() - write_start
                continue

            # Apply additional smoothing for outer rings if smoothing is enabled
            bass = min(1.0, max(0.0, bass_series[i])) * opacity

            if self.smoothing > 0:
                # Apply additional smoothing for outer rings (50% of main smoothing)
                outer_smooth_factor = (self.smoothing / 100.0) * 0.5
                if i == 0:
                    outer_bass = bass
                else:
                    alpha_outer = 0.9 - (outer_smooth_factor * 0.8)  # 0.9 to 0.1
                    outer_bass = alpha_outer * bass + (1 - alpha_outer) * prev_outer_bass
                prev_outer_bass = outer_bass
            else:
                outer_bass = bass  # Use same value when no smoothing

            # draw circles timing
            circles_start = time.time()
            frame = self._draw_bass_circles(frame, bass, outer_bass)
            circles_time_total += time.time() - circles_start

            # logo cutout timing
            if logo is not None:
                logo_start = time.time()
                frame = self._apply_logo_cutout(frame, logo, i, bg)
                logo_time_total += time.time() - logo_start

            # Write timing
            write_start = time.time()
            writer.write(frame)
            write_time_total += time.time() - write_start

            # Optimized progress reporting with timing
            if total_frames > 0 and i % max(1, total_frames // 10) == 0:
                elapsed = time.time() - render_start
                fps_actual = (i + 1) / elapsed if elapsed > 0 else 0
                print(f"Progress: {int(100 * i / total_frames)}% | Elapsed: {elapsed:.1f}s | FPS: {fps_actual:.1f}")

        render_time = time.time() - render_start
        print(f"🎬 Frame rendering: {render_time:.3f}s ({render_time/total_frames*1000:.1f}ms per frame)")

        writer.release()
        if bg is not None:
            bg.close()

        # finalize temp -> output
        finalize_start = time.time()
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(tmp_out, output_path)
        finalize_time = time.time() - finalize_start
        print(f"📁 File operations: {finalize_time:.3f}s")

        # mux original audio
        audio_mux_start = time.time()
        self._mux_audio(output_path, audio_path)
        audio_mux_time = time.time() - audio_mux_start
        print(f"🔊 Audio muxing: {audio_mux_time:.3f}s")

        # Final performance summary
        total_time = time.time() - start_time
        realtime_ratio = duration / total_time if total_time > 0 else 0

        print("\n" + "="*60)
        print("📊 PERFORMANCE SUMMARY")
        print("="*60)
        print(f"🎵 Audio processing:     {audio_time:6.3f}s ({audio_time/total_time*100:5.1f}%)")
        print(f"⚡ Pre-computations:     {precompute_time:6.3f}s ({precompute_time/total_time*100:5.1f}%)")
        print(f"🎬 Frame rendering:      {render_time:6.3f}s ({render_time/total_time*100:5.1f}%)")
        print(f"📝 Video writer setup:   {writer_time:6.3f}s ({writer_time/total_time*100:5.1f}%)")
        print(f"📁 File operations:      {finalize_time:6.3f}s ({finalize_time/total_time*100:5.1f}%)")
        print(f"🔊 Audio muxing:         {audio_mux_time:6.3f}s ({audio_mux_time/total_time*100:5.1f}%)")
        print(f"📹 Background setup:     {bg_time:6.3f}s ({bg_time/total_time*100:5.1f}%)")
        print(f"🖼️ Logo loading:         {logo_time:6.3f}s ({logo_time/total_time*100:5.1f}%)")
        print(f"🌊 Smoothing level:      {self.smoothing:6d}% (includes anti-flicker)")
        print("-"*60)
        print("🔍 DETAILED FRAME TIMING:")
        print(f"📹 Background frames:    {bg_time_total:6.3f}s ({bg_time_total/total_time*100:5.1f}%)")
        print(f"⭕ Circle drawing:       {circles_time_total:6.3f}s ({circles_time_total/total_time*100:5.1f}%)")
        print(f"🖼️ Logo cutout:          {logo_time_total:6.3f}s ({logo_time_total/total_time*100:5.1f}%)")
        print(f"💾 Video writing:        {write_time_total:6.3f}s ({write_time_total/total_time*100:5.1f}%)")
        print("-"*60)
        print(f"⏱️  Total time:           {total_time:6.3f}s")
        print(f"🎬 Video duration:       {duration:6.1f}s")
        print(f"⚡ Speed ratio:          {realtime_ratio:6.2f}x realtime")
        print(f"🎯 Avg FPS:              {total_frames/total_time:6.1f} fps")
        print("="*60)
        print(f"✅ Done: {output_path}")

    # ---------------------------
    # Background / frames
    # ---------------------------
    def _open_background(self, video_path):
        if not video_path:
            return None
        try:
            clip = VideoFileClip(video_path)
            # If background is shorter than audio, we still sample safely by clamping time.
            # Resize on each frame fetch is costly; we fetch then resize via cv2.
            return clip
        except Exception as e:
            print(f"⚠️ Failed to open background video: {e}")
            return None

    def _get_background_frame(self, bg, t):
        """
        Highly optimized background frame retrieval with caching.
        """
        if bg is None:
            return self.black_frame.copy()

        try:
            # Fast time clamping
            t_clamped = min(max(0.0, t), max(0.0, bg.duration - 1e-3))
            img = bg.get_frame(t_clamped)

            # Fast type conversion and color space conversion
            if img.dtype != np.uint8:
                img = (np.clip(img, 0.0, 1.0) * 255).astype(np.uint8)

            # RGB -> BGR (vectorized)
            img = img[:, :, ::-1]

            # Resize only if necessary
            if img.shape[:2] != (self.H, self.W):
                img = cv2.resize(img, (self.W, self.H), interpolation=cv2.INTER_AREA)

            return img
        except Exception:
            return self.black_frame.copy()

    # ---------------------------
    # Audio / Bass series
    # ---------------------------
    def _compute_bass_series(self, audio_path):
        """
        Highly optimized bass computation using vectorized batch processing.
        Returns (bass_series[0..N-1], N, duration_s).
        """
        load_start = time.time()
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        load_time = time.time() - load_start

        # skip intro seconds if requested
        if self.duration_intro > 0:
            start = int(self.duration_intro * sr)
            y = y[start:]

        duration = len(y) / sr
        total_frames = max(1, int(duration * self.fps))
        samples_per_frame = max(1, int(sr / self.fps))

        # Pre-compute window once
        window_start = time.time()
        window = np.hanning(samples_per_frame).astype(np.float32)
        window_time = time.time() - window_start

        # Pre-allocate arrays
        bass_vals = np.zeros(total_frames, dtype=np.float32)

        # Use larger chunks for better vectorization
        chunk_size = min(2000, total_frames)  # Increased chunk size

        fft_start = time.time()

        # Pre-compute all segment indices for vectorized processing
        segment_indices = np.arange(total_frames) * samples_per_frame
        segment_ends = np.minimum(segment_indices + samples_per_frame, len(y))

        for chunk_start in range(0, total_frames, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_frames)
            chunk_size_actual = chunk_end - chunk_start

            # Vectorized segment extraction
            seg_starts = segment_indices[chunk_start:chunk_end]
            seg_ends = segment_ends[chunk_start:chunk_end]

            # Process all segments in the chunk at once
            chunk_vals = np.zeros(chunk_size_actual, dtype=np.float32)

            for i, (s, e) in enumerate(zip(seg_starts, seg_ends)):
                if s >= len(y):
                    chunk_vals[i] = 0.0
                    continue

                # Extract segment
                seg = y[s:e].astype(np.float32)

                # Pad if necessary (vectorized)
                if len(seg) < samples_per_frame:
                    seg = np.pad(seg, (0, samples_per_frame - len(seg)), mode="constant")

                # Apply window and compute FFT (vectorized)
                seg_windowed = seg * window
                spec = np.fft.rfft(seg_windowed)
                mag = np.abs(spec)

                # Fast normalization using numpy operations
                maxmag = mag.max()
                if maxmag < 1e-6:
                    norm = mag
                else:
                    norm = mag / maxmag

                # Bass calculation (vectorized)
                bins = min(self.bass_bins + 1, len(norm))
                if bins <= 1:
                    bass = 0.0
                else:
                    bass = float(np.mean(norm[1:bins]))

                chunk_vals[i] = bass

            # Store chunk results
            bass_vals[chunk_start:chunk_end] = chunk_vals

        fft_time = time.time() - fft_start

        # Final normalization (vectorized)
        norm_start = time.time()
        bass_vals = np.clip(bass_vals, 0.0, 1.0)
        norm_time = time.time() - norm_start

        # Apply smoothing and anti-flickering
        smooth_start = time.time()
        if self.smoothing > 0:
            bass_vals = self._apply_smoothing_system(bass_vals)
        smooth_time = time.time() - smooth_start

        # Print detailed audio processing timing
        print(f"  📂 Audio loading: {load_time:.3f}s")
        print(f"  🪟 Window setup: {window_time:.3f}s")
        print(f"  🔢 FFT processing: {fft_time:.3f}s")
        print(f"  📊 Normalization: {norm_time:.3f}s")
        print(f"  🌊 Smoothing: {smooth_time:.3f}s (level={self.smoothing}%)")

        return bass_vals, total_frames, duration

    def _apply_smoothing_system(self, bass_series):
        """
        Comprehensive smoothing and anti-flickering system (0-100% scale).
        - 0%: Raw values, no smoothing
        - 1-50%: Light to moderate exponential smoothing
        - 51-80%: Strong smoothing with anti-flicker
        - 81-100%: Maximum smoothing with strong anti-flicker
        """
        if self.smoothing == 0:
            return bass_series

        if len(bass_series) < 3:
            return bass_series

        # Convert smoothing percentage to processing parameters
        smooth_factor = self.smoothing / 100.0

        # 1. Exponential smoothing (applies to all levels > 0)
        if smooth_factor <= 0.5:
            # Light to moderate smoothing (1-50%)
            alpha = 0.9 - (smooth_factor * 1.6)  # 0.9 to 0.1
        else:
            # Strong smoothing (51-100%)
            alpha = 0.1 - ((smooth_factor - 0.5) * 0.18)  # 0.1 to 0.01

        alpha = max(0.01, min(0.9, alpha))

        # Apply exponential smoothing
        smoothed = np.zeros_like(bass_series)
        smoothed[0] = bass_series[0]

        for i in range(1, len(bass_series)):
            smoothed[i] = alpha * bass_series[i] + (1 - alpha) * smoothed[i-1]

        # 2. Anti-flickering (applies to levels > 30%)
        if smooth_factor > 0.3:
            smoothed = self._apply_anti_flicker(smoothed, smooth_factor)

        # 3. Moving average for very high smoothing (81-100%)
        if smooth_factor > 0.8:
            window_size = max(3, int(len(bass_series) * 0.05))  # 5% of total frames
            if window_size % 2 == 0:
                window_size += 1

            # Apply moving average
            padded = np.pad(smoothed, window_size//2, mode='edge')
            smoothed = np.convolve(padded, np.ones(window_size)/window_size, mode='valid')

        return np.clip(smoothed, 0.0, 1.0)

    def _apply_anti_flicker(self, bass_series, smooth_factor):
        """
        Anti-flickering techniques based on smoothing level.
        """
        result = bass_series.copy()

        # 1. Minimum value thresholding (prevents complete disappearance)
        min_threshold = 0.005 + (smooth_factor * 0.025)  # 0.005 to 0.03
        result = np.maximum(result, min_threshold)

        # 2. Change rate limiting (prevents sudden jumps)
        max_change_rate = 0.4 - (smooth_factor * 0.35)  # 0.4 to 0.05
        for i in range(1, len(result)):
            change = result[i] - result[i-1]
            if abs(change) > max_change_rate:
                result[i] = result[i-1] + np.sign(change) * max_change_rate

        # 3. Temporal consistency (smooths rapid oscillations)
        if smooth_factor > 0.5:
            # Apply temporal smoothing kernel
            kernel_strength = (smooth_factor - 0.5) * 0.6  # 0.0 to 0.3
            kernel = np.array([0.2 * kernel_strength, 1.0 - 0.4 * kernel_strength, 0.2 * kernel_strength])
            kernel = kernel / np.sum(kernel)

            padded = np.pad(result, 1, mode='edge')
            result = np.convolve(padded, kernel, mode='valid')

        # 4. Peak preservation (maintains important bass hits)
        if smooth_factor < 0.7:  # Only for moderate smoothing
            # Detect significant peaks in original
            original_peaks = bass_series > (np.mean(bass_series) + 2 * np.std(bass_series))
            # Preserve original values at peaks
            result[original_peaks] = np.maximum(result[original_peaks], bass_series[original_peaks] * 0.8)

        return result

    # ---------------------------
    # Opacity / fades
    # ---------------------------
    def _compute_opacity_vectorized(self, total_frames):
        """
        Vectorized opacity computation for all frames at once.
        """
        fi = int(self.fadein * self.fps)
        fo = int(self.fadeout * self.fps)
        do = int(self.delay_outro * self.fps)
        start = int(self.time_in * self.fps)
        end = max(0, total_frames - fo - do)

        # Create frame indices
        i = np.arange(total_frames, dtype=np.float32)

        # Initialize opacity array
        opacity = np.zeros(total_frames, dtype=np.float32)

        # Before start: 0.0
        before_start = i < start
        opacity[before_start] = 0.0

        # Fade in
        if fi > 0:
            fadein_mask = (i >= start) & (i < start + fi)
            opacity[fadein_mask] = (i[fadein_mask] - start) / fi

        # Full opacity
        full_mask = (i >= start + fi) & (i < end)
        opacity[full_mask] = 1.0

        # Fade out
        if fo > 0:
            fadeout_mask = i >= end
            opacity[fadeout_mask] = np.maximum(0.0, 1.0 - (i[fadeout_mask] - end) / max(1, fo))

        return opacity

    def _opacity(self, i, total_frames):
        """
        Single frame opacity calculation (kept for compatibility).
        """
        fi = int(self.fadein * self.fps)
        fo = int(self.fadeout * self.fps)
        do = int(self.delay_outro * self.fps)
        start = int(self.time_in * self.fps)
        end = max(0, total_frames - fo - do)

        if i < start:
            return 0.0
        if fi > 0 and start <= i < start + fi:
            return (i - start) / fi
        if fo > 0 and i >= end:
            return max(0.0, 1.0 - (i - end) / max(1, fo))
        return 1.0

    # ---------------------------
    # Drawing
    # ---------------------------
    def _draw_bass_circles(self, frame, bass, outer_bass):
        """
        Highly optimized circle drawing with configurable spacing and gaps.
        """
        # Fast color interpolation using pre-computed differences
        t = min(1.0, max(0.0, bass))
        col = (
            int(round(self.cpri[0] + self.color_diffs[0] * t)),
            int(round(self.cpri[1] + self.color_diffs[1] * t)),
            int(round(self.cpri[2] + self.color_diffs[2] * t))
        )

        # Pre-compute eased values
        eased_core = bass ** self.ease_power
        eased_outer = outer_bass ** self.ease_power

        # Core circle radius (optimized calculation)
        r_core = min(self.core_cap, int(self.cmin + self.radius_range * eased_core))
        r_core = max(1, r_core)

        # Draw core circle
        cv2.circle(frame, (self.cx, self.cy), r_core, col, thickness=-1, lineType=cv2.LINE_AA)

        # Calculate dynamic gap between core and outer rings based on bass
        current_gap = self.initial_gap + self.gap_range * eased_outer

        # Draw outer rings with configurable spacing
        outer_radii = (r_core + current_gap + self.ring_spacings).astype(np.int32)
        outer_radii = np.maximum(1, outer_radii)

        # Draw all outer rings in one loop (optimized)
        for r in outer_radii:
            cv2.circle(frame, (self.cx, self.cy), r, col, thickness=1, lineType=cv2.LINE_AA)

        return frame

    def _preprocess_logo(self, logo_rgba):
        """
        Preprocess logo once for optimal performance during rendering.
        """
        if logo_rgba is None:
            return

        # Calculate logo size based on circle radius or fixed size
        if self.logo_scale_to_circle:
            # Scale logo to fit within the minimum circle radius
            # Use 80% of the minimum circle diameter to leave some margin
            target = int(self.cmin * 1.6 * self.logo_scale)  # 80% of diameter
        else:
            # Use fixed size
            target = self.logo_fixed_size

        if target <= 0:
            return

        # Calculate final dimensions
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

        # Use efficient interpolation for preprocessing
        logo = cv2.resize(logo_rgba, (w, h), interpolation=cv2.INTER_AREA)

        # Extract and preprocess alpha channel
        if logo.shape[2] == 4:
            alpha = logo[:, :, 3].astype(np.float32) / 255.0
        else:
            gray = cv2.cvtColor(logo[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.float32)
            alpha = gray / 255.0
            alpha = np.clip((alpha - 0.1) / 0.8, 0.0, 1.0)

        # Light anti-aliasing blur
        alpha = cv2.GaussianBlur(alpha, (3, 3), 0.5)

        # Cache the processed logo and alpha
        self._logo_cache = logo
        self._logo_alpha_cache = alpha
        self._logo_size_cache = (w, h)

    def _apply_logo_cutout(self, frame, logo_rgba, frame_idx, bg_clip):
        """
        Fast logo cutout using preprocessed cached data:
        - If background video available: replace masked pixels with background pixels at this time.
        - Else: replace with black (gives a hole look).
        """
        # Use cached preprocessed logo data
        if self._logo_cache is None or self._logo_alpha_cache is None or self._logo_size_cache is None:
            return frame

        w, h = self._logo_size_cache
        alpha = self._logo_alpha_cache

        # center placement
        x0 = int(self.cx - w // 2)
        y0 = int(self.cy - h // 2)

        # clamp ROI to frame
        x0_clamp = max(0, min(x0, self.W - w))
        y0_clamp = max(0, min(y0, self.H - h))
        w_clamp = min(w, self.W - x0_clamp)
        h_clamp = min(h, self.H - y0_clamp)
        if w_clamp <= 0 or h_clamp <= 0:
            return frame

        # region of interest in frame
        roi = frame[y0_clamp:y0_clamp + h_clamp, x0_clamp:x0_clamp + w_clamp].copy()
        alpha_roi = alpha[:h_clamp, :w_clamp]

        if bg_clip is not None:
            # fetch matching background frame for this visual frame index
            t = frame_idx / self.fps
            bg_img = self._get_background_frame(bg_clip, t)
            bg_roi = bg_img[y0_clamp:y0_clamp + h_clamp, x0_clamp:x0_clamp + w_clamp]

            # Fast alpha blending using vectorized operations
            alpha_3d = np.stack([alpha_roi] * 3, axis=2)
            roi = (1.0 - alpha_3d) * roi.astype(np.float32) + alpha_3d * bg_roi.astype(np.float32)
            roi = np.clip(roi, 0, 255).astype(np.uint8)
        else:
            # Replace with black using fast alpha blending
            alpha_3d = np.stack([alpha_roi] * 3, axis=2)
            roi = (1.0 - alpha_3d) * roi.astype(np.float32)
            roi = np.clip(roi, 0, 255).astype(np.uint8)

        frame[y0_clamp:y0_clamp + h_clamp, x0_clamp:x0_clamp + w_clamp] = roi
        return frame

    # ---------------------------
    # Utils
    # ---------------------------
    @staticmethod
    def _ensure_dir(d):
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)

    @staticmethod
    def _load_logo(path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)  # keep alpha if any
        if img is None:
            raise FileNotFoundError(f"Logo not found: {path}")
        return img


    @staticmethod
    def _mux_audio(video_path, audio_path):
        """
        Use ffmpeg to mux audio into the video (copy video, encode AAC audio).
        If ffmpeg missing or fails, keep the silent video.
        """
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
    Example:
    python bass_logo_visualizer.py
    """
    # quick demo values — change to your paths
    AUDIO = "song.wav"
    OUTPUT = "out_bass_logo.mp4"
    LOGO = "logo.png"                 # optional; supports alpha
    BACKGROUND = "background.mp4"     # optional

    vis = BassCircleLogoVisualizer(
        width=1280,
        height=720,
        fps=30,
        circle_min_radius=40,
        circle_max_radius=100,
        color=(0, 255, 0),          # Single color override (green BGR) - overrides primary/secondary
        # circle_color_primary=(255, 50, 255),   # magenta-ish (BGR) - ignored when color is set
        # circle_color_secondary=(50, 200, 255), # yellow-ish (BGR) - ignored when color is set
        x_position=0.5,             # X position as fraction of width (0.5 = center)
        y_position=0.5,             # Y position as fraction of height (0.5 = center)
        logo_scale_factor=1.2,      # Scale factor for logo relative to circle
        logo_scale_to_circle=True,  # Scale logo to minimum circle radius
        fadein=2.0,
        fadeout=0.5,
        delay_outro=0.0,
        time_in=0.0,
        duration_intro=0.0,
        bass_bins=3,
        smoothing=50,               # Smoothing and anti-flickering: 0-100 (0=raw, 100=very smooth)
        initial_gap=20,             # Initial gap between core and first outer ring
        max_gap=60,                 # Maximum gap between core and outer rings
        outer_ring_spacing=15,      # Spacing between outer rings
    )
    vis.render(AUDIO, OUTPUT, logo_path=LOGO, background_video_path=BACKGROUND)