"""
Enhanced Music Analyzer
Refactored music analyzer with centralized utilities and improved error handling
"""

import io
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import librosa
import matplotlib.pyplot as plt
import numpy as np
import ruptures as rpt
import soundfile as sf
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, savgol_filter

from ..centralized_workflow_utilities import (
    BaseWorkflow, WorkflowType, WorkflowStatus, WorkflowValidationMixin,
    WorkflowLoggingMixin, WorkflowFileOperationMixin, WorkflowAsyncOperationMixin,
    create_workflow_logger, validate_workflow_parameters, create_temp_workflow_directory,
    cleanup_workflow_directory, save_workflow_result, execute_system_command
)
from api.services.unified_services import handle_errors, ErrorContext


class EnhancedMusicAnalyzerWorkflow(BaseWorkflow):
    """Enhanced music analyzer workflow with centralized utilities"""
    
    def __init__(self):
        super().__init__(WorkflowType.ANALYSIS, "music_analyzer")
        self.logger = create_workflow_logger("music_analyzer")
    
    @handle_errors("music_analyzer", "execute")
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the music analysis workflow"""
        # Validate parameters
        required_fields = ["audio_path"]
        validate_workflow_parameters(parameters, required_fields)
        
        audio_path = parameters["audio_path"]
        analysis_type = parameters.get("analysis_type", "comprehensive")
        output_path = parameters.get("output_path")
        
        # Validate file paths
        self._validate_file_paths(audio_path)
        if output_path:
            self._validate_output_path(output_path)
        
        # Create temp directory
        temp_dir = create_temp_workflow_directory(self.workflow_id)
        
        try:
            # Step 1: Load audio
            self._update_progress(10.0)
            audio_data, sample_rate = await self._load_audio(audio_path)
            
            # Step 2: Detect segments
            self._update_progress(30.0)
            segments = await self._detect_music_segments(audio_data, sample_rate, parameters)
            
            # Step 3: Extract features
            self._update_progress(50.0)
            features = await self._extract_music_features(audio_data, sample_rate, parameters)
            
            # Step 4: Generate visualization data
            self._update_progress(70.0)
            visualization_data = await self._generate_visualization_data(audio_data, sample_rate, parameters)
            
            # Step 5: Compile results
            self._update_progress(90.0)
            results = await self._compile_analysis_results(segments, features, visualization_data, parameters)
            
            # Step 6: Save results
            if output_path:
                save_workflow_result(results, output_path)
            
            self._update_progress(100.0)
            return results
            
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
    
    async def _detect_music_segments(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect music segments using improved algorithm"""
        try:
            self.logger.info("Detecting music segments")
            
            # Get parameters
            min_peaks = parameters.get("min_peaks", 2)
            max_peaks = parameters.get("max_peaks", None)
            window_size = parameters.get("window_size", 1024)
            hop_length = parameters.get("hop_length", 512)
            min_gap_seconds = parameters.get("min_gap_seconds", 2.0)
            short_ma_sec = parameters.get("short_ma_sec", 0.50)
            long_ma_sec = parameters.get("long_ma_sec", 3.00)
            include_boundaries = parameters.get("include_boundaries", True)
            
            # Detect segments using improved algorithm
            segments = await self._detect_music_segments_precise(
                audio_data, sample_rate, min_peaks, max_peaks, window_size,
                hop_length, min_gap_seconds, short_ma_sec, long_ma_sec, include_boundaries
            )
            
            self.logger.info(f"Detected {len(segments)} music segments")
            return segments
            
        except Exception as e:
            self.logger.error(f"Failed to detect music segments: {e}")
            raise
    
    async def _detect_music_segments_precise(
        self,
        y: np.ndarray,
        sr: int,
        min_peaks: int = 2,
        max_peaks: Optional[int] = None,
        window_size: int = 1024,
        hop_length: int = 512,
        min_gap_seconds: float = 2.0,
        short_ma_sec: float = 0.50,
        long_ma_sec: float = 3.00,
        include_boundaries: bool = True
    ) -> Dict[str, Any]:
        """Detect precise musical segments using improved algorithm"""
        try:
            self.logger.info(f"Analyzing audio - Duration: {len(y)/sr:.2f} seconds, Sample rate: {sr} Hz")
            
            # RMS ENERGY → dB
            rms = librosa.feature.rms(y=y, frame_length=window_size, hop_length=hop_length)[0]
            rms_db = librosa.amplitude_to_db(rms, ref=np.max)
            rms_db = np.nan_to_num(rms_db, nan=np.min(rms_db))
            
            # SMOOTH dB TO REDUCE NOISE
            smoothed_db = gaussian_filter1d(rms_db, sigma=1.5)
            
            # MOVING AVERAGES (SHORT AND LONG)
            def moving_average(x, win):
                win = max(1, int(win))
                kernel = np.ones(win, dtype=float) / float(win)
                return np.convolve(x, kernel, mode='same')
            
            short_frames = max(1, int(round(short_ma_sec * sr / hop_length)))
            long_frames = max(short_frames + 1, int(round(long_ma_sec * sr / hop_length)))
            ma_short = moving_average(smoothed_db, short_frames)
            ma_long = moving_average(smoothed_db, long_frames)
            
            # TIMES
            L = len(smoothed_db)
            times = librosa.frames_to_time(np.arange(L), sr=sr, hop_length=hop_length)
            
            # ROBUST NORMALIZATION (z-score via MAD)
            def robust_z(x):
                x = np.asarray(x)
                med = np.median(x)
                mad = np.median(np.abs(x - med)) + 1e-8
                return (x - med) / (1.4826 * mad)
            
            score = ma_short - ma_long
            score_z = robust_z(score)
            score_z = gaussian_filter1d(score_z, sigma=1.0)
            
            # IMPROVED ADAPTIVE THRESHOLD USING MULTIPLE CRITERIA
            def adaptive_threshold(score_z, rms_db, times):
                # Base threshold using robust statistics
                base_thr = np.median(score_z) + 0.8 * (np.median(np.abs(score_z - np.median(score_z))) * 1.4826)
                
                # Energy-based threshold adjustment
                energy_percentile = np.percentile(rms_db, 70)  # Focus on higher energy regions
                energy_mask = rms_db > energy_percentile
                if np.any(energy_mask):
                    energy_thr = np.median(score_z[energy_mask]) + 0.5 * np.std(score_z[energy_mask])
                    base_thr = min(base_thr, energy_thr)
                
                return base_thr
            
            thr = adaptive_threshold(score_z, rms_db, times)
            
            # TEMPO-AWARE MIN DISTANCE BETWEEN PEAKS
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
            try:
                tempo = float(tempo)
            except Exception:
                tempo = float(np.asarray(tempo).reshape(-1)[0]) if np.size(tempo) else 0.0
            
            # Dynamic minimum distance based on tempo and audio characteristics
            if tempo <= 0:
                min_dist_frames = max(1, int(0.5 * sr / hop_length))
            else:
                seconds_per_beat = 60.0 / tempo
                min_dist_frames = max(1, int(0.3 * float(seconds_per_beat) * sr / hop_length))
            
            # MIN GAP IN FRAMES
            min_gap_frames = max(1, int(min_gap_seconds * sr / hop_length))
            min_dist_frames = max(min_dist_frames, min_gap_frames)
            
            # PEAK DETECTION
            peaks, properties = find_peaks(
                score_z,
                height=thr,
                distance=min_dist_frames,
                prominence=0.1
            )
            
            # CONVERT PEAKS TO TIMES
            peak_times = times[peaks]
            
            # DYNAMIC PEAK COUNT EVALUATION
            if max_peaks is None:
                max_peaks = max(min_peaks * 3, len(peak_times))
            
            # Filter peaks if too many
            if len(peak_times) > max_peaks:
                # Sort by prominence and take top peaks
                prominences = properties['prominences']
                sorted_indices = np.argsort(prominences)[::-1]
                selected_indices = sorted_indices[:max_peaks]
                peak_times = peak_times[selected_indices]
                peak_times = np.sort(peak_times)
            
            # INCLUDE BOUNDARIES
            if include_boundaries:
                if len(peak_times) == 0 or peak_times[0] > 1.0:
                    peak_times = np.concatenate([[0.0], peak_times])
                if len(peak_times) == 0 or peak_times[-1] < times[-1] - 1.0:
                    peak_times = np.concatenate([peak_times, [times[-1]]])
            
            # CREATE SEGMENTS
            segments = []
            for i in range(len(peak_times) - 1):
                start_time = peak_times[i]
                end_time = peak_times[i + 1]
                duration = end_time - start_time
                
                segments.append({
                    "start_time": float(start_time),
                    "end_time": float(end_time),
                    "duration": float(duration),
                    "segment_index": i
                })
            
            return {
                "segments": segments,
                "peak_times": peak_times.tolist(),
                "tempo": float(tempo),
                "threshold": float(thr),
                "total_segments": len(segments),
                "analysis_parameters": {
                    "min_peaks": min_peaks,
                    "max_peaks": max_peaks,
                    "window_size": window_size,
                    "hop_length": hop_length,
                    "min_gap_seconds": min_gap_seconds,
                    "short_ma_sec": short_ma_sec,
                    "long_ma_sec": long_ma_sec,
                    "include_boundaries": include_boundaries
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to detect music segments precisely: {e}")
            raise
    
    async def _extract_music_features(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract comprehensive music features"""
        try:
            self.logger.info("Extracting music features")
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            
            # Extract rhythm features
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sample_rate)
            onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate)
            
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            chroma_mean = np.mean(chroma, axis=1)
            
            # Extract tonnetz features
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            tonnetz_mean = np.mean(tonnetz, axis=1)
            
            # Extract zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # Extract RMS energy
            rms = librosa.feature.rms(y=audio_data)[0]
            
            # Calculate global features
            global_features = {
                "tempo": float(tempo),
                "duration": len(audio_data) / sample_rate,
                "sample_rate": sample_rate,
                "mean_spectral_centroid": float(np.mean(spectral_centroids)),
                "mean_spectral_rolloff": float(np.mean(spectral_rolloff)),
                "mean_spectral_bandwidth": float(np.mean(spectral_bandwidth)),
                "mean_zcr": float(np.mean(zcr)),
                "mean_rms": float(np.mean(rms)),
                "chroma_mean": chroma_mean.tolist(),
                "tonnetz_mean": tonnetz_mean.tolist(),
                "num_beats": len(beats),
                "num_onsets": len(onset_times)
            }
            
            # Extract segment-wise features
            segment_features = {
                "spectral_centroids": spectral_centroids.tolist(),
                "spectral_rolloff": spectral_rolloff.tolist(),
                "spectral_bandwidth": spectral_bandwidth.tolist(),
                "mfccs": mfccs.tolist(),
                "zcr": zcr.tolist(),
                "rms": rms.tolist(),
                "chroma": chroma.tolist(),
                "tonnetz": tonnetz.tolist(),
                "beats": beats.tolist(),
                "onset_times": onset_times.tolist()
            }
            
            features = {
                "global_features": global_features,
                "segment_features": segment_features,
                "extraction_parameters": {
                    "window_size": parameters.get("window_size", 1024),
                    "hop_length": parameters.get("hop_length", 512),
                    "n_mfcc": 13
                }
            }
            
            self.logger.info("Music features extracted successfully")
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract music features: {e}")
            raise
    
    async def _generate_visualization_data(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visualization data for audio visualizers"""
        try:
            self.logger.info("Generating visualization data")
            
            # Extract features for visualization
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            rms = librosa.feature.rms(y=audio_data)[0]
            
            # Calculate time frames
            hop_length = parameters.get("hop_length", 512)
            times = librosa.frames_to_time(np.arange(len(rms)), sr=sample_rate, hop_length=hop_length)
            
            # Generate visualization data
            visualization_data = {
                "times": times.tolist(),
                "spectral_centroids": spectral_centroids.tolist(),
                "spectral_rolloff": spectral_rolloff.tolist(),
                "mfccs": mfccs.tolist(),
                "rms": rms.tolist(),
                "duration": len(audio_data) / sample_rate,
                "sample_rate": sample_rate,
                "hop_length": hop_length
            }
            
            self.logger.info("Visualization data generated successfully")
            return visualization_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate visualization data: {e}")
            raise
    
    async def _compile_analysis_results(
        self,
        segments: Dict[str, Any],
        features: Dict[str, Any],
        visualization_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile comprehensive analysis results"""
        try:
            self.logger.info("Compiling analysis results")
            
            results = {
                "analysis_id": self.workflow_id,
                "analysis_timestamp": self._start_time.isoformat() if self._start_time else None,
                "analysis_type": parameters.get("analysis_type", "comprehensive"),
                "segments": segments,
                "features": features,
                "visualization_data": visualization_data,
                "parameters": parameters,
                "metadata": {
                    "workflow_version": "2.0.0",
                    "analysis_duration": (self._end_time - self._start_time).total_seconds() if self._start_time and self._end_time else None,
                    "status": "completed"
                }
            }
            
            self.logger.info("Analysis results compiled successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to compile analysis results: {e}")
            raise


class EnhancedMusicAnalyzerService:
    """Enhanced music analyzer service with centralized utilities"""
    
    def __init__(self):
        self.logger = create_workflow_logger("music_analyzer_service")
        self.workflow = EnhancedMusicAnalyzerWorkflow()
    
    @handle_errors("music_analyzer_service", "analyze_music")
    async def analyze_music(
        self,
        audio_path: str,
        analysis_type: str = "comprehensive",
        output_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze music with enhanced error handling"""
        try:
            self.logger.info(f"Starting music analysis: {audio_path}")
            
            # Prepare parameters
            parameters = {
                "audio_path": audio_path,
                "analysis_type": analysis_type,
                "output_path": output_path,
                **kwargs
            }
            
            # Execute workflow
            result = await self.workflow.run(parameters)
            
            self.logger.info(f"Music analysis completed: {audio_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Music analysis failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return await self.workflow.health_check()


# Factory function for creating music analyzer service
def create_music_analyzer_service() -> EnhancedMusicAnalyzerService:
    """Create enhanced music analyzer service instance"""
    return EnhancedMusicAnalyzerService()


# Export
__all__ = [
    "EnhancedMusicAnalyzerWorkflow",
    "EnhancedMusicAnalyzerService",
    "create_music_analyzer_service"
]
