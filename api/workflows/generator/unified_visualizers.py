import os
import shutil
import subprocess

import cv2
import librosa
import numpy as np
from pydub import AudioSegment

# Optional torch import
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PyTorch not available: {e}")
    TORCH_AVAILABLE = False
    torch = None

try:
    from moviepy.editor import AudioFileClip, VideoFileClip
except ImportError:
    try:
        from moviepy import AudioFileClip, VideoFileClip
    except ImportError:
        VideoFileClip = None
        AudioFileClip = None
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class VisualizerType(Enum):
    LINEAR_BARS = "linear_bars"
    LINEAR_DOTS = "linear_dots"
    WAVEFORM = "waveform"
    BASS_CIRCLE = "bass_circle"
    TRAP_NATION = "trap_nation"

class VisualizerConfig:
    def __init__(self, 
                 visualizer_type: VisualizerType,
                 width: int = 1920,
                 height: int = 1080,
                 fps: int = 30,
                 n_segments: int = 60,
                 fadein: float = 3.0,
                 fadeout: float = 3.0,
                 delay_outro: float = 0.0,
                 duration_intro: float = 0.0,
                 time_in: float = 0.0,
                 height_percent: int = 10,
                 width_percent: int = 90,
                 bar_thickness: Optional[int] = None,
                 bar_count: Optional[int] = None,
                 mirror_right: bool = False,
                 bar_height_min: int = 10,
                 bar_height_max: int = 35,
                 smoothness: int = 0,
                 x_position: int = 50,
                 y_position: int = 50,
                 color: Tuple[int, int, int] = (255, 50, 100),
                 dot_size: Optional[int] = None,
                 dot_filled: bool = True,
                 transparency: bool = True,
                 top_active: bool = True,
                 bottom_active: bool = True,
                 fill_alpha: float = 0.5,
                 border_alpha: float = 1.0,
                 smooth_arcs: bool = False,
                 enhanced_mode: Optional[Dict[str, Any]] = None):
        self.visualizer_type = visualizer_type
        self.width = width
        self.height = height
        self.fps = fps
        self.n_segments = n_segments
        self.fadein = fadein
        self.fadeout = fadeout
        self.delay_outro = delay_outro
        self.duration_intro = duration_intro
        self.time_in = time_in
        self.height_percent = height_percent
        self.width_percent = width_percent
        self.bar_thickness = bar_thickness
        self.bar_count = bar_count
        self.mirror_right = mirror_right
        self.bar_height_min = bar_height_min
        self.bar_height_max = bar_height_max
        self.smoothness = smoothness
        self.x_position = x_position
        self.y_position = y_position
        self.color = color
        self.dot_size = dot_size
        self.dot_filled = dot_filled
        self.transparency = transparency
        self.top_active = top_active
        self.bottom_active = bottom_active
        self.fill_alpha = fill_alpha
        self.border_alpha = border_alpha
        self.smooth_arcs = smooth_arcs
        self.enhanced_mode = enhanced_mode or {"active": False, "threshold": 0.3, "factor": 2.0}

class Logger:
    def __init__(self, name: str = "Visualizer"):
        self.name = name
    
    def log(self, message: str):
        print(f"[{self.name}] {message}")
    
    def error(self, message: str):
        print(f"[{self.name}] ERROR: {message}")
    
    def warning(self, message: str):
        print(f"[{self.name}] WARNING: {message}")
    
    def info(self, message: str):
        print(f"[{self.name}] INFO: {message}")

class AudioVisualizerBase:
    def __init__(self, name: str = "Visualizer"):
        self.logger = Logger(name)
        self.temp_dir = None
        self.fade_params = {}
        self.visualizer_fps = 30
        self.time_in = 0.0

    def render(self, audio_path: str, output_path: str, config: VisualizerConfig, video_path: Optional[str] = None) -> str:
        self.logger.log(f"Starting render for {audio_path}")
        self.visualizer_fps = config.fps
        self.time_in = config.time_in

        vis_width = int(config.width * config.width_percent / 100)
        vis_height = int(config.height * config.height_percent / 100)
        
        vis_x = int(config.width * config.x_position / 100) - vis_width // 2
        vis_y = int(config.height * config.y_position / 100) - vis_height // 2
        
        vis_x = max(0, min(vis_x, config.width - vis_width))
        vis_y = max(0, min(vis_y, config.height - vis_height))

        if config.bar_count is None:
            config.bar_count = config.n_segments
        if config.bar_thickness is None:
            config.bar_thickness = max(1, int(vis_width / config.bar_count / 2))
        
        if config.dot_size is None:
            config.dot_size = max(1, config.bar_thickness)
        
        smoothness_factor = config.smoothness / 100.0

        y_sr, fft_data, duration, total_frames, _ = self._prepare_fft_data(
            audio_path, config.fps, config.n_segments, config.duration_intro,
            config.fadein, config.fadeout, config.delay_outro, smoothness_factor
        )

        bg_video = self._load_background(video_path, duration, config.width, config.height)
        writer, temp_path = self._init_writer(output_path, config.fps, config.width, config.height)

        smoothing_buffer = None
        previous_values = None
        velocity_buffer = None
        moving_average_buffer = None

        for i in range(total_frames):
            frame = self._create_background_frame(bg_video, i / config.fps, config.width, config.height)
            opacity = self._calculate_opacity(i)

            if opacity > 0:
                values = fft_data[i].detach().cpu().numpy() * opacity
                if config.bar_count < len(values):
                    values = values[:config.bar_count]
                elif config.bar_count > len(values):
                    padded_values = np.zeros(config.bar_count)
                    padded_values[:len(values)] = values
                    values = padded_values
                
                if smoothness_factor > 0:
                    values = self._apply_frame_smoothing(values, smoothness_factor, smoothing_buffer, previous_values, velocity_buffer, moving_average_buffer, i)
                    if smoothing_buffer is None:
                        smoothing_buffer = values.copy()
                        previous_values = values.copy()
                        velocity_buffer = np.zeros_like(values)
                        moving_average_buffer = [values.copy()]
                    else:
                        smoothing_buffer = values.copy()
                        previous_values = values.copy()
                        if len(moving_average_buffer) >= 3:
                            moving_average_buffer.pop(0)
                        moving_average_buffer.append(values.copy())
                
                frame = self._draw_frame(frame, values, i, config, vis_width, vis_height, vis_x, vis_y)

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

    def _draw_frame(self, frame: np.ndarray, values: np.ndarray, frame_idx: int, config: VisualizerConfig, vis_width: int, vis_height: int, vis_x: int, vis_y: int) -> np.ndarray:
        if config.visualizer_type == VisualizerType.LINEAR_BARS:
            return self._draw_linear_bars(frame, values, config)
        elif config.visualizer_type == VisualizerType.LINEAR_DOTS:
            return self._draw_linear_dots(frame, values, config)
        elif config.visualizer_type == VisualizerType.WAVEFORM:
            return self._draw_waveform(frame, values, config)
        elif config.visualizer_type == VisualizerType.BASS_CIRCLE:
            return self._draw_bass_circle(frame, values, config)
        elif config.visualizer_type == VisualizerType.TRAP_NATION:
            return self._draw_trap_nation(frame, values, config)
        else:
            return frame

    def _draw_linear_bars(self, frame: np.ndarray, values: np.ndarray, config: VisualizerConfig) -> np.ndarray:
        values = self._apply_enhanced_mode(values, config)
        
        n_segments = len(values)
        margin = max(10, config.width // 20)
        usable_w = config.width - 2 * margin
        center_y = int(config.height * config.y_position / 100)
        min_bar_h = int(config.height * config.bar_height_min / 100)
        max_bar_h = int(config.height * config.bar_height_max / 100)

        if config.mirror_right:
            bars_per_side = n_segments // 2
            left_values = values[:bars_per_side]
            right_values = values[:bars_per_side]
        else:
            bars_per_side = n_segments
            left_values = values
            right_values = []

        if len(left_values) > 0:
            left_width = usable_w // 2 if config.mirror_right else usable_w
            start_x = int(config.width * config.x_position / 100) - left_width // 2
            for j in range(len(left_values)):
                amp = left_values[j]
                x = start_x + int((j / (len(left_values) - 1)) * left_width) if len(left_values) > 1 else start_x + left_width // 2
                bar_h = int(min_bar_h + amp * (max_bar_h - min_bar_h))
                top = int(center_y - bar_h/2)
                bottom = int(center_y + bar_h/2)
                
                if config.transparency:
                    color_intensity = int(255 * amp)
                else:
                    color_intensity = 255
                bar_color = (min(255, int(config.color[0] * (color_intensity + 50) / 255)), 
                           min(255, int(config.color[1] * (color_intensity + 50) / 255)), 
                           min(255, int(config.color[2] * (color_intensity + 50) / 255)))
                cv2.line(frame, (x, top), (x, bottom), bar_color, config.bar_thickness)

        if config.mirror_right and len(right_values) > 0:
            right_width = usable_w // 2
            right_start_x = int(config.width * config.x_position / 100) + right_width // 2
            for j in range(len(right_values)):
                mirror_j = len(right_values) - 1 - j
                amp = right_values[mirror_j]
                x = right_start_x + int((j / (len(right_values) - 1)) * right_width) if len(right_values) > 1 else right_start_x + right_width // 2
                bar_h = int(min_bar_h + amp * (max_bar_h - min_bar_h))
                top = int(center_y - bar_h/2)
                bottom = int(center_y + bar_h/2)
                
                if config.transparency:
                    color_intensity = int(255 * amp)
                else:
                    color_intensity = 255
                bar_color = (min(255, int(config.color[0] * (color_intensity + 50) / 255)), 
                           min(255, int(config.color[1] * (color_intensity + 50) / 255)), 
                           min(255, int(config.color[2] * (color_intensity + 50) / 255)))
                cv2.line(frame, (x, top), (x, bottom), bar_color, config.bar_thickness)
        
        return frame

    def _draw_linear_dots(self, frame: np.ndarray, values: np.ndarray, config: VisualizerConfig) -> np.ndarray:
        values = self._apply_enhanced_mode(values, config)
        
        n_segments = len(values)
        margin = max(10, config.width // 20)
        usable_w = config.width - 2 * margin
        center_y = int(config.height * config.y_position / 100)
        min_dot_h = int(config.height * config.bar_height_min / 100)
        max_dot_h = int(config.height * config.bar_height_max / 100)

        if config.mirror_right:
            dots_per_side = n_segments // 2
            left_values = values[:dots_per_side]
            right_values = values[:dots_per_side]
        else:
            dots_per_side = n_segments
            left_values = values
            right_values = []

        if len(left_values) > 0:
            left_width = usable_w // 2 if config.mirror_right else usable_w
            if config.mirror_right:
                center_x = int(config.width * config.x_position / 100)
                start_x = center_x - left_width
            else:
                start_x = int(config.width * config.x_position / 100) - left_width // 2
            for j in range(len(left_values)):
                amp = left_values[j]
                x = start_x + int((j / (len(left_values) - 1)) * left_width) if len(left_values) > 1 else start_x + left_width // 2
                dot_h = int(min_dot_h + amp * (max_dot_h - min_dot_h))
                top_y = int(center_y - dot_h/2)
                bottom_y = int(center_y + dot_h/2)
                
                if config.transparency:
                    color_intensity = int(255 * amp)
                else:
                    color_intensity = 255
                dot_color = (min(255, int(config.color[0] * (color_intensity + 50) / 255)), 
                           min(255, int(config.color[1] * (color_intensity + 50) / 255)), 
                           min(255, int(config.color[2] * (color_intensity + 50) / 255)))
                
                if config.top_active:
                    self._draw_high_quality_dot(frame, x, top_y, config.dot_size, dot_color, config.dot_filled)
                if config.bottom_active:
                    self._draw_high_quality_dot(frame, x, bottom_y, config.dot_size, dot_color, config.dot_filled)

        if config.mirror_right and len(right_values) > 0:
            right_width = usable_w // 2
            center_x = int(config.width * config.x_position / 100)
            right_start_x = center_x
            for j in range(len(right_values)):
                mirror_j = len(right_values) - 1 - j
                amp = right_values[mirror_j]
                x = right_start_x + int((j / (len(right_values) - 1)) * right_width) if len(right_values) > 1 else right_start_x + right_width // 2
                dot_h = int(min_dot_h + amp * (max_dot_h - min_dot_h))
                top_y = int(center_y - dot_h/2)
                bottom_y = int(center_y + dot_h/2)
                
                if config.transparency:
                    color_intensity = int(255 * amp)
                else:
                    color_intensity = 255
                dot_color = (min(255, int(config.color[0] * (color_intensity + 50) / 255)), 
                           min(255, int(config.color[1] * (color_intensity + 50) / 255)), 
                           min(255, int(config.color[2] * (color_intensity + 50) / 255)))
                
                if config.top_active:
                    self._draw_high_quality_dot(frame, x, top_y, config.dot_size, dot_color, config.dot_filled)
                if config.bottom_active:
                    self._draw_high_quality_dot(frame, x, bottom_y, config.dot_size, dot_color, config.dot_filled)
        
        return frame

    def _draw_waveform(self, frame: np.ndarray, values: np.ndarray, config: VisualizerConfig) -> np.ndarray:
        values = self._apply_enhanced_mode(values, config)
        
        n_segments = len(values)
        margin = max(10, config.width // 20)
        usable_w = config.width - 2 * margin
        center_y = int(config.height * config.y_position / 100)
        min_wave_h = int(config.height * config.bar_height_min / 100)
        max_wave_h = int(config.height * config.bar_height_max / 100)

        if config.mirror_right:
            credits_per_side = n_segments // 2
            left_values = values[:credits_per_side]
            right_values = values[:credits_per_side]
        else:
            credits_per_side = n_segments
            left_values = values
            right_values = []

        if len(left_values) > 0 and config.top_active:
            left_width = usable_w // 2 if config.mirror_right else usable_w
            if config.mirror_right:
                center_x = int(config.width * config.x_position / 100)
                start_x = center_x - left_width
            else:
                start_x = int(config.width * config.x_position / 100) - left_width // 2
            
            top_credits = []
            for j in range(len(left_values)):
                amp = left_values[j]
                x = start_x + int((j / (len(left_values) - 1)) * left_width) if len(left_values) > 1 else start_x + left_width // 2
                wave_h = int(min_wave_h + amp * (max_wave_h - min_wave_h))
                y = center_y - wave_h // 2
                top_credits.append((x, y))
            
            if len(top_credits) > 1:
                fill_credits = top_credits.copy()
                fill_credits.append((top_credits[-1][0], center_y))
                fill_credits.append((top_credits[0][0], center_y))
                fill_credits.append(top_credits[0])
                
                fill_credits_array = np.array(fill_credits, np.int32)
                
                if config.transparency:
                    fill_color_intensity = int(255 * np.mean(left_values))
                else:
                    fill_color_intensity = 255
                
                fill_color = (min(255, int(config.color[0] * (fill_color_intensity + 50) / 255)), 
                             min(255, int(config.color[1] * (fill_color_intensity + 50) / 255)), 
                             min(255, int(config.color[2] * (fill_color_intensity + 50) / 255)))
                
                overlay = frame.copy()
                cv2.fillPoly(overlay, [fill_credits_array], fill_color)
                cv2.addWeighted(frame, 1 - config.fill_alpha, overlay, config.fill_alpha, 0, frame)
            
            if config.smooth_arcs and len(top_credits) > 2:
                if config.transparency:
                    border_color_intensity = int(255 * np.mean(left_values))
                else:
                    border_color_intensity = 255
                
                border_color = (min(255, int(config.color[0] * (border_color_intensity + 50) / 255)), 
                               min(255, int(config.color[1] * (border_color_intensity + 50) / 255)), 
                               min(255, int(config.color[2] * (border_color_intensity + 50) / 255)))
                
                smooth_credits = self._create_smooth_curve(top_credits)
                if len(smooth_credits) > 1:
                    for i in range(len(smooth_credits) - 1):
                        cv2.line(frame, smooth_credits[i], smooth_credits[i + 1], border_color, max(1, config.bar_thickness))
            else:
                for i in range(len(top_credits) - 1):
                    x1, y1 = top_credits[i]
                    x2, y2 = top_credits[i + 1]
                    
                    if config.transparency:
                        border_color_intensity = int(255 * max(left_values[i], left_values[i + 1]))
                    else:
                        border_color_intensity = 255
                    
                    border_color = (min(255, int(config.color[0] * (border_color_intensity + 50) / 255)), 
                                   min(255, int(config.color[1] * (border_color_intensity + 50) / 255)), 
                                   min(255, int(config.color[2] * (border_color_intensity + 50) / 255)))
                    
                    cv2.line(frame, (x1, y1), (x2, y2), border_color, max(1, config.bar_thickness))
        
        return frame

    def _draw_bass_circle(self, frame: np.ndarray, values: np.ndarray, config: VisualizerConfig) -> np.ndarray:
        center_x = int(config.width * config.x_position / 100)
        center_y = int(config.height * config.y_position / 100)
        
        max_radius = min(config.width, config.height) // 4
        min_radius = max_radius // 4
        
        for i, amp in enumerate(values):
            angle = (i / len(values)) * 2 * np.pi
            radius = int(min_radius + amp * (max_radius - min_radius))
            
            x = int(center_x + radius * np.cos(angle))
            y = int(center_y + radius * np.sin(angle))
            
            if config.transparency:
                color_intensity = int(255 * amp)
            else:
                color_intensity = 255
            
            circle_color = (min(255, int(config.color[0] * (color_intensity + 50) / 255)), 
                          min(255, int(config.color[1] * (color_intensity + 50) / 255)), 
                          min(255, int(config.color[2] * (color_intensity + 50) / 255)))
            
            cv2.circle(frame, (x, y), config.dot_size, circle_color, -1)
        
        return frame

    def _draw_trap_nation(self, frame: np.ndarray, values: np.ndarray, config: VisualizerConfig) -> np.ndarray:
        center_x = int(config.width * config.x_position / 100)
        center_y = int(config.height * config.y_position / 100)
        
        max_radius = min(config.width, config.height) // 3
        
        for i, amp in enumerate(values):
            angle = (i / len(values)) * 2 * np.pi
            radius = int(amp * max_radius)
            
            x = int(center_x + radius * np.cos(angle))
            y = int(center_y + radius * np.sin(angle))
            
            if config.transparency:
                color_intensity = int(255 * amp)
            else:
                color_intensity = 255
            
            bar_color = (min(255, int(config.color[0] * (color_intensity + 50) / 255)), 
                        min(255, int(config.color[1] * (color_intensity + 50) / 255)), 
                        min(255, int(config.color[2] * (color_intensity + 50) / 255)))
            
            cv2.line(frame, (center_x, center_y), (x, y), bar_color, config.bar_thickness)
        
        return frame

    def _draw_high_quality_dot(self, frame: np.ndarray, x: int, y: int, radius: int, color: Tuple[int, int, int], filled: bool):
        if filled:
            for i in range(radius + 1):
                alpha = 1.0 - (i / (radius + 1)) * 0.3
                blended_color = tuple(int(c * alpha) for c in color)
                cv2.circle(frame, (x, y), radius - i, blended_color, -1)
        else:
            thickness = max(2, radius // 3)
            for i in range(thickness):
                alpha = 1.0 - (i / thickness) * 0.2
                blended_color = tuple(int(c * alpha) for c in color)
                cv2.circle(frame, (x, y), radius - i, blended_color, 1)

    def _create_smooth_curve(self, credits: List[Tuple[int, int]], interpolation_factor: int = 8) -> List[Tuple[int, int]]:
        if len(credits) < 2:
            return credits
        
        if len(credits) == 2:
            x1, y1 = credits[0]
            x2, y2 = credits[1]
            smooth_credits = []
            
            for i in range(interpolation_factor + 1):
                t = i / interpolation_factor
                smooth_t = t * t * (3.0 - 2.0 * t)
                x = int(x1 + (x2 - x1) * smooth_t)
                y = int(y1 + (y2 - y1) * smooth_t)
                smooth_credits.append((x, y))
            
            return smooth_credits
        
        x_coords = [p[0] for p in credits]
        y_coords = [p[1] for p in credits]
        
        x_smooth = []
        y_smooth = []
        
        x_smooth.append(credits[0][0])
        y_smooth.append(credits[0][1])
        
        for i in range(len(credits) - 1):
            x1, y1 = credits[i]
            x2, y2 = credits[i + 1]
            
            if i > 0:
                x0, y0 = credits[i - 1]
                cp1_x = x1 + (x1 - x0) * 0.2
                cp1_y = y1 + (y1 - y0) * 0.2
            else:
                cp1_x = x1
                cp1_y = y1
            
            if i < len(credits) - 2:
                x3, y3 = credits[i + 2]
                cp2_x = x2 - (x3 - x2) * 0.2
                cp2_y = y2 - (y3 - y2) * 0.2
            else:
                cp2_x = x2
                cp2_y = y2
            
            for j in range(1, interpolation_factor + 1):
                t = j / interpolation_factor
                x_interp = int((1-t)**3 * x1 + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * x2)
                y_interp = int((1-t)**3 * y1 + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * y2)
                
                x_smooth.append(x_interp)
                y_smooth.append(y_interp)
        
        return list(zip(x_smooth, y_smooth))

    def _apply_enhanced_mode(self, values: np.ndarray, config: VisualizerConfig) -> np.ndarray:
        if not config.enhanced_mode or not config.enhanced_mode.get("active", False):
            return values
        
        threshold = config.enhanced_mode.get("threshold", 0.3)
        factor = config.enhanced_mode.get("factor", 2.0)
        
        min_height = int(config.height * config.bar_height_min / 100)
        max_height = int(config.height * config.bar_height_max / 100)
        height_range = max_height - min_height
        height_threshold = height_range * threshold
        
        enhanced_values = values.copy()
        for i in range(len(enhanced_values)):
            current_height_increase = enhanced_values[i] * height_range
            
            if current_height_increase >= height_threshold:
                enhanced_value = min(1.0, enhanced_values[i] * factor)
                transition_factor = 0.8
                enhanced_values[i] = transition_factor * enhanced_value + (1 - transition_factor) * enhanced_values[i]
            else:
                enhanced_values[i] = enhanced_values[i]
        
        return enhanced_values

    def _prepare_fft_data_numpy(self, audio_path: str, fps: int, n_segments: int, duration_intro: float = 0, fadein: float = 3, fadeout: float = 3, delay_outro: float = 0, smoothness_factor: float = 0.0):
        """Numpy fallback for FFT processing when PyTorch is not available"""
        audio = AudioSegment.from_file(audio_path)
        if duration_intro > 0:
            audio = audio[duration_intro * 1000:]

        if not self.temp_dir:
            self.temp_dir = os.path.join(os.path.dirname(audio_path), "temp_fft")
        os.makedirs(self.temp_dir, exist_ok=True)
        temp_wav = os.path.join(self.temp_dir, "audio_temp.wav")
        audio.export(temp_wav, format="wav")

        y, sr = librosa.load(temp_wav, sr=None)
        duration = len(y) / sr
        total_frames = int(duration * fps)
        samples_per_frame = int(sr / fps)

        # Use numpy instead of torch
        y_array = np.array(y)
        
        if smoothness_factor > 0.3:
            window = np.hanning(samples_per_frame)
        else:
            window = np.ones(samples_per_frame)
        
        fft_magnitude_list = []
        for i in range(total_frames):
            start_idx = i * samples_per_frame
            end_idx = start_idx + samples_per_frame
            
            if start_idx >= len(y_array):
                frame_data = np.zeros(samples_per_frame)
            else:
                frame_data = y_array[start_idx:end_idx]
                if len(frame_data) < samples_per_frame:
                    pad_length = samples_per_frame - len(frame_data)
                    frame_data = np.pad(frame_data, (0, pad_length))
            
            frame_data = frame_data * window
            fft = np.fft.fft(frame_data)
            fft_magnitude = np.abs(fft[:samples_per_frame//2])
            fft_magnitude_list.append(fft_magnitude)
        
        return fft_magnitude_list

    def _prepare_fft_data(self, audio_path: str, fps: int, n_segments: int, duration_intro: float = 0, fadein: float = 3, fadeout: float = 3, delay_outro: float = 0, smoothness_factor: float = 0.0):
        if not TORCH_AVAILABLE:
            self.logger.warning("PyTorch not available, using numpy fallback for FFT processing")
            return self._prepare_fft_data_numpy(audio_path, fps, n_segments, duration_intro, fadein, fadeout, delay_outro, smoothness_factor)
        
        audio = AudioSegment.from_file(audio_path)
        if duration_intro > 0:
            audio = audio[duration_intro * 1000:]

        if not self.temp_dir:
            self.temp_dir = os.path.join(os.path.dirname(audio_path), "temp_fft")
        os.makedirs(self.temp_dir, exist_ok=True)
        temp_wav = os.path.join(self.temp_dir, "audio_temp.wav")
        audio.export(temp_wav, format="wav")

        y, sr = librosa.load(temp_wav, sr=None)
        duration = len(y) / sr
        total_frames = int(duration * fps)
        samples_per_frame = int(sr / fps)

        y_tensor = torch.tensor(y, device="cpu")
        
        if smoothness_factor > 0.3:
            window = torch.hann_window(samples_per_frame)
        else:
            window = torch.ones(samples_per_frame)
        
        fft_magnitude_list = []
        for i in range(total_frames):
            start_idx = i * samples_per_frame
            end_idx = start_idx + samples_per_frame
            
            if start_idx >= len(y_tensor):
                frame_data = torch.zeros(samples_per_frame)
            else:
                frame_data = y_tensor[start_idx:end_idx]
                if len(frame_data) < samples_per_frame:
                    pad_length = samples_per_frame - len(frame_data)
                    frame_data = torch.cat([frame_data, torch.zeros(pad_length)])
            
            frame_data = frame_data * window
            fft_frame = torch.fft.rfft(frame_data)
            fft_mag = torch.abs(fft_frame[:n_segments // 2])
            
            fft_magnitude_list.append(fft_mag)
        
        fft_magnitude = torch.stack(fft_magnitude_list)
        
        if smoothness_factor > 0.5:
            smoothing_alpha = 0.1 + (0.3 * smoothness_factor)
            fft_magnitude = self._apply_smoothing_filter(fft_magnitude, alpha=smoothing_alpha)
        
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

    def _apply_smoothing_filter(self, fft_magnitude: torch.Tensor, alpha: float = 0.3) -> torch.Tensor:
        smoothed = torch.zeros_like(fft_magnitude)
        smoothed[0] = fft_magnitude[0]
        
        for i in range(1, len(fft_magnitude)):
            smoothed[i] = alpha * fft_magnitude[i] + (1 - alpha) * smoothed[i-1]
        
        return smoothed

    def _apply_frame_smoothing(self, values: np.ndarray, smoothness_factor: float, smoothing_buffer: Optional[np.ndarray], previous_values: Optional[np.ndarray], velocity_buffer: Optional[np.ndarray], moving_average_buffer: Optional[List[np.ndarray]], frame_idx: int) -> np.ndarray:
        if smoothing_buffer is None or previous_values is None:
            return values
        
        velocity = values - previous_values
        
        if smoothness_factor < 0.3:
            max_velocity = 0.3
        else:
            max_velocity = 0.1 + (0.2 * smoothness_factor)
        velocity = np.clip(velocity, -max_velocity, max_velocity)
        
        if velocity_buffer is not None:
            velocity_buffer = 0.5 * velocity_buffer + 0.5 * velocity
        else:
            velocity_buffer = velocity
        
        smoothed_values = previous_values + velocity_buffer
        
        if smoothness_factor >= 0.6 and moving_average_buffer is not None and len(moving_average_buffer) > 1:
            moving_avg = np.mean(moving_average_buffer, axis=0)
            blend_factor = (smoothness_factor - 0.6) / 0.4
            smoothed_values = (1 - blend_factor) * smoothed_values + blend_factor * moving_avg
        
        if smoothness_factor < 0.3:
            smoothing_alpha = 0.5
        else:
            smoothing_alpha = 0.2 + (0.3 * smoothness_factor)
        final_values = (1 - smoothing_alpha) * smoothing_buffer + smoothing_alpha * smoothed_values
        
        return final_values

    def _load_background(self, video_path: Optional[str], duration: float, width: int, height: int):
        if not video_path or VideoFileClip is None:
            return None
        try:
            clip = VideoFileClip(video_path).subclip(0, duration).resize((width, height))
            return clip
        except Exception as e:
            self.logger.log(f"⚠️ Failed to load background video: {e}")
            return None

    def _create_background_frame(self, bg_video, t: float, width: int, height: int) -> np.ndarray:
        if bg_video:
            try:
                frame = bg_video.get_frame(t)[:, :, ::-1].copy()
                return frame
            except Exception:
                pass
        return np.zeros((height, width, 3), dtype=np.uint8)

    def _calculate_opacity(self, frame_idx: int) -> float:
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

    def _init_writer(self, output_path: str, fps: int, width: int, height: int):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        temp_path = output_path + ".temp.mp4"
        writer = cv2.VideoWriter(
            temp_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )
        if not writer.isOpened():
            raise RuntimeError("Failed to open video writer")
        return writer, temp_path

    def _finalize_output(self, temp_path: str, output_path: str):
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(temp_path, output_path)

    def _add_audio(self, video_path: str, audio_path: str):
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

class UnifiedVisualizerService:
    def __init__(self):
        self.visualizer = AudioVisualizerBase("UnifiedVisualizer")
    
    def create_visualizer(self, visualizer_type: VisualizerType) -> AudioVisualizerBase:
        return AudioVisualizerBase(f"{visualizer_type.value}_visualizer")
    
    def render_visualizer(self, audio_path: str, output_path: str, config: VisualizerConfig, video_path: Optional[str] = None) -> str:
        visualizer = self.create_visualizer(config.visualizer_type)
        return visualizer.render(audio_path, output_path, config, video_path)
    
    def get_available_visualizers(self) -> List[Dict[str, str]]:
        return [
            {"type": vt.value, "name": vt.value.replace("_", " ").title()} 
            for vt in VisualizerType
        ]
    
    def get_visualizer_config_schema(self) -> Dict[str, Any]:
        return {
            "visualizer_type": {
                "type": "string",
                "enum": [vt.value for vt in VisualizerType],
                "description": "Type of visualizer to use"
            },
            "width": {"type": "integer", "default": 1920, "description": "Video width"},
            "height": {"type": "integer", "default": 1080, "description": "Video height"},
            "fps": {"type": "integer", "default": 30, "description": "Frames per second"},
            "n_segments": {"type": "integer", "default": 60, "description": "Number of frequency segments"},
            "fadein": {"type": "number", "default": 3.0, "description": "Fade in duration in seconds"},
            "fadeout": {"type": "number", "default": 3.0, "description": "Fade out duration in seconds"},
            "delay_outro": {"type": "number", "default": 0.0, "description": "Delay after fadeout in seconds"},
            "duration_intro": {"type": "number", "default": 0.0, "description": "Skip intro duration in seconds"},
            "time_in": {"type": "number", "default": 0.0, "description": "Time offset before visualizer appears"},
            "height_percent": {"type": "integer", "default": 10, "description": "Height as percentage of screen"},
            "width_percent": {"type": "integer", "default": 90, "description": "Width as percentage of screen"},
            "bar_thickness": {"type": "integer", "nullable": True, "description": "Thickness of bars"},
            "bar_count": {"type": "integer", "nullable": True, "description": "Number of bars to display"},
            "mirror_right": {"type": "boolean", "default": False, "description": "Mirror bars to the right side"},
            "bar_height_min": {"type": "integer", "default": 10, "description": "Minimum bar height percentage"},
            "bar_height_max": {"type": "integer", "default": 35, "description": "Maximum bar height percentage"},
            "smoothness": {"type": "integer", "default": 0, "description": "Smoothness level 0-100"},
            "x_position": {"type": "integer", "default": 50, "description": "X position percentage"},
            "y_position": {"type": "integer", "default": 50, "description": "Y position percentage"},
            "color": {"type": "array", "items": {"type": "integer"}, "default": [255, 50, 100], "description": "RGB color tuple"},
            "dot_size": {"type": "integer", "nullable": True, "description": "Size of dots in pixels"},
            "dot_filled": {"type": "boolean", "default": True, "description": "Whether to draw filled dots"},
            "transparency": {"type": "boolean", "default": True, "description": "Whether opacity depends on audio values"},
            "top_active": {"type": "boolean", "default": True, "description": "Whether to draw top elements"},
            "bottom_active": {"type": "boolean", "default": True, "description": "Whether to draw bottom elements"},
            "fill_alpha": {"type": "number", "default": 0.5, "description": "Alpha value for filled areas"},
            "border_alpha": {"type": "number", "default": 1.0, "description": "Alpha value for borders"},
            "smooth_arcs": {"type": "boolean", "default": False, "description": "Whether to use smooth curves"},
            "enhanced_mode": {
                "type": "object",
                "properties": {
                    "active": {"type": "boolean", "default": False},
                    "threshold": {"type": "number", "default": 0.3},
                    "factor": {"type": "number", "default": 2.0}
                },
                "description": "Enhanced mode settings"
            }
        }
