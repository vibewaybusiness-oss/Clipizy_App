"""
Enhanced Unified Visualizer System
Refactored visualizer system with centralized utilities and improved error handling
"""

import os
import shutil
import subprocess
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import cv2
import librosa
import numpy as np
import torch
from pydub import AudioSegment

try:
    from moviepy.editor import AudioFileClip, VideoFileClip
except ImportError:
    try:
        from moviepy import AudioFileClip, VideoFileClip
    except ImportError:
        VideoFileClip = None
        AudioFileClip = None

from ..centralized_workflow_utilities import (
    BaseWorkflow, WorkflowType, WorkflowStatus, WorkflowValidationMixin,
    WorkflowLoggingMixin, WorkflowFileOperationMixin, WorkflowAsyncOperationMixin,
    create_workflow_logger, validate_workflow_parameters, create_temp_workflow_directory,
    cleanup_workflow_directory, save_workflow_result, execute_system_command
)
from api.services.unified_services import handle_errors, ErrorContext


class VisualizerType(Enum):
    """Visualizer types"""
    LINEAR_BARS = "linear_bars"
    LINEAR_DOTS = "linear_dots"
    WAVEFORM = "waveform"
    BASS_CIRCLE = "bass_circle"
    TRAP_NATION = "trap_nation"


class VisualizerConfig:
    """Configuration for visualizer"""
    
    def __init__(
        self,
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
        enhanced_mode: Optional[Dict[str, Any]] = None
    ):
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


class EnhancedUnifiedVisualizerWorkflow(BaseWorkflow):
    """Enhanced unified visualizer workflow with centralized utilities"""
    
    def __init__(self):
        super().__init__(WorkflowType.VISUALIZATION, "unified_visualizer")
        self.logger = create_workflow_logger("unified_visualizer")
    
    @handle_errors("unified_visualizer", "execute")
    async def execute(self, parameters: Dict[str, Any]) -> str:
        """Execute the visualizer workflow"""
        # Validate parameters
        required_fields = ["audio_path", "output_path", "config"]
        validate_workflow_parameters(parameters, required_fields)
        
        audio_path = parameters["audio_path"]
        output_path = parameters["output_path"]
        config = parameters["config"]
        
        # Validate file paths
        self._validate_file_paths(audio_path)
        self._validate_output_path(output_path)
        
        # Create temp directory
        temp_dir = create_temp_workflow_directory(self.workflow_id)
        
        try:
            # Step 1: Load and process audio
            self._update_progress(10.0)
            audio_data, sample_rate = await self._load_audio(audio_path)
            
            # Step 2: Extract audio features
            self._update_progress(30.0)
            features = await self._extract_audio_features(audio_data, sample_rate, config)
            
            # Step 3: Generate visualizer frames
            self._update_progress(50.0)
            frames = await self._generate_visualizer_frames(features, config)
            
            # Step 4: Create video
            self._update_progress(70.0)
            video_path = await self._create_video(frames, audio_path, output_path, config)
            
            # Step 5: Apply post-processing
            self._update_progress(90.0)
            final_output = await self._apply_post_processing(video_path, config)
            
            self._update_progress(100.0)
            return final_output
            
        finally:
            # Cleanup temp directory
            cleanup_workflow_directory(temp_dir)
    
    async def _load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file"""
        try:
            self.logger.info(f"Loading audio file: {audio_path}")
            
            # Load audio using librosa
            audio_data, sample_rate = librosa.load(audio_path, sr=None)
            
            self.logger.info(f"Audio loaded: {len(audio_data)} samples at {sample_rate} Hz")
            return audio_data, sample_rate
            
        except Exception as e:
            self.logger.error(f"Failed to load audio file {audio_path}: {e}")
            raise
    
    async def _extract_audio_features(self, audio_data: np.ndarray, sample_rate: int, config: VisualizerConfig) -> Dict[str, Any]:
        """Extract audio features for visualization"""
        try:
            self.logger.info("Extracting audio features")
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            
            # Extract rhythm features
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            
            # Calculate RMS energy
            rms = librosa.feature.rms(y=audio_data)[0]
            
            features = {
                "spectral_centroids": spectral_centroids,
                "spectral_rolloff": spectral_rolloff,
                "mfccs": mfccs,
                "tempo": tempo,
                "beats": beats,
                "chroma": chroma,
                "rms": rms,
                "sample_rate": sample_rate,
                "duration": len(audio_data) / sample_rate
            }
            
            self.logger.info("Audio features extracted successfully")
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract audio features: {e}")
            raise
    
    async def _generate_visualizer_frames(self, features: Dict[str, Any], config: VisualizerConfig) -> List[np.ndarray]:
        """Generate visualizer frames"""
        try:
            self.logger.info(f"Generating {config.visualizer_type.value} frames")
            
            if config.visualizer_type == VisualizerType.LINEAR_BARS:
                frames = await self._generate_linear_bars_frames(features, config)
            elif config.visualizer_type == VisualizerType.LINEAR_DOTS:
                frames = await self._generate_linear_dots_frames(features, config)
            elif config.visualizer_type == VisualizerType.WAVEFORM:
                frames = await self._generate_waveform_frames(features, config)
            elif config.visualizer_type == VisualizerType.BASS_CIRCLE:
                frames = await self._generate_bass_circle_frames(features, config)
            elif config.visualizer_type == VisualizerType.TRAP_NATION:
                frames = await self._generate_trap_nation_frames(features, config)
            else:
                raise ValueError(f"Unsupported visualizer type: {config.visualizer_type}")
            
            self.logger.info(f"Generated {len(frames)} frames")
            return frames
            
        except Exception as e:
            self.logger.error(f"Failed to generate visualizer frames: {e}")
            raise
    
    async def _generate_linear_bars_frames(self, features: Dict[str, Any], config: VisualizerConfig) -> List[np.ndarray]:
        """Generate linear bars frames"""
        frames = []
        rms = features["rms"]
        duration = features["duration"]
        fps = config.fps
        total_frames = int(duration * fps)
        
        # Calculate bar positions and properties
        bar_count = config.bar_count or config.n_segments
        bar_width = config.width // bar_count
        bar_height_range = config.bar_height_max - config.bar_height_min
        
        for frame_idx in range(total_frames):
            # Create frame
            frame = np.zeros((config.height, config.width, 3), dtype=np.uint8)
            
            # Calculate time position
            time_pos = frame_idx / fps
            
            # Get RMS value for this time
            rms_idx = int((time_pos / duration) * len(rms))
            rms_value = rms[min(rms_idx, len(rms) - 1)]
            
            # Normalize RMS value
            normalized_rms = np.clip(rms_value / np.max(rms), 0, 1)
            
            # Generate bars
            for bar_idx in range(bar_count):
                # Calculate bar height
                bar_height = config.bar_height_min + int(normalized_rms * bar_height_range)
                
                # Calculate bar position
                x_start = bar_idx * bar_width
                x_end = x_start + bar_width - 1
                y_start = config.height - bar_height
                y_end = config.height
                
                # Draw bar
                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), config.color, -1)
                
                # Mirror if enabled
                if config.mirror_right:
                    mirror_x_start = config.width - x_end
                    mirror_x_end = config.width - x_start
                    cv2.rectangle(frame, (mirror_x_start, y_start), (mirror_x_end, y_end), config.color, -1)
            
            frames.append(frame)
        
        return frames
    
    async def _generate_linear_dots_frames(self, features: Dict[str, Any], config: VisualizerConfig) -> List[np.ndarray]:
        """Generate linear dots frames"""
        frames = []
        rms = features["rms"]
        duration = features["duration"]
        fps = config.fps
        total_frames = int(duration * fps)
        
        # Calculate dot properties
        dot_count = config.bar_count or config.n_segments
        dot_spacing = config.width // dot_count
        dot_size = config.dot_size or 3
        
        for frame_idx in range(total_frames):
            # Create frame
            frame = np.zeros((config.height, config.width, 3), dtype=np.uint8)
            
            # Calculate time position
            time_pos = frame_idx / fps
            
            # Get RMS value for this time
            rms_idx = int((time_pos / duration) * len(rms))
            rms_value = rms[min(rms_idx, len(rms) - 1)]
            
            # Normalize RMS value
            normalized_rms = np.clip(rms_value / np.max(rms), 0, 1)
            
            # Generate dots
            for dot_idx in range(dot_count):
                # Calculate dot position
                x = dot_idx * dot_spacing + dot_spacing // 2
                y = config.height // 2
                
                # Draw dot
                if config.dot_filled:
                    cv2.circle(frame, (x, y), dot_size, config.color, -1)
                else:
                    cv2.circle(frame, (x, y), dot_size, config.color, 2)
                
                # Mirror if enabled
                if config.mirror_right:
                    mirror_x = config.width - x
                    if config.dot_filled:
                        cv2.circle(frame, (mirror_x, y), dot_size, config.color, -1)
                    else:
                        cv2.circle(frame, (mirror_x, y), dot_size, config.color, 2)
            
            frames.append(frame)
        
        return frames
    
    async def _generate_waveform_frames(self, features: Dict[str, Any], config: VisualizerConfig) -> List[np.ndarray]:
        """Generate waveform frames"""
        frames = []
        rms = features["rms"]
        duration = features["duration"]
        fps = config.fps
        total_frames = int(duration * fps)
        
        for frame_idx in range(total_frames):
            # Create frame
            frame = np.zeros((config.height, config.width, 3), dtype=np.uint8)
            
            # Calculate time position
            time_pos = frame_idx / fps
            
            # Get RMS value for this time
            rms_idx = int((time_pos / duration) * len(rms))
            rms_value = rms[min(rms_idx, len(rms) - 1)]
            
            # Normalize RMS value
            normalized_rms = np.clip(rms_value / np.max(rms), 0, 1)
            
            # Calculate waveform height
            waveform_height = int(normalized_rms * config.height * 0.8)
            
            # Draw waveform
            center_y = config.height // 2
            y_start = center_y - waveform_height // 2
            y_end = center_y + waveform_height // 2
            
            cv2.line(frame, (0, y_start), (config.width, y_start), config.color, 2)
            cv2.line(frame, (0, y_end), (config.width, y_end), config.color, 2)
            
            frames.append(frame)
        
        return frames
    
    async def _generate_bass_circle_frames(self, features: Dict[str, Any], config: VisualizerConfig) -> List[np.ndarray]:
        """Generate bass circle frames"""
        frames = []
        rms = features["rms"]
        duration = features["duration"]
        fps = config.fps
        total_frames = int(duration * fps)
        
        # Calculate circle properties
        center_x = config.width // 2
        center_y = config.height // 2
        max_radius = min(config.width, config.height) // 4
        
        for frame_idx in range(total_frames):
            # Create frame
            frame = np.zeros((config.height, config.width, 3), dtype=np.uint8)
            
            # Calculate time position
            time_pos = frame_idx / fps
            
            # Get RMS value for this time
            rms_idx = int((time_pos / duration) * len(rms))
            rms_value = rms[min(rms_idx, len(rms) - 1)]
            
            # Normalize RMS value
            normalized_rms = np.clip(rms_value / np.max(rms), 0, 1)
            
            # Calculate circle radius
            radius = int(normalized_rms * max_radius)
            
            # Draw circle
            if radius > 0:
                cv2.circle(frame, (center_x, center_y), radius, config.color, -1)
            
            frames.append(frame)
        
        return frames
    
    async def _generate_trap_nation_frames(self, features: Dict[str, Any], config: VisualizerConfig) -> List[np.ndarray]:
        """Generate trap nation frames"""
        frames = []
        rms = features["rms"]
        duration = features["duration"]
        fps = config.fps
        total_frames = int(duration * fps)
        
        # Calculate bar properties
        bar_count = config.bar_count or config.n_segments
        bar_width = config.width // bar_count
        bar_height_range = config.bar_height_max - config.bar_height_min
        
        for frame_idx in range(total_frames):
            # Create frame
            frame = np.zeros((config.height, config.width, 3), dtype=np.uint8)
            
            # Calculate time position
            time_pos = frame_idx / fps
            
            # Get RMS value for this time
            rms_idx = int((time_pos / duration) * len(rms))
            rms_value = rms[min(rms_idx, len(rms) - 1)]
            
            # Normalize RMS value
            normalized_rms = np.clip(rms_value / np.max(rms), 0, 1)
            
            # Generate bars with trap nation style
            for bar_idx in range(bar_count):
                # Calculate bar height with variation
                base_height = config.bar_height_min + int(normalized_rms * bar_height_range)
                variation = np.sin(bar_idx * 0.5 + time_pos * 2) * 5
                bar_height = max(1, int(base_height + variation))
                
                # Calculate bar position
                x_start = bar_idx * bar_width
                x_end = x_start + bar_width - 1
                y_start = config.height - bar_height
                y_end = config.height
                
                # Draw bar with gradient effect
                for y in range(y_start, y_end):
                    alpha = (y - y_start) / (y_end - y_start)
                    color = tuple(int(c * alpha) for c in config.color)
                    cv2.line(frame, (x_start, y), (x_end, y), color, 1)
            
            frames.append(frame)
        
        return frames
    
    async def _create_video(self, frames: List[np.ndarray], audio_path: str, output_path: str, config: VisualizerConfig) -> str:
        """Create video from frames"""
        try:
            self.logger.info("Creating video from frames")
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, config.fps, (config.width, config.height))
            
            # Write frames
            for frame in frames:
                video_writer.write(frame)
            
            video_writer.release()
            
            # Add audio to video
            if AudioFileClip:
                try:
                    # Load audio
                    audio_clip = AudioFileClip(audio_path)
                    
                    # Load video
                    video_clip = VideoFileClip(output_path)
                    
                    # Combine audio and video
                    final_clip = video_clip.set_audio(audio_clip)
                    
                    # Write final video
                    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
                    
                    # Clean up
                    audio_clip.close()
                    video_clip.close()
                    final_clip.close()
                    
                except Exception as e:
                    self.logger.warning(f"Failed to add audio to video: {e}")
            
            self.logger.info(f"Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to create video: {e}")
            raise
    
    async def _apply_post_processing(self, video_path: str, config: VisualizerConfig) -> str:
        """Apply post-processing to video"""
        try:
            self.logger.info("Applying post-processing")
            
            # Apply fade in/out if specified
            if config.fadein > 0 or config.fadeout > 0:
                if VideoFileClip:
                    try:
                        # Load video
                        video_clip = VideoFileClip(video_path)
                        
                        # Apply fades
                        if config.fadein > 0:
                            video_clip = video_clip.fadein(config.fadein)
                        if config.fadeout > 0:
                            video_clip = video_clip.fadeout(config.fadeout)
                        
                        # Write processed video
                        video_clip.write_videofile(video_path, codec='libx264')
                        
                        # Clean up
                        video_clip.close()
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to apply fades: {e}")
            
            self.logger.info("Post-processing completed")
            return video_path
            
        except Exception as e:
            self.logger.error(f"Failed to apply post-processing: {e}")
            raise


class EnhancedUnifiedVisualizerService:
    """Enhanced unified visualizer service with centralized utilities"""
    
    def __init__(self):
        self.logger = create_workflow_logger("unified_visualizer_service")
        self.workflow = EnhancedUnifiedVisualizerWorkflow()
    
    @handle_errors("unified_visualizer_service", "render_visualizer")
    async def render_visualizer(
        self,
        audio_path: str,
        output_path: str,
        config: VisualizerConfig
    ) -> str:
        """Render visualizer with enhanced error handling"""
        try:
            self.logger.info(f"Starting visualizer rendering: {audio_path} -> {output_path}")
            
            # Prepare parameters
            parameters = {
                "audio_path": audio_path,
                "output_path": output_path,
                "config": config
            }
            
            # Execute workflow
            result = await self.workflow.run(parameters)
            
            self.logger.info(f"Visualizer rendering completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Visualizer rendering failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return await self.workflow.health_check()


# Factory function for creating visualizer service
def create_visualizer_service() -> EnhancedUnifiedVisualizerService:
    """Create enhanced visualizer service instance"""
    return EnhancedUnifiedVisualizerService()


# Export
__all__ = [
    "VisualizerType",
    "VisualizerConfig",
    "EnhancedUnifiedVisualizerWorkflow",
    "EnhancedUnifiedVisualizerService",
    "create_visualizer_service"
]
