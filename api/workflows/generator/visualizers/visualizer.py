import os
import shutil
import subprocess

import cv2
import librosa
import numpy as np
import torch
from moviepy import AudioFileClip, VideoFileClip
from pydub import AudioSegment


class logger:
    def __init__(self, name="Visualizer"):
        self.name = name

    def log(self, message):
        print(f"[{self.name}] {message}")

    def error(self, message):
        print(f"[{self.name}] ERROR: {message}")

    def warning(self, message):
        print(f"[{self.name}] WARNING: {message}")

    def info(self, message):
        print(f"[{self.name}] INFO: {message}")

class AudioVisualizerBase:
    def __init__(self, name="Visualizer"):
        self.logger = logger(name)
        self.temp_dir = None
        self.fade_params = {}
        self.visualizer_fps = 30
        self.time_in = 0.0

    # ----------------------------
    # High-level entry point
    # ----------------------------
    def render(self, audio_path, output_path, width=1920, height=1080,
               video_path=None, fps=30, n_segments=60,
               fadein=3, fadeout=3, delay_outro=0,
               duration_intro=0, time_in=0.0, draw_frame_fn=None,
               height_percent=10, width_percent=90,
               bar_thickness=None, bar_count=None, mirror_right=False,
               bar_height_min=10, bar_height_max=35, smoothness=0,
               x_position=50, y_position=50, color=(255, 50, 100),
               dot_size=None, dot_filled=True, transparency=True,
               top_active=True, bottom_active=True, fill_alpha=0.5, border_alpha=1.0, smooth_arcs=False, enhanced_mode=None):
        """
        Render a visualizer video.

        Args:
            audio_path: Path to audio file
            output_path: Final video output path
            width, height: Resolution
            video_path: Optional background video
            fps: Frames per second
            n_segments: FFT frequency bins
            fadein/fadeout: Fade durations
            delay_outro: Extra frames after fadeout
            duration_intro: Skip intro seconds in audio
            time_in: Time offset before visualizer appears
            draw_frame_fn: Callback to draw frame (style-specific)
            height_percent: Height as percentage of screen (1-100)
            width_percent: Width as percentage of screen (1-100)
            bar_thickness: Thickness of bars (None for auto-calculated)
            bar_count: Number of bars to display (None for auto-calculated)
            mirror_right: Mirror bars to the right side for symmetric effect
            bar_height_min: Minimum bar height as percentage of visualizer height (1-100)
            bar_height_max: Maximum bar height as percentage of visualizer height (1-100)
            smoothness: Smoothness level from 0-100 (0=no smoothness, 100=very smooth with anti-flickering)
            x_position: X position as percentage of screen width (0-100, 0=left edge, 100=right edge)
            y_position: Y position as percentage of screen height (0-100, 0=top edge, 100=bottom edge)
            color: RGB color tuple for the visualizer bars (B, G, R format for OpenCV)
            dot_size: Size of dots in pixels (None for auto-calculated based on bar_thickness)
            dot_filled: Whether to draw filled dots (True) or outline dots (False)
            transparency: Whether opacity should depend on audio values (True) or always be 1.0 (False)
            top_active: Whether to draw dots in the top half (True) or not (False)
            bottom_active: Whether to draw dots in the bottom half (True) or not (False)
            fill_alpha: Alpha value for filled area under the curve (0.0-1.0)
            border_alpha: Alpha value for the border/highest credits (0.0-1.0)
            smooth_arcs: Whether to use smooth curves instead of straight lines (True/False)
            enhanced_mode: Dict with enhanced waveform behavior settings
                - active: Whether enhanced mode is enabled (True/False)
                - threshold: Minimum value (0.0-1.0) required to trigger movement (default 0.3)
                - factor: Enhancement factor multiplier (default 2.0)
                Example: {"active": True, "threshold": 0.3, "factor": 2.0}
        """
        self.logger.log(f"Starting render for {audio_path}")
        self.visualizer_fps = fps
        self.time_in = time_in

        # Calculate visualizer dimensions as percentages of screen
        vis_width = int(width * width_percent / 100)
        vis_height = int(height * height_percent / 100)

        # Calculate position based on x_position and y_position parameters
        vis_x = int(width * x_position / 100) - vis_width // 2  # Center on x_position
        vis_y = int(height * y_position / 100) - vis_height // 2  # Center on y_position

        # Ensure visualizer stays within screen bounds
        vis_x = max(0, min(vis_x, width - vis_width))
        vis_y = max(0, min(vis_y, height - vis_height))

        # Set bar parameters with defaults
        if bar_count is None:
            bar_count = n_segments
        if bar_thickness is None:
            bar_thickness = max(1, int(vis_width / bar_count / 2))

        # Set dot parameters with defaults
        if dot_size is None:
            dot_size = max(1, bar_thickness)

        # Calculate smoothness factor (0-1)
        smoothness_factor = smoothness / 100.0

        # --- Prepare FFT data with improved smoothness ---
        y_sr, fft_data, duration, total_frames, _ = self._prepare_fft_data(
            audio_path, fps, n_segments, duration_intro,
            fadein, fadeout, delay_outro, smoothness_factor
        )

        # --- Background ---
        bg_video = self._load_background(video_path, duration, width, height)

        # --- Writer ---
        writer, temp_path = self._init_writer(output_path, fps, width, height)

        # Initialize smoothing buffers
        smoothing_buffer = None
        previous_values = None
        velocity_buffer = None
        moving_average_buffer = None

        # --- Frame loop ---
        for i in range(total_frames):
            frame = self._create_background_frame(bg_video, i / fps, width, height)
            opacity = self._calculate_opacity(i)

            if opacity > 0 and draw_frame_fn:
                values = fft_data[i].detach().cpu().numpy() * opacity
                # Limit values to bar_count if specified
                if bar_count < len(values):
                    values = values[:bar_count]
                elif bar_count > len(values):
                    # Pad with zeros if bar_count is larger
                    padded_values = np.zeros(bar_count)
                    padded_values[:len(values)] = values
                    values = padded_values

                # Apply frame-level smoothing based on smoothness level
                if smoothness_factor > 0:
                    values = self._apply_frame_smoothing(values, smoothness_factor, smoothing_buffer, previous_values, velocity_buffer, moving_average_buffer, i)
                    # Update buffers for next frame
                    if smoothing_buffer is None:
                        smoothing_buffer = values.copy()
                        previous_values = values.copy()
                        velocity_buffer = np.zeros_like(values)
                        moving_average_buffer = [values.copy()]
                    else:
                        smoothing_buffer = values.copy()
                        previous_values = values.copy()
                        if len(moving_average_buffer) >= 3:  # Keep last 3 frames for moving average (0.1s at 30fps)
                            moving_average_buffer.pop(0)
                        moving_average_buffer.append(values.copy())

                frame = draw_frame_fn(frame, values, i, fps, vis_width, vis_height, vis_x, vis_y, bar_thickness, mirror_right, bar_height_min, bar_height_max, height, width, x_position, y_position, color, dot_size, dot_filled, transparency, top_active, bottom_active, fill_alpha, border_alpha, smooth_arcs, enhanced_mode)

            writer.write(frame)

            if i % (total_frames // 10 or 1) == 0:
                self.logger.log(f"Progress: {100 * i // total_frames}%")

        writer.release()
        self._finalize_output(temp_path, output_path)
        self._add_audio(output_path, audio_path)

        if bg_video:
            bg_video.close()

        self.logger.log(f"✅ Render complete: {output_path}")
        return output_path

    # ----------------------------
    # Helpers: Audio/FFT
    # ----------------------------
    def _prepare_fft_data(self, audio_path, fps, n_segments,
                          duration_intro=0, fadein=3, fadeout=3, delay_outro=0, smoothness_factor=0.0):
        audio = AudioSegment.from_file(audio_path)
        if duration_intro > 0:
            audio = audio[duration_intro * 1000:]

        # Export to temp WAV for librosa
        if not self.temp_dir:
            self.temp_dir = os.path.join(os.path.dirname(audio_path), "temp_fft")
        os.makedirs(self.temp_dir, exist_ok=True)
        temp_wav = os.path.join(self.temp_dir, "audio_temp.wav")
        audio.export(temp_wav, format="wav")

        y, sr = librosa.load(temp_wav, sr=None)
        duration = len(y) / sr
        total_frames = int(duration * fps)
        samples_per_frame = int(sr / fps)

        # FFT processing with configurable smoothness
        y_tensor = torch.tensor(y, device="cpu")

        # Apply window function based on smoothness level
        if smoothness_factor > 0.3:  # Only apply window for higher smoothness values
            window = torch.hann_window(samples_per_frame)
        else:
            window = torch.ones(samples_per_frame)  # No window for maximum responsiveness

        # Process each frame individually
        fft_magnitude_list = []
        for i in range(total_frames):
            start_idx = i * samples_per_frame
            end_idx = start_idx + samples_per_frame

            if start_idx >= len(y_tensor):
                # Pad with zeros if beyond audio length
                frame_data = torch.zeros(samples_per_frame)
            else:
                frame_data = y_tensor[start_idx:end_idx]
                if len(frame_data) < samples_per_frame:
                    # Pad with zeros if frame is too short
                    pad_length = samples_per_frame - len(frame_data)
                    frame_data = torch.cat([frame_data, torch.zeros(pad_length)])

            # Apply window function
            frame_data = frame_data * window

            # Direct FFT on this frame
            fft_frame = torch.fft.rfft(frame_data)
            fft_mag = torch.abs(fft_frame[:n_segments // 2])

            fft_magnitude_list.append(fft_mag)

        fft_magnitude = torch.stack(fft_magnitude_list)

        # Apply FFT-level smoothing based on smoothness factor
        if smoothness_factor > 0.5:  # Only apply FFT smoothing for higher smoothness values
            smoothing_alpha = 0.1 + (0.3 * smoothness_factor)  # 0.1 to 0.4 range
            fft_magnitude = self._apply_smoothing_filter(fft_magnitude, alpha=smoothing_alpha)

        # Normalize each frequency band independently to its own maximum
        # This allows each bar to reach full height based on its own peak
        for freq_idx in range(fft_magnitude.shape[1]):
            freq_band = fft_magnitude[:, freq_idx]
            freq_max = torch.amax(freq_band)
            if freq_max > 0:
                fft_magnitude[:, freq_idx] = freq_band / freq_max

        mirrored = torch.cat([fft_magnitude, torch.flip(fft_magnitude, dims=[1])], dim=1)
        if mirrored.shape[1] != n_segments:
            mirrored = mirrored[:, :n_segments]

        self.fade_params = {
            "fadein_frames": int(fadein * fps),
            "fadeout_frames": int(fadeout * fps),
            "delay_outro_frames": int(delay_outro * fps),
            "total_frames": total_frames
        }
        return y, mirrored, duration, total_frames, samples_per_frame

    def _pad_or_slice(self, tensor, start, length):
        end = start + length
        if start >= len(tensor):
            return torch.zeros(length)
        segment = tensor[start:end]
        if len(segment) < length:
            pad = torch.zeros(length - len(segment))
            segment = torch.cat([segment, pad])
        return segment

    def _apply_smoothing_filter(self, fft_magnitude, alpha=0.3):
        """Apply exponential smoothing to reduce jitter between frames"""
        smoothed = torch.zeros_like(fft_magnitude)
        smoothed[0] = fft_magnitude[0]

        for i in range(1, len(fft_magnitude)):
            smoothed[i] = alpha * fft_magnitude[i] + (1 - alpha) * smoothed[i-1]

        return smoothed

    def _apply_frame_smoothing(self, values, smoothness_factor, smoothing_buffer, previous_values, velocity_buffer, moving_average_buffer, frame_idx):
        """Apply frame-level smoothing based on smoothness level (0-100%)"""
        if smoothing_buffer is None or previous_values is None:
            return values

        # Calculate velocity (change from previous frame)
        velocity = values - previous_values

        # Anti-flickering: limit maximum velocity change based on smoothness
        if smoothness_factor < 0.3:
            max_velocity = 0.3  # More controlled for low smoothness
        else:
            max_velocity = 0.1 + (0.2 * smoothness_factor)  # 0.1 to 0.3 range
        velocity = np.clip(velocity, -max_velocity, max_velocity)

        # Update velocity buffer with smoothing
        if velocity_buffer is not None:
            velocity_buffer = 0.5 * velocity_buffer + 0.5 * velocity  # More responsive
        else:
            velocity_buffer = velocity

        # Apply velocity-limited smoothing
        smoothed_values = previous_values + velocity_buffer

        # For high smoothness (60-100), use moving average
        if smoothness_factor >= 0.6 and moving_average_buffer is not None and len(moving_average_buffer) > 1:
            # Calculate moving average of last few frames
            moving_avg = np.mean(moving_average_buffer, axis=0)
            # Blend between smoothed values and moving average
            blend_factor = (smoothness_factor - 0.6) / 0.4  # 0 to 1 for smoothness 60-100
            smoothed_values = (1 - blend_factor) * smoothed_values + blend_factor * moving_avg

        # Final smoothing with exponential moving average
        if smoothness_factor < 0.3:
            smoothing_alpha = 0.5  # More controlled for low smoothness
        else:
            smoothing_alpha = 0.2 + (0.3 * smoothness_factor)  # 0.2 to 0.5 range
        final_values = (1 - smoothing_alpha) * smoothing_buffer + smoothing_alpha * smoothed_values

        return final_values

    # ----------------------------
    # Helpers: Background
    # ----------------------------
    def _load_background(self, video_path, duration, width, height):
        if not video_path:
            return None
        try:
            clip = VideoFileClip(video_path).subclip(0, duration).resize((width, height))
            return clip
        except Exception as e:
            self.logger.log(f"⚠️ Failed to load background video: {e}")
            return None

    def _create_background_frame(self, bg_video, t, width, height):
        if bg_video:
            try:
                frame = bg_video.get_frame(t)[:, :, ::-1].copy()
                return frame
            except Exception:
                pass
        return np.zeros((height, width, 3), dtype=np.uint8)

    # ----------------------------
    # Helpers: Fade/Opacity
    # ----------------------------
    def _calculate_opacity(self, frame_idx):
        fadein = self.fade_params["fadein_frames"]
        fadeout = self.fade_params["fadeout_frames"]
        total = self.fade_params["total_frames"]
        delay_outro = self.fade_params["delay_outro_frames"]

        start = int(self.time_in * self.visualizer_fps)
        end = total - fadeout - delay_outro

        if frame_idx < start:
            return 0.0
        if frame_idx < start + fadein:
            return (frame_idx - start) / fadein
        if frame_idx >= end:
            return max(0.0, 1 - (frame_idx - end) / fadeout)
        return 1.0

    # ----------------------------
    # Helpers: Writer
    # ----------------------------
    def _init_writer(self, output_path, fps, width, height):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        temp_path = output_path + ".temp.mp4"
        writer = cv2.VideoWriter(
            temp_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )
        if not writer.isOpened():
            raise RuntimeError("Failed to open video writer")
        return writer, temp_path

    def _finalize_output(self, temp_path, output_path):
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(temp_path, output_path)

    # ----------------------------
    # Helpers: Audio mux
    # ----------------------------
    def _add_audio(self, video_path, audio_path):
        temp_out = video_path + ".with_audio.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
            "-map", "0:v:0", "-map", "1:a:0",
            temp_out
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(temp_out):
            os.remove(video_path)
            shutil.move(temp_out, video_path)
            self.logger.log("🔊 Audio muxed into video")


# ----------------------------
# Example: Linear Bars Visualizer
# ----------------------------
class LinearBarsVisualizer(AudioVisualizerBase):
    def __init__(self):
        super().__init__("LinearBars")

    def _apply_enhanced_mode(self, values, enhanced_mode, bar_height_min, bar_height_max, total_height):
        """Apply enhanced mode processing to values based on height increase threshold"""
        if not enhanced_mode or not enhanced_mode.get("active", False):
            return values

        # Get enhanced mode parameters with defaults
        threshold = enhanced_mode.get("threshold", 0.3)
        factor = enhanced_mode.get("factor", 2.0)

        # Calculate height range
        min_height = int(total_height * bar_height_min / 100)
        max_height = int(total_height * bar_height_max / 100)
        height_range = max_height - min_height

        # Calculate threshold in terms of height increase
        height_threshold = height_range * threshold

        # Apply threshold and enhancement based on height increase
        enhanced_values = values.copy()
        for i in range(len(enhanced_values)):
            # Calculate current height increase
            current_height_increase = enhanced_values[i] * height_range

            if current_height_increase >= height_threshold:
                # Apply enhancement factor with gradual transition to reduce flickering
                enhanced_value = min(1.0, enhanced_values[i] * factor)

                # Gradual transition instead of sudden jump
                transition_factor = 0.8  # 80% new value, 20% old value for smoother transition
                enhanced_values[i] = transition_factor * enhanced_value + (1 - transition_factor) * enhanced_values[i]
            else:
                # Keep values below threshold as they are (stand in place)
                enhanced_values[i] = enhanced_values[i]

        return enhanced_values

    def draw_frame(self, frame, values, frame_idx, fps, vis_width, vis_height, vis_x, vis_y, bar_thickness, mirror_right=False, bar_height_min=10, bar_height_max=35, total_height=1080, total_width=1920, x_position=50, y_position=50, color=(255, 50, 100), dot_size=None, dot_filled=True, transparency=True, top_active=True, bottom_active=True, fill_alpha=0.5, border_alpha=1.0, smooth_arcs=False, enhanced_mode=None):
        # Apply enhanced mode processing to values
        values = self._apply_enhanced_mode(values, enhanced_mode, bar_height_min, bar_height_max, total_height)

        n_segments = len(values)
        # Use full video width for bar positioning, not just visualizer width
        margin = max(10, total_width // 20)  # Dynamic margin based on total video width
        usable_w = total_width - 2 * margin

        # Calculate center position based on y_position parameter
        center_y = int(total_height * y_position / 100)

        # Calculate bar height limits as percentages of total video height
        min_bar_h = int(total_height * bar_height_min / 100)
        max_bar_h = int(total_height * bar_height_max / 100)

        # Ensure bars can extend beyond visualizer boundaries
        # The visualizer band is just a reference area, bars can go outside it

        # Calculate the number of bars to draw on each side
        if mirror_right:
            bars_per_side = n_segments // 2
            # Use first half of values for left side
            left_values = values[:bars_per_side]
            # Mirror the left side values for right side
            right_values = values[:bars_per_side]
        else:
            bars_per_side = n_segments
            left_values = values
            right_values = []

        # Draw left side bars
        if len(left_values) > 0:
            # Calculate left side width (half of usable width when mirroring)
            left_width = usable_w // 2 if mirror_right else usable_w
            # Calculate starting x position based on x_position parameter
            start_x = int(total_width * x_position / 100) - left_width // 2
            for j in range(len(left_values)):
                amp = left_values[j]
                x = start_x + int((j / (len(left_values) - 1)) * left_width) if len(left_values) > 1 else start_x + left_width // 2
                # Calculate bar height using min/max limits
                bar_h = int(min_bar_h + amp * (max_bar_h - min_bar_h))
                top = int(center_y - bar_h/2)
                bottom = int(center_y + bar_h/2)

                # Draw bar with gradient effect for smoother appearance
                if transparency:
                    color_intensity = int(255 * amp)
                else:
                    color_intensity = 255  # Full opacity
                bar_color = (min(255, int(color[0] * (color_intensity + 50) / 255)),
                           min(255, int(color[1] * (color_intensity + 50) / 255)),
                           min(255, int(color[2] * (color_intensity + 50) / 255)))
                cv2.line(frame, (x, top), (x, bottom), bar_color, bar_thickness)

        # Draw right side bars (mirrored)
        if mirror_right and len(right_values) > 0:
            # Calculate right side width (half of usable width)
            right_width = usable_w // 2
            # Calculate starting x position for right side based on x_position parameter
            right_start_x = int(total_width * x_position / 100) + right_width // 2
            for j in range(len(right_values)):
                # Mirror the bar order - reverse the index
                mirror_j = len(right_values) - 1 - j
                amp = right_values[mirror_j]
                # Position bars in the right half, mirrored from left
                x = right_start_x + int((j / (len(right_values) - 1)) * right_width) if len(right_values) > 1 else right_start_x + right_width // 2
                # Calculate bar height using min/max limits
                bar_h = int(min_bar_h + amp * (max_bar_h - min_bar_h))
                top = int(center_y - bar_h/2)
                bottom = int(center_y + bar_h/2)

                # Draw bar with gradient effect for smoother appearance
                if transparency:
                    color_intensity = int(255 * amp)
                else:
                    color_intensity = 255  # Full opacity
                bar_color = (min(255, int(color[0] * (color_intensity + 50) / 255)),
                           min(255, int(color[1] * (color_intensity + 50) / 255)),
                           min(255, int(color[2] * (color_intensity + 50) / 255)))
                cv2.line(frame, (x, top), (x, bottom), bar_color, bar_thickness)

        return frame


# ----------------------------
# Linear Dots Visualizer
# ----------------------------
class LinearDotsVisualizer(AudioVisualizerBase):
    def __init__(self):
        super().__init__("LinearDots")

    def _apply_enhanced_mode(self, values, enhanced_mode, bar_height_min, bar_height_max, total_height):
        """Apply enhanced mode processing to values based on height increase threshold"""
        if not enhanced_mode or not enhanced_mode.get("active", False):
            return values

        # Get enhanced mode parameters with defaults
        threshold = enhanced_mode.get("threshold", 0.3)
        factor = enhanced_mode.get("factor", 2.0)

        # Calculate height range
        min_height = int(total_height * bar_height_min / 100)
        max_height = int(total_height * bar_height_max / 100)
        height_range = max_height - min_height

        # Calculate threshold in terms of height increase
        height_threshold = height_range * threshold

        # Apply threshold and enhancement based on height increase
        enhanced_values = values.copy()
        for i in range(len(enhanced_values)):
            # Calculate current height increase
            current_height_increase = enhanced_values[i] * height_range

            if current_height_increase >= height_threshold:
                # Apply enhancement factor with gradual transition to reduce flickering
                enhanced_value = min(1.0, enhanced_values[i] * factor)

                # Gradual transition instead of sudden jump
                transition_factor = 0.8  # 80% new value, 20% old value for smoother transition
                enhanced_values[i] = transition_factor * enhanced_value + (1 - transition_factor) * enhanced_values[i]
            else:
                # Keep values below threshold as they are (stand in place)
                enhanced_values[i] = enhanced_values[i]

        return enhanced_values

    def _draw_high_quality_dot(self, frame, x, y, radius, color, filled):
        """Draw a high-quality dot with anti-aliasing"""
        if filled:
            # For filled dots, use multiple circles with decreasing opacity for smooth edges
            for i in range(radius + 1):
                alpha = 1.0 - (i / (radius + 1)) * 0.3  # Gradual fade for smooth edges
                blended_color = tuple(int(c * alpha) for c in color)
                cv2.circle(frame, (x, y), radius - i, blended_color, -1)
        else:
            # For outline dots, draw multiple concentric circles for smooth edges
            thickness = max(2, radius // 3)
            for i in range(thickness):
                alpha = 1.0 - (i / thickness) * 0.2  # Slight fade for smooth edges
                blended_color = tuple(int(c * alpha) for c in color)
                cv2.circle(frame, (x, y), radius - i, blended_color, 1)

    def draw_frame(self, frame, values, frame_idx, fps, vis_width, vis_height, vis_x, vis_y, bar_thickness, mirror_right=False, bar_height_min=10, bar_height_max=35, total_height=1080, total_width=1920, x_position=50, y_position=50, color=(255, 50, 100), dot_size=None, dot_filled=True, transparency=True, top_active=True, bottom_active=True, fill_alpha=0.5, border_alpha=1.0, smooth_arcs=False, enhanced_mode=None):
        # Apply enhanced mode processing to values
        values = self._apply_enhanced_mode(values, enhanced_mode, bar_height_min, bar_height_max, total_height)

        n_segments = len(values)
        # Use full video width for dot positioning, not just visualizer width
        margin = max(10, total_width // 20)  # Dynamic margin based on total video width
        usable_w = total_width - 2 * margin

        # Calculate center position based on y_position parameter
        center_y = int(total_height * y_position / 100)

        # Calculate dot height limits as percentages of total video height
        min_dot_h = int(total_height * bar_height_min / 100)
        max_dot_h = int(total_height * bar_height_max / 100)

        # Set dot size with default
        if dot_size is None:
            dot_size = max(1, bar_thickness)

        # Calculate the number of dots to draw on each side
        if mirror_right:
            dots_per_side = n_segments // 2
            # Use first half of values for left side
            left_values = values[:dots_per_side]
            # Mirror the left side values for right side
            right_values = values[:dots_per_side]
        else:
            dots_per_side = n_segments
            left_values = values
            right_values = []

        # Draw left side dots
        if len(left_values) > 0:
            # Calculate left side width (half of usable width when mirroring)
            left_width = usable_w // 2 if mirror_right else usable_w
            # Calculate starting x position based on x_position parameter
            if mirror_right:
                # When mirroring, center the left side to the left of center
                center_x = int(total_width * x_position / 100)
                start_x = center_x - left_width
            else:
                # When not mirroring, center the full width
                start_x = int(total_width * x_position / 100) - left_width // 2
            for j in range(len(left_values)):
                amp = left_values[j]
                x = start_x + int((j / (len(left_values) - 1)) * left_width) if len(left_values) > 1 else start_x + left_width // 2
                # Calculate dot height using min/max limits
                dot_h = int(min_dot_h + amp * (max_dot_h - min_dot_h))
                top_y = int(center_y - dot_h/2)
                bottom_y = int(center_y + dot_h/2)

                # Draw dots with gradient effect for smoother appearance
                if transparency:
                    color_intensity = int(255 * amp)
                else:
                    color_intensity = 255  # Full opacity
                dot_color = (min(255, int(color[0] * (color_intensity + 50) / 255)),
                           min(255, int(color[1] * (color_intensity + 50) / 255)),
                           min(255, int(color[2] * (color_intensity + 50) / 255)))

                # Draw top dot with high quality (if active)
                if top_active:
                    self._draw_high_quality_dot(frame, x, top_y, dot_size, dot_color, dot_filled)
                # Draw bottom dot with high quality (if active)
                if bottom_active:
                    self._draw_high_quality_dot(frame, x, bottom_y, dot_size, dot_color, dot_filled)

        # Draw right side dots (mirrored)
        if mirror_right and len(right_values) > 0:
            # Calculate right side width (half of usable width)
            right_width = usable_w // 2
            # Calculate starting x position for right side based on x_position parameter
            center_x = int(total_width * x_position / 100)
            right_start_x = center_x
            for j in range(len(right_values)):
                # Mirror the dot order - reverse the index
                mirror_j = len(right_values) - 1 - j
                amp = right_values[mirror_j]
                # Position dots in the right half, mirrored from left
                x = right_start_x + int((j / (len(right_values) - 1)) * right_width) if len(right_values) > 1 else right_start_x + right_width // 2
                # Calculate dot height using min/max limits
                dot_h = int(min_dot_h + amp * (max_dot_h - min_dot_h))
                top_y = int(center_y - dot_h/2)
                bottom_y = int(center_y + dot_h/2)

                # Draw dots with gradient effect for smoother appearance
                if transparency:
                    color_intensity = int(255 * amp)
                else:
                    color_intensity = 255  # Full opacity
                dot_color = (min(255, int(color[0] * (color_intensity + 50) / 255)),
                           min(255, int(color[1] * (color_intensity + 50) / 255)),
                           min(255, int(color[2] * (color_intensity + 50) / 255)))

                # Draw top dot with high quality (if active)
                if top_active:
                    self._draw_high_quality_dot(frame, x, top_y, dot_size, dot_color, dot_filled)
                # Draw bottom dot with high quality (if active)
                if bottom_active:
                    self._draw_high_quality_dot(frame, x, bottom_y, dot_size, dot_color, dot_filled)

        return frame


# ----------------------------
# Waveform Visualizer
# ----------------------------
class WaveformVisualizer(AudioVisualizerBase):
    def __init__(self):
        super().__init__("Waveform")

    def _create_smooth_curve(self, credits, interpolation_factor=8):
        """Create smooth curves using cubic spline interpolation with better smoothing"""
        if len(credits) < 2:
            return credits

        if len(credits) == 2:
            # For just 2 credits, create a simple smooth interpolation
            x1, y1 = credits[0]
            x2, y2 = credits[1]
            smooth_credits = []

            for i in range(interpolation_factor + 1):
                t = i / interpolation_factor
                # Use smoothstep function for very smooth curves
                smooth_t = t * t * (3.0 - 2.0 * t)  # smoothstep function
                x = int(x1 + (x2 - x1) * smooth_t)
                y = int(y1 + (y2 - y1) * smooth_t)
                smooth_credits.append((x, y))

            return smooth_credits

        # For 3+ credits, use cubic spline interpolation
        x_coords = [p[0] for p in credits]
        y_coords = [p[1] for p in credits]

        # Create much more interpolated credits for ultra-smooth curves
        x_smooth = []
        y_smooth = []

        # Add first point
        x_smooth.append(credits[0][0])
        y_smooth.append(credits[0][1])

        for i in range(len(credits) - 1):
            x1, y1 = credits[i]
            x2, y2 = credits[i + 1]

            # Calculate control credits for cubic bezier-like smoothing
            if i > 0:
                # Use previous point for better continuity
                x0, y0 = credits[i - 1]
                # Control point 1: influenced by previous point
                cp1_x = x1 + (x1 - x0) * 0.2
                cp1_y = y1 + (y1 - y0) * 0.2
            else:
                cp1_x = x1
                cp1_y = y1

            if i < len(credits) - 2:
                # Use next point for better continuity
                x3, y3 = credits[i + 2]
                # Control point 2: influenced by next point
                cp2_x = x2 - (x3 - x2) * 0.2
                cp2_y = y2 - (y3 - y2) * 0.2
            else:
                cp2_x = x2
                cp2_y = y2

            # Create smooth cubic bezier interpolation
            for j in range(1, interpolation_factor + 1):
                t = j / interpolation_factor

                # Cubic bezier formula
                x_interp = int((1-t)**3 * x1 + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * x2)
                y_interp = int((1-t)**3 * y1 + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * y2)

                x_smooth.append(x_interp)
                y_smooth.append(y_interp)

        return list(zip(x_smooth, y_smooth))

    def _apply_enhanced_mode(self, values, enhanced_mode, bar_height_min, bar_height_max, total_height):
        """Apply enhanced mode processing to values based on height increase threshold"""
        if not enhanced_mode or not enhanced_mode.get("active", False):
            return values

        # Get enhanced mode parameters with defaults
        threshold = enhanced_mode.get("threshold", 0.3)
        factor = enhanced_mode.get("factor", 2.0)

        # Calculate height range
        min_height = int(total_height * bar_height_min / 100)
        max_height = int(total_height * bar_height_max / 100)
        height_range = max_height - min_height

        # Calculate threshold in terms of height increase
        height_threshold = height_range * threshold

        # Apply threshold and enhancement based on height increase
        enhanced_values = values.copy()
        for i in range(len(enhanced_values)):
            # Calculate current height increase
            current_height_increase = enhanced_values[i] * height_range

            if current_height_increase >= height_threshold:
                # Apply enhancement factor with gradual transition to reduce flickering
                enhanced_value = min(1.0, enhanced_values[i] * factor)

                # Gradual transition instead of sudden jump
                transition_factor = 0.8  # 80% new value, 20% old value for smoother transition
                enhanced_values[i] = transition_factor * enhanced_value + (1 - transition_factor) * enhanced_values[i]
            else:
                # Keep values below threshold as they are (stand in place)
                enhanced_values[i] = enhanced_values[i]

        return enhanced_values

    def draw_frame(self, frame, values, frame_idx, fps, vis_width, vis_height, vis_x, vis_y, bar_thickness, mirror_right=False, bar_height_min=10, bar_height_max=35, total_height=1080, total_width=1920, x_position=50, y_position=50, color=(255, 50, 100), dot_size=None, dot_filled=True, transparency=True, top_active=True, bottom_active=True, fill_alpha=0.5, border_alpha=1.0, smooth_arcs=False, enhanced_mode=None):
        # Apply enhanced mode processing to values
        values = self._apply_enhanced_mode(values, enhanced_mode, bar_height_min, bar_height_max, total_height)

        n_segments = len(values)
        # Use full video width for waveform positioning
        margin = max(10, total_width // 20)
        usable_w = total_width - 2 * margin

        # Calculate center position based on y_position parameter
        center_y = int(total_height * y_position / 100)

        # Calculate waveform height limits as percentages of total video height
        min_wave_h = int(total_height * bar_height_min / 100)
        max_wave_h = int(total_height * bar_height_max / 100)

        # Calculate the number of credits to draw
        if mirror_right:
            credits_per_side = n_segments // 2
            left_values = values[:credits_per_side]
            right_values = values[:credits_per_side]
        else:
            credits_per_side = n_segments
            left_values = values
            right_values = []

        # Draw left side waveform
        if len(left_values) > 0 and top_active:
            left_width = usable_w // 2 if mirror_right else usable_w
            if mirror_right:
                center_x = int(total_width * x_position / 100)
                start_x = center_x - left_width
            else:
                start_x = int(total_width * x_position / 100) - left_width // 2

            # Create credits for the top waveform
            top_credits = []
            for j in range(len(left_values)):
                amp = left_values[j]
                x = start_x + int((j / (len(left_values) - 1)) * left_width) if len(left_values) > 1 else start_x + left_width // 2
                wave_h = int(min_wave_h + amp * (max_wave_h - min_wave_h))
                y = center_y - wave_h // 2
                top_credits.append((x, y))

            # Draw filled area under the top curve
            if len(top_credits) > 1:
                # Create polygon credits for filled area
                fill_credits = top_credits.copy()
                # Add bottom credits to close the area
                fill_credits.append((top_credits[-1][0], center_y))
                fill_credits.append((top_credits[0][0], center_y))
                fill_credits.append(top_credits[0])

                # Convert to numpy array for fillPoly
                fill_credits_array = np.array(fill_credits, np.int32)

                # Calculate fill color with alpha
                if transparency:
                    fill_color_intensity = int(255 * np.mean(left_values))
                else:
                    fill_color_intensity = 255

                fill_color = (min(255, int(color[0] * (fill_color_intensity + 50) / 255)),
                             min(255, int(color[1] * (fill_color_intensity + 50) / 255)),
                             min(255, int(color[2] * (fill_color_intensity + 50) / 255)))

                # Create overlay for alpha blending
                overlay = frame.copy()
                cv2.fillPoly(overlay, [fill_credits_array], fill_color)
                cv2.addWeighted(frame, 1 - fill_alpha, overlay, fill_alpha, 0, frame)

            # Draw border (highest credits) with full alpha
            if smooth_arcs and len(top_credits) > 2:
                # Create smooth curves using interpolation
                if transparency:
                    border_color_intensity = int(255 * np.mean(left_values))
                else:
                    border_color_intensity = 255

                border_color = (min(255, int(color[0] * (border_color_intensity + 50) / 255)),
                               min(255, int(color[1] * (border_color_intensity + 50) / 255)),
                               min(255, int(color[2] * (border_color_intensity + 50) / 255)))

                # Interpolate credits for smooth curves
                smooth_credits = self._create_smooth_curve(top_credits)
                if len(smooth_credits) > 1:
                    for i in range(len(smooth_credits) - 1):
                        cv2.line(frame, smooth_credits[i], smooth_credits[i + 1], border_color, max(1, bar_thickness))
            else:
                # Draw straight lines
                for i in range(len(top_credits) - 1):
                    x1, y1 = top_credits[i]
                    x2, y2 = top_credits[i + 1]

                    # Calculate border color
                    if transparency:
                        border_color_intensity = int(255 * max(left_values[i], left_values[i + 1]))
                    else:
                        border_color_intensity = 255

                    border_color = (min(255, int(color[0] * (border_color_intensity + 50) / 255)),
                                   min(255, int(color[1] * (border_color_intensity + 50) / 255)),
                                   min(255, int(color[2] * (border_color_intensity + 50) / 255)))

                    # Draw line with border alpha
                    cv2.line(frame, (x1, y1), (x2, y2), border_color, max(1, bar_thickness))

        # Draw bottom side waveform
        if len(left_values) > 0 and bottom_active:
            left_width = usable_w // 2 if mirror_right else usable_w
            if mirror_right:
                center_x = int(total_width * x_position / 100)
                start_x = center_x - left_width
            else:
                start_x = int(total_width * x_position / 100) - left_width // 2

            # Create credits for the bottom waveform
            bottom_credits = []
            for j in range(len(left_values)):
                amp = left_values[j]
                x = start_x + int((j / (len(left_values) - 1)) * left_width) if len(left_values) > 1 else start_x + left_width // 2
                wave_h = int(min_wave_h + amp * (max_wave_h - min_wave_h))
                y = center_y + wave_h // 2
                bottom_credits.append((x, y))

            # Draw filled area above the bottom curve
            if len(bottom_credits) > 1:
                # Create polygon credits for filled area
                fill_credits = bottom_credits.copy()
                # Add top credits to close the area
                fill_credits.append((bottom_credits[-1][0], center_y))
                fill_credits.append((bottom_credits[0][0], center_y))
                fill_credits.append(bottom_credits[0])

                # Convert to numpy array for fillPoly
                fill_credits_array = np.array(fill_credits, np.int32)

                # Calculate fill color with alpha
                if transparency:
                    fill_color_intensity = int(255 * np.mean(left_values))
                else:
                    fill_color_intensity = 255

                fill_color = (min(255, int(color[0] * (fill_color_intensity + 50) / 255)),
                             min(255, int(color[1] * (fill_color_intensity + 50) / 255)),
                             min(255, int(color[2] * (fill_color_intensity + 50) / 255)))

                # Create overlay for alpha blending
                overlay = frame.copy()
                cv2.fillPoly(overlay, [fill_credits_array], fill_color)
                cv2.addWeighted(frame, 1 - fill_alpha, overlay, fill_alpha, 0, frame)

            # Draw border (highest credits) with full alpha
            if smooth_arcs and len(bottom_credits) > 2:
                # Create smooth curves using interpolation
                if transparency:
                    border_color_intensity = int(255 * np.mean(left_values))
                else:
                    border_color_intensity = 255

                border_color = (min(255, int(color[0] * (border_color_intensity + 50) / 255)),
                               min(255, int(color[1] * (border_color_intensity + 50) / 255)),
                               min(255, int(color[2] * (border_color_intensity + 50) / 255)))

                # Interpolate credits for smooth curves
                smooth_credits = self._create_smooth_curve(bottom_credits)
                if len(smooth_credits) > 1:
                    for i in range(len(smooth_credits) - 1):
                        cv2.line(frame, smooth_credits[i], smooth_credits[i + 1], border_color, max(1, bar_thickness))
            else:
                # Draw straight lines
                for i in range(len(bottom_credits) - 1):
                    x1, y1 = bottom_credits[i]
                    x2, y2 = bottom_credits[i + 1]

                    # Calculate border color
                    if transparency:
                        border_color_intensity = int(255 * max(left_values[i], left_values[i + 1]))
                    else:
                        border_color_intensity = 255

                    border_color = (min(255, int(color[0] * (border_color_intensity + 50) / 255)),
                                   min(255, int(color[1] * (border_color_intensity + 50) / 255)),
                                   min(255, int(color[2] * (border_color_intensity + 50) / 255)))

                    # Draw line with border alpha
                    cv2.line(frame, (x1, y1), (x2, y2), border_color, max(1, bar_thickness))

        # Draw right side waveform (mirrored) - top
        if mirror_right and len(right_values) > 0 and top_active:
            right_width = usable_w // 2
            center_x = int(total_width * x_position / 100)
            right_start_x = center_x

            # Create credits for the mirrored top waveform
            top_credits = []
            for j in range(len(right_values)):
                mirror_j = len(right_values) - 1 - j
                amp = right_values[mirror_j]
                x = right_start_x + int((j / (len(right_values) - 1)) * right_width) if len(right_values) > 1 else right_start_x + right_width // 2
                wave_h = int(min_wave_h + amp * (max_wave_h - min_wave_h))
                y = center_y - wave_h // 2
                top_credits.append((x, y))

            # Draw filled area under the top curve
            if len(top_credits) > 1:
                # Create polygon credits for filled area
                fill_credits = top_credits.copy()
                # Add bottom credits to close the area
                fill_credits.append((top_credits[-1][0], center_y))
                fill_credits.append((top_credits[0][0], center_y))
                fill_credits.append(top_credits[0])

                # Convert to numpy array for fillPoly
                fill_credits_array = np.array(fill_credits, np.int32)

                # Calculate fill color with alpha
                if transparency:
                    fill_color_intensity = int(255 * np.mean(right_values))
                else:
                    fill_color_intensity = 255

                fill_color = (min(255, int(color[0] * (fill_color_intensity + 50) / 255)),
                             min(255, int(color[1] * (fill_color_intensity + 50) / 255)),
                             min(255, int(color[2] * (fill_color_intensity + 50) / 255)))

                # Create overlay for alpha blending
                overlay = frame.copy()
                cv2.fillPoly(overlay, [fill_credits_array], fill_color)
                cv2.addWeighted(frame, 1 - fill_alpha, overlay, fill_alpha, 0, frame)

            # Draw border (highest credits) with full alpha
            if smooth_arcs and len(top_credits) > 2:
                # Create smooth curves using interpolation
                if transparency:
                    border_color_intensity = int(255 * np.mean(right_values))
                else:
                    border_color_intensity = 255

                border_color = (min(255, int(color[0] * (border_color_intensity + 50) / 255)),
                               min(255, int(color[1] * (border_color_intensity + 50) / 255)),
                               min(255, int(color[2] * (border_color_intensity + 50) / 255)))

                # Interpolate credits for smooth curves
                smooth_credits = self._create_smooth_curve(top_credits)
                if len(smooth_credits) > 1:
                    for i in range(len(smooth_credits) - 1):
                        cv2.line(frame, smooth_credits[i], smooth_credits[i + 1], border_color, max(1, bar_thickness))
            else:
                # Draw straight lines
                for i in range(len(top_credits) - 1):
                    x1, y1 = top_credits[i]
                    x2, y2 = top_credits[i + 1]

                    # Calculate border color
                    if transparency:
                        border_color_intensity = int(255 * max(right_values[i], right_values[i + 1]))
                    else:
                        border_color_intensity = 255

                    border_color = (min(255, int(color[0] * (border_color_intensity + 50) / 255)),
                                   min(255, int(color[1] * (border_color_intensity + 50) / 255)),
                                   min(255, int(color[2] * (border_color_intensity + 50) / 255)))

                    # Draw line with border alpha
                    cv2.line(frame, (x1, y1), (x2, y2), border_color, max(1, bar_thickness))

        # Draw right side waveform (mirrored) - bottom
        if mirror_right and len(right_values) > 0 and bottom_active:
            right_width = usable_w // 2
            center_x = int(total_width * x_position / 100)
            right_start_x = center_x

            # Create credits for the mirrored bottom waveform
            bottom_credits = []
            for j in range(len(right_values)):
                mirror_j = len(right_values) - 1 - j
                amp = right_values[mirror_j]
                x = right_start_x + int((j / (len(right_values) - 1)) * right_width) if len(right_values) > 1 else right_start_x + right_width // 2
                wave_h = int(min_wave_h + amp * (max_wave_h - min_wave_h))
                y = center_y + wave_h // 2
                bottom_credits.append((x, y))

            # Draw filled area above the bottom curve
            if len(bottom_credits) > 1:
                # Create polygon credits for filled area
                fill_credits = bottom_credits.copy()
                # Add top credits to close the area
                fill_credits.append((bottom_credits[-1][0], center_y))
                fill_credits.append((bottom_credits[0][0], center_y))
                fill_credits.append(bottom_credits[0])

                # Convert to numpy array for fillPoly
                fill_credits_array = np.array(fill_credits, np.int32)

                # Calculate fill color with alpha
                if transparency:
                    fill_color_intensity = int(255 * np.mean(right_values))
                else:
                    fill_color_intensity = 255

                fill_color = (min(255, int(color[0] * (fill_color_intensity + 50) / 255)),
                             min(255, int(color[1] * (fill_color_intensity + 50) / 255)),
                             min(255, int(color[2] * (fill_color_intensity + 50) / 255)))

                # Create overlay for alpha blending
                overlay = frame.copy()
                cv2.fillPoly(overlay, [fill_credits_array], fill_color)
                cv2.addWeighted(frame, 1 - fill_alpha, overlay, fill_alpha, 0, frame)

            # Draw border (highest credits) with full alpha
            if smooth_arcs and len(bottom_credits) > 2:
                # Create smooth curves using interpolation
                if transparency:
                    border_color_intensity = int(255 * np.mean(right_values))
                else:
                    border_color_intensity = 255

                border_color = (min(255, int(color[0] * (border_color_intensity + 50) / 255)),
                               min(255, int(color[1] * (border_color_intensity + 50) / 255)),
                               min(255, int(color[2] * (border_color_intensity + 50) / 255)))

                # Interpolate credits for smooth curves
                smooth_credits = self._create_smooth_curve(bottom_credits)
                if len(smooth_credits) > 1:
                    for i in range(len(smooth_credits) - 1):
                        cv2.line(frame, smooth_credits[i], smooth_credits[i + 1], border_color, max(1, bar_thickness))
            else:
                # Draw straight lines
                for i in range(len(bottom_credits) - 1):
                    x1, y1 = bottom_credits[i]
                    x2, y2 = bottom_credits[i + 1]

                    # Calculate border color
                    if transparency:
                        border_color_intensity = int(255 * max(right_values[i], right_values[i + 1]))
                    else:
                        border_color_intensity = 255

                    border_color = (min(255, int(color[0] * (border_color_intensity + 50) / 255)),
                                   min(255, int(color[1] * (border_color_intensity + 50) / 255)),
                                   min(255, int(color[2] * (border_color_intensity + 50) / 255)))

                    # Draw line with border alpha
                    cv2.line(frame, (x1, y1), (x2, y2), border_color, max(1, bar_thickness))

        return frame


# ----------------------------
# Usage
# ----------------------------
# Linear Bars Visualizer
vis_bars = LinearBarsVisualizer()
output_dir = os.path.dirname(__file__)
vis_bars.render(os.path.join(output_dir, "song.wav"), os.path.join(output_dir, "out_bars.mp4"),
          width=1280, height=720, draw_frame_fn=vis_bars.draw_frame,
          height_percent=10, width_percent=90,
          bar_thickness=3, bar_count=60, mirror_right=True,
          bar_height_min=10, bar_height_max=35, smoothness=0,
          x_position=50, y_position=50, color=(255, 50, 100),
          transparency=True, enhanced_mode={"active": True, "threshold": 0.3, "factor": 2.0})

# Linear Dots Visualizer
vis_dots = LinearDotsVisualizer()
vis_dots.render(os.path.join(output_dir, "song.wav"), os.path.join(output_dir, "out_dots.mp4"),
          width=1280, height=720, draw_frame_fn=vis_dots.draw_frame,
          height_percent=10, width_percent=90,
          bar_thickness=3, bar_count=60, mirror_right=True,
          bar_height_min=10, bar_height_max=35, smoothness=10,
          x_position=50, y_position=50, color=(255, 50, 100),
          dot_size=3, dot_filled=True, transparency=False,
          top_active=False, bottom_active=True, enhanced_mode={"active": True, "threshold": 0.3, "factor": 2.0})

# Waveform Visualizer
vis_waveform = WaveformVisualizer()
vis_waveform.render(os.path.join(output_dir, "song.wav"), os.path.join(output_dir, "out_waveform.mp4"),
          width=1280, height=720, draw_frame_fn=vis_waveform.draw_frame,
          height_percent=15, width_percent=90,
          bar_thickness=2, bar_count=120, mirror_right=True,
          bar_height_min=0, bar_height_max=40, smoothness=20,
          x_position=50, y_position=50, color=(100, 200, 255),
          fill_alpha=0.5, border_alpha=1.0, transparency=True,
          top_active=True, bottom_active=True, smooth_arcs=True,
          enhanced_mode={"active": True, "threshold": 0.3, "factor": 2.0})