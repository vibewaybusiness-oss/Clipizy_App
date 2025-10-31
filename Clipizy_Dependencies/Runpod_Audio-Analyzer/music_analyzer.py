"""
Unified Music Analyzer
Combines enhanced features with working standalone implementation
Supports both synchronous and asynchronous interfaces
"""

import io
import os
import logging
import asyncio
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import uuid

import librosa
import numpy as np
import ruptures as rpt
import soundfile as sf
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, savgol_filter

MATPLOTLIB_AVAILABLE = False
plt = None

def _import_matplotlib():
    global MATPLOTLIB_AVAILABLE, plt
    if not MATPLOTLIB_AVAILABLE:
        try:
            import matplotlib.pyplot as plt
            MATPLOTLIB_AVAILABLE = True
            return True
        except Exception as e:
            print(f"⚠️ Matplotlib not available: {e}")
            MATPLOTLIB_AVAILABLE = False
            plt = None
            return False
    return MATPLOTLIB_AVAILABLE

def _create_logger(name: str = "music_analyzer") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def detect_music_segments_precise(
    y, sr,
    min_peaks=2,
    max_peaks=None,
    window_size=1024,
    hop_length=512,
    min_gap_seconds=2.0,
    short_ma_sec=0.50,
    long_ma_sec=3.00,
    include_boundaries=True,
):
    """
    Detect precise musical segments using improved MOVING-AVERAGE DIFFERENCE method on RMS dB.
    Uses adaptive thresholding and dynamic peak count evaluation.
    """
    print(f"Loading audio - Duration: {len(y)/sr:.2f} seconds, Sample rate: {sr} Hz")

    rms = librosa.feature.rms(y=y, frame_length=window_size, hop_length=hop_length)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    rms_db = np.nan_to_num(rms_db, nan=np.min(rms_db))

    smoothed_db = gaussian_filter1d(rms_db, sigma=1.5)

    def moving_average(x, win):
        win = max(1, int(win))
        kernel = np.ones(win, dtype=float) / float(win)
        return np.convolve(x, kernel, mode='same')

    short_frames = max(1, int(round(short_ma_sec * sr / hop_length)))
    long_frames = max(short_frames + 1, int(round(long_ma_sec * sr / hop_length)))
    ma_short = moving_average(smoothed_db, short_frames)
    ma_long = moving_average(smoothed_db, long_frames)

    L = len(smoothed_db)
    times = librosa.frames_to_time(np.arange(L), sr=sr, hop_length=hop_length)

    def robust_z(x):
        x = np.asarray(x)
        med = np.median(x)
        mad = np.median(np.abs(x - med)) + 1e-8
        return (x - med) / (1.4826 * mad)

    score = ma_short - ma_long
    score_z = robust_z(score)
    score_z = gaussian_filter1d(score_z, sigma=1.0)

    def adaptive_threshold(score_z, rms_db, times):
        base_thr = np.median(score_z) + 0.8 * (np.median(np.abs(score_z - np.median(score_z))) * 1.4826)
        energy_percentile = np.percentile(rms_db, 70)
        energy_mask = rms_db > energy_percentile
        if np.any(energy_mask):
            energy_thr = np.median(score_z[energy_mask]) + 0.5 * np.std(score_z[energy_mask])
            base_thr = min(base_thr, energy_thr)
        return base_thr

    thr = adaptive_threshold(score_z, rms_db, times)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
    try:
        tempo = float(tempo)
    except Exception:
        tempo = float(np.asarray(tempo).reshape(-1)[0]) if np.size(tempo) else 0.0
    
    if tempo <= 0:
        min_dist_frames = max(1, int(0.5 * sr / hop_length))
    else:
        seconds_per_beat = 60.0 / tempo
        min_dist_frames = max(1, int(0.3 * float(seconds_per_beat) * sr / hop_length))

    min_gap_frames = max(1, int(min_gap_seconds * sr / hop_length))
    min_dist_frames = max(min_dist_frames, min_gap_frames)

    def find_peaks_multi_level(score_z, times, rms_db, base_thr):
        all_peaks = []
        
        peaks1, props1 = find_peaks(
            score_z,
            height=base_thr,
            distance=min_dist_frames,
            prominence=np.std(score_z) * 0.6
        )
        all_peaks.extend([(p, score_z[p], 1.0) for p in peaks1])
        
        peaks2, props2 = find_peaks(
            score_z,
            height=base_thr * 0.7,
            distance=max(1, min_dist_frames // 2),
            prominence=np.std(score_z) * 0.3
        )
        for p in peaks2:
            if all(abs(times[p] - times[existing_p]) >= min_gap_seconds 
                   for existing_p, _, _ in all_peaks):
                all_peaks.append((p, score_z[p], 0.7))
        
        energy_threshold = np.percentile(rms_db, 60)
        high_energy_mask = rms_db > energy_threshold
        if np.any(high_energy_mask):
            high_energy_indices = np.where(high_energy_mask)[0]
            high_energy_score = score_z[high_energy_mask]
            peaks3, props3 = find_peaks(
                high_energy_score,
                height=base_thr * 0.5,
                distance=max(1, min_dist_frames // 3),
                prominence=np.std(high_energy_score) * 0.2
            )
            for p in peaks3:
                actual_p = high_energy_indices[p]
                if all(abs(times[actual_p] - times[existing_p]) >= min_gap_seconds 
                       for existing_p, _, _ in all_peaks):
                    all_peaks.append((actual_p, score_z[actual_p], 0.5))
        
        return all_peaks

    all_peaks = find_peaks_multi_level(score_z, times, rms_db, thr)
    
    def dual_analysis_approach(peaks, times, duration, score_z, rms_db):
        if not peaks:
            return min_peaks, [], []
        
        peaks_with_confidence = [(p, s, l, s * l) for p, s, l in peaks]
        peaks_with_confidence.sort(key=lambda x: x[3], reverse=True)
        
        print("="*60)
        print("STAGE 1: TEMPO-BASED PEAKS (RED)")
        print("="*60)
        
        def get_tempo_peaks(score_z, rms_db, times, duration):
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
            try:
                tempo = float(tempo)
            except Exception:
                tempo = 120.0
            
            print(f"Detected tempo: {tempo:.1f} BPM")
            
            if tempo > 0:
                seconds_per_beat = 60.0 / tempo
                phrase_length = seconds_per_beat * 4
            else:
                phrase_length = 6.0
            
            tempo_based_count = max(5, int(duration / phrase_length))
            
            print(f"Tempo-based phrase length: {phrase_length:.2f} seconds")
            print(f"Tempo-based peak count: {tempo_based_count}")
            
            tempo_peaks = []
            min_gap_frames = max(1, int(phrase_length * sr / hop_length))
            
            for p, s, l, conf in peaks_with_confidence:
                if len(tempo_peaks) >= tempo_based_count:
                    break
                t = times[p]
                if all(abs(t - times[existing_p]) >= phrase_length for existing_p, _, _, _ in tempo_peaks):
                    tempo_peaks.append((p, s, l, conf))
            
            return tempo_peaks, tempo, phrase_length
        
        tempo_peaks, tempo, phrase_length = get_tempo_peaks(score_z, rms_db, times, duration)
        
        print("\n" + "="*60)
        print("STAGE 2: MOVING AVERAGE GAP SEGMENT DETECTION (GREEN)")
        print("="*60)
        
        def detect_segments_ma_gap(score_z, rms_db, times, duration, ma_short, ma_long):
            window_size = max(8.0, duration / 15.0)
            window_frames = int(window_size * sr / hop_length)
            
            print(f"Using window size: {window_size:.2f} seconds")
            print("Using moving average values for gap calculation")
            
            segments = []
            segment_starts = [0]
            
            segments.append({
                'time': 0.0,
                'ma_short_gap': 0,
                'ma_long_gap': 0,
                'ma_divergence': 0,
                'combined_gap': 0,
                'window_start': 0.0,
                'window_end': window_size,
                'is_first_segment': True
            })
            
            for start_idx in range(0, len(times), window_frames):
                end_idx = min(start_idx + window_frames, len(times) - 1)
                
                if end_idx - start_idx < window_frames // 2:
                    continue
                
                window_ma_short = ma_short[start_idx:end_idx]
                window_ma_long = ma_long[start_idx:end_idx]
                window_times = times[start_idx:end_idx]
                
                if len(window_ma_short) < 10:
                    continue
                
                ma_short_max_idx = np.argmax(window_ma_short)
                ma_short_min_idx = np.argmin(window_ma_short)
                ma_long_max_idx = np.argmax(window_ma_long)
                ma_long_min_idx = np.argmin(window_ma_long)
                
                ma_short_gap = window_ma_short[ma_short_max_idx] - window_ma_short[ma_short_min_idx]
                ma_long_gap = window_ma_long[ma_long_max_idx] - window_ma_long[ma_long_min_idx]
                
                ma_divergence = np.mean(np.abs(window_ma_short - window_ma_long))
                
                ma_short_changes = np.abs(np.diff(window_ma_short))
                ma_long_changes = np.abs(np.diff(window_ma_long))
                ma_combined_changes = 0.7 * ma_short_changes + 0.3 * ma_long_changes
                
                combined_gap = 0.4 * ma_short_gap + 0.3 * ma_long_gap + 0.3 * ma_divergence
                
                min_gap_threshold = 3.0
                min_divergence_threshold = 0.5
                
                if combined_gap < min_gap_threshold or ma_divergence < min_divergence_threshold:
                    continue
                
                if len(ma_combined_changes) > 0:
                    max_change_idx = np.argmax(ma_combined_changes)
                    segment_time = window_times[max_change_idx + 1]
                    
                    if not segment_starts or abs(segment_time - segment_starts[-1]) > window_size * 0.8:
                        segments.append({
                            'time': segment_time,
                            'ma_short_gap': ma_short_gap,
                            'ma_long_gap': ma_long_gap,
                            'ma_divergence': ma_divergence,
                            'combined_gap': combined_gap,
                            'window_start': window_times[0],
                            'window_end': window_times[-1]
                        })
                        segment_starts.append(segment_time)
            
            segments.append({
                'time': times[-1],
                'ma_short_gap': 0,
                'ma_long_gap': 0,
                'ma_divergence': 0,
                'combined_gap': 0,
                'window_start': times[-1],
                'window_end': times[-1]
            })
            
            segments.sort(key=lambda x: x['time'])
            
            print(f"Detected {len(segments)} segments using moving average gap analysis")
            
            for i, seg in enumerate(segments):
                print(f"Segment {i+1}: {seg['time']:.2f}s (ma_short_gap: {seg['ma_short_gap']:.2f}, ma_long_gap: {seg['ma_long_gap']:.2f}, divergence: {seg['ma_divergence']:.2f})")
            
            return segments
        
        segments = detect_segments_ma_gap(score_z, rms_db, times, duration, ma_short, ma_long)
        
        def fit_segments_to_tempo_points(segments, tempo_peaks, times):
            tempo_times = [times[p] for p, s, l, conf in tempo_peaks]
            duration = times[-1]
            internal_tempo_times = [t for t in tempo_times if t > 1.0 and t < duration - 1.0]
            
            print(f"Internal tempo peaks (excluding t0/tf): {len(internal_tempo_times)}")
            
            fitted_segments = []
            for i, seg in enumerate(segments[:-1]):
                seg_time = seg['time']
                
                if seg.get('is_first_segment', False) or seg_time == 0.0:
                    fitted_segments.append({
                        'time': 0.0,
                        'original_time': seg_time,
                        'ma_short_gap': seg['ma_short_gap'],
                        'ma_long_gap': seg['ma_long_gap'],
                        'ma_divergence': seg['ma_divergence'],
                        'combined_gap': seg['combined_gap'],
                        'window_start': seg['window_start'],
                        'window_end': seg['window_end'],
                        'fitted_to_tempo': False,
                        'is_first_segment': True
                    })
                    continue
                
                if internal_tempo_times:
                    closest_tempo_idx = np.argmin([abs(seg_time - t) for t in internal_tempo_times])
                    closest_tempo_time = internal_tempo_times[closest_tempo_idx]
                    
                    if abs(seg_time - closest_tempo_time) <= 5.0:
                        fitted_time = closest_tempo_time
                        fitted_segments.append({
                            'time': fitted_time,
                            'original_time': seg_time,
                            'ma_short_gap': seg['ma_short_gap'],
                            'ma_long_gap': seg['ma_long_gap'],
                            'ma_divergence': seg['ma_divergence'],
                            'combined_gap': seg['combined_gap'],
                            'window_start': seg['window_start'],
                            'window_end': seg['window_end'],
                            'fitted_to_tempo': True
                        })
                    else:
                        fitted_segments.append({
                            'time': seg_time,
                            'original_time': seg_time,
                            'ma_short_gap': seg['ma_short_gap'],
                            'ma_long_gap': seg['ma_long_gap'],
                            'ma_divergence': seg['ma_divergence'],
                            'combined_gap': seg['combined_gap'],
                            'window_start': seg['window_start'],
                            'window_end': seg['window_end'],
                            'fitted_to_tempo': False
                        })
                else:
                    fitted_segments.append({
                        'time': seg_time,
                        'original_time': seg_time,
                        'ma_short_gap': seg['ma_short_gap'],
                        'ma_long_gap': seg['ma_long_gap'],
                        'ma_divergence': seg['ma_divergence'],
                        'combined_gap': seg['combined_gap'],
                        'window_start': seg['window_start'],
                        'window_end': seg['window_end'],
                        'fitted_to_tempo': False
                    })
            
            fitted_segments.append(segments[-1])
            
            return fitted_segments
        
        fitted_segments = fit_segments_to_tempo_points(segments, tempo_peaks, times)
        
        print("\n" + "="*60)
        print("DUAL ANALYSIS SUMMARY")
        print("="*60)
        print(f"Tempo-based peaks (RED): {len(tempo_peaks)}")
        print(f"Original segments: {len(segments)}")
        print(f"Fitted segments (GREEN): {len(fitted_segments)}")
        
        fitted_count = sum(1 for seg in fitted_segments[:-1] if seg.get('fitted_to_tempo', False))
        print(f"Segments fitted to tempo points: {fitted_count}")
        print("="*60)
        
        return len(tempo_peaks), tempo_peaks, fitted_segments

    tempo_count, tempo_peaks, segments = dual_analysis_approach(all_peaks, times, times[-1], score_z, rms_db)
    
    selected_peaks = tempo_peaks

    if include_boundaries:
        if not selected_peaks or times[selected_peaks[0][0]] > 1.0:
            selected_peaks.insert(0, (0, score_z[0], 1.0, score_z[0]))
        
        end_idx = len(times) - 1
        if not selected_peaks or times[selected_peaks[-1][0]] < times[-1] - 1.0:
            selected_peaks.append((end_idx, score_z[-1], 1.0, score_z[-1]))

    final_peak_times = np.array([times[p] for p, s, l, conf in selected_peaks])
    final_peak_scores = np.array([s for p, s, l, conf in selected_peaks])

    order = np.argsort(final_peak_times)
    final_peak_times = final_peak_times[order]
    final_peak_scores = final_peak_scores[order]

    return final_peak_times, final_peak_scores, times, rms_db[:L], ma_short, ma_long, score_z, segments

def _beat_times(y, sr):
    """Extract beat times and tempo from audio."""
    tempo, bt = librosa.beat.beat_track(y=y, sr=sr, units="time")
    return tempo, np.asarray(bt)

def _extend_downbeats_to_edges(downbeats, duration):
    """Extend downbeat grid to cover full audio duration."""
    if len(downbeats) == 0:
        return np.array([0.0, duration])
    db = np.asarray(downbeats, dtype=float)
    bar = np.median(np.diff(db)) if len(db) > 1 else (duration / max(1, round(duration / 2.0)))
    t = db[0]
    back = []
    while t - bar > 0:
        t -= bar
        back.append(t)
    if t > 0:
        back.append(0.0)
    fwd = list(db)
    t = db[-1]
    while t + bar < duration:
        t += bar
        fwd.append(t)
    if fwd[-1] < duration:
        fwd.append(duration)
    grid = np.array(sorted(back) + fwd, dtype=float)
    grid = grid[np.r_[True, np.diff(grid) > 1e-3]]
    return grid

def _downbeats_from_beats(beat_times, prefer=(4,3), duration=None):
    """Extract downbeats from beat times using stable bar duration."""
    if len(beat_times) < 4:
        return np.array(beat_times)
    best_k, best_score, best = 4, -1e9, beat_times[::4]
    for k in prefer:
        cand = beat_times[::k]
        if len(cand) > 2:
            score = -np.std(np.diff(cand))
            if score > best_score:
                best_k, best_score, best = k, score, cand
    db = np.asarray(best)
    if duration is None:
        return db
    return _extend_downbeats_to_edges(db, duration)

def load_audio_file(audio_path: str, sr: int = 22050) -> Tuple[np.ndarray, int]:
    """Load audio from file path."""
    try:
        audio_data, sample_rate = librosa.load(audio_path, sr=sr)
        return audio_data, sample_rate
    except Exception as e:
        raise ValueError(f"Failed to load audio file {audio_path}: {e}")

def load_audio_bytes(data: bytes, sr: int = 22050) -> Tuple[np.ndarray, int]:
    """Load and preprocess audio from bytes."""
    y, file_sr = sf.read(io.BytesIO(data), always_2d=False, dtype='float32')
    if y.ndim > 1:
        y = np.mean(y, axis=1)
    if file_sr != sr:
        y = librosa.resample(y, orig_sr=file_sr, target_sr=sr)
    y = y.astype(np.float32)
    y = librosa.util.normalize(y)
    return y, sr

def extract_music_features(
    audio_data: np.ndarray,
    sample_rate: int,
    window_size: int = 1024,
    hop_length: int = 512
) -> Dict[str, Any]:
    """Extract comprehensive music features."""
    spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
    
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
    
    tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
    onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sample_rate)
    onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate)
    
    chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
    chroma_mean = np.mean(chroma, axis=1)
    
    tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
    tonnetz_mean = np.mean(tonnetz, axis=1)
    
    zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
    rms = librosa.feature.rms(y=audio_data)[0]
    
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
    
    return {
        "global_features": global_features,
        "segment_features": segment_features,
        "extraction_parameters": {
            "window_size": window_size,
            "hop_length": hop_length,
            "n_mfcc": 13
        }
    }

def analyze_audio(
    audio_input: Any,
    sr: int = 22050,
    hop: int = 512,
    create_plot: bool = False,
    audio_file: str = "audio.wav",
    use_precise_detection: bool = True,
    extract_features: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Unified audio analysis function supporting both file paths and bytes.
    
    Args:
        audio_input: Either a file path (str) or bytes data
        sr: Sample rate
        hop: Hop length for analysis
        create_plot: Whether to create visualization
        audio_file: Audio file name for display
        use_precise_detection: Use precise segment detection
        extract_features: Extract comprehensive music features
        **kwargs: Additional parameters for segmentation
    
    Returns:
        Dictionary containing analysis results
    """
    logger = _create_logger()
    
    if isinstance(audio_input, str):
        logger.info(f"Loading audio from file: {audio_input}")
        y, sr = load_audio_file(audio_input, sr)
    elif isinstance(audio_input, bytes):
        logger.info(f"Loading audio from bytes")
        y, sr = load_audio_bytes(audio_input, sr)
    else:
        raise ValueError("audio_input must be either a file path (str) or bytes")
    
    duration = len(y) / sr
    logger.info(f"Audio loaded: {duration:.2f} seconds at {sr} Hz")

    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    rms_t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    tempo, beat_times = _beat_times(y, sr)
    
    if use_precise_detection:
        try:
            print("🎵 Using PRECISE segment detection method...")
            peak_times, peak_scores, times, rms_db, ma_short, ma_long, score_z, segments = detect_music_segments_precise(
                y, sr,
                min_peaks=kwargs.get('min_peaks', 2),
                max_peaks=kwargs.get('max_peaks', None),
                window_size=kwargs.get('window_size', 2048),
                hop_length=hop,
                min_gap_seconds=kwargs.get('min_gap_seconds', 2.0),
                short_ma_sec=kwargs.get('short_ma_sec', 0.50),
                long_ma_sec=kwargs.get('long_ma_sec', 3.00),
                include_boundaries=kwargs.get('include_boundaries', True)
            )
            
            segments_all = np.array([seg['time'] for seg in segments])
            
            if len(segments_all) > 0 and segments_all[0] != 0.0:
                segments_all = np.concatenate([[0.0], segments_all])
            
            if len(segments_all) > 0 and segments_all[-1] != duration:
                segments_all = np.concatenate([segments_all, [duration]])
            
            segments_all = np.unique(segments_all)
            
            downbeats_full = _downbeats_from_beats(beat_times, duration=duration)
            
            debug = {
                "method": "precise_detection",
                "peak_times": peak_times.tolist(),
                "peak_scores": peak_scores.tolist(),
                "segments": [seg for seg in segments],
                "tempo": float(tempo),
                "beat_times": beat_times.tolist()
            }
            beat_energy_debug = None
            bar_novelty = None
            
        except Exception as e:
            logger.warning(f"Precise detection failed: {e}, falling back to simple segmentation")
            segments_all = np.array([0.0, duration])
            downbeats_full = _downbeats_from_beats(beat_times, duration=duration)
            debug = {"method": "fallback", "error": str(e)}
            beat_energy_debug = None
            bar_novelty = None
    else:
        segments_all = np.array([0.0, duration])
        downbeats_full = _downbeats_from_beats(beat_times, duration=duration)
        debug = {"method": "simple"}
        beat_energy_debug = None
        bar_novelty = None

    segment_lengths = []
    if len(segments_all) > 1:
        for i in range(len(segments_all) - 1):
            segment_lengths.append(segments_all[i+1] - segments_all[i])

    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    rms_db = np.nan_to_num(rms_db, nan=np.min(rms_db))

    segments_dict = {
        "segments": [
            {
                "start_time": float(segments_all[i]),
                "end_time": float(segments_all[i+1]),
                "duration": float(segments_all[i+1] - segments_all[i]),
                "segment_index": i
            }
            for i in range(len(segments_all) - 1)
        ],
        "peak_times": segments_all.tolist(),
        "tempo": float(tempo),
        "total_segments": len(segments_all) - 1
    }

    result = {
        "analysis_id": str(uuid.uuid4()),
        "analysis_timestamp": datetime.now().isoformat(),
        "analysis_type": "comprehensive",
        "duration": duration,
        "tempo": float(tempo),
        "segments_sec": segments_all.tolist(),
        "segments": segments_dict,
        "beat_times_sec": beat_times.tolist(),
        "downbeats_sec": downbeats_full.tolist(),
        "rms_energy": {
            "times": rms_t.tolist(),
            "values": rms_db.tolist(),
            "min_energy": float(np.min(rms_db)),
            "max_energy": float(np.max(rms_db))
        },
        "debug": {
            **debug,
            "num_segments": len(segments_all) - 1,
            "segment_lengths": segment_lengths
        }
    }

    if extract_features:
        logger.info("Extracting comprehensive music features")
        features = extract_music_features(y, sr, window_size=2048, hop_length=hop)
        result["features"] = features
        result["visualization_data"] = {
            "times": rms_t.tolist(),
            "spectral_centroids": features["segment_features"]["spectral_centroids"],
            "spectral_rolloff": features["segment_features"]["spectral_rolloff"],
            "mfccs": features["segment_features"]["mfccs"],
            "rms": features["segment_features"]["rms"],
            "duration": duration,
            "sample_rate": sr,
            "hop_length": hop
        }

    if create_plot:
        fig = create_visualization(y, sr, rms_t, rms, beat_times, downbeats_full, segments_all, bar_novelty, audio_file, beat_energy_debug)
        if fig is not None:
            result["plot"] = fig

    return result

def analyze_audio_file(audio_path: str, **kwargs) -> Dict[str, Any]:
    """Analyze audio from file path."""
    return analyze_audio(audio_path, **kwargs)

def analyze_audio_bytes(data: bytes, **kwargs) -> Dict[str, Any]:
    """Analyze audio from bytes."""
    return analyze_audio(data, **kwargs)

def analyze_and_plot(audio_input: Any, audio_file: str = "audio.wav", output_dir: str = ".", **kwargs):
    """Analyze audio and save visualization plot."""
    result = analyze_audio(audio_input, create_plot=True, audio_file=audio_file, **kwargs)

    if "plot" in result and _import_matplotlib():
        fig = result["plot"]
        output_image = os.path.join(output_dir, f"bar_level_analysis_{os.path.splitext(os.path.basename(audio_file))[0]}.png")
        fig.savefig(output_image, dpi=300, bbox_inches='tight')
        plt.close(fig)
        result["plot_saved"] = output_image
        del result["plot"]
    else:
        print("⚠️ Plot not created - matplotlib not available")

    return result

class UnifiedMusicAnalyzer:
    """Unified music analyzer with sync and async support."""
    
    def __init__(self):
        self.logger = _create_logger("UnifiedMusicAnalyzer")
    
    def analyze_audio_file(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Synchronous analysis from file path."""
        return analyze_audio_file(audio_path, **kwargs)
    
    def analyze_audio_bytes(self, data: bytes, **kwargs) -> Dict[str, Any]:
        """Synchronous analysis from bytes."""
        return analyze_audio_bytes(data, **kwargs)
    
    async def analyze_audio_file_async(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Asynchronous analysis from file path."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, analyze_audio_file, audio_path, **kwargs)
    
    async def analyze_audio_bytes_async(self, data: bytes, **kwargs) -> Dict[str, Any]:
        """Asynchronous analysis from bytes."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, analyze_audio_bytes, data, **kwargs)

def create_visualization(y, sr, rms_t, rms, beat_times, downbeats, segments, bar_novelty, audio_file="audio.wav", beat_energy_debug=None):
    """Create visualization for audio segmentation analysis"""
    if not _import_matplotlib():
        print("⚠️ Matplotlib not available, skipping visualization")
        return None
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))

    rms_db = 20 * np.log10(rms + 1e-9)

    ax1.plot(rms_t, rms_db, 'b-', alpha=0.7, label='RMS Energy (dB)')

    if len(beat_times) > 0:
        for i, beat_time in enumerate(beat_times):
            ax1.axvline(x=beat_time, color='purple', alpha=0.3, linewidth=0.5, linestyle='--',
                       label='Beats' if i == 0 else "")

    if len(segments) > 0:
        for i, seg_time in enumerate(segments):
            ax1.axvline(x=seg_time, color='green', alpha=0.8, linewidth=2,
                       label='Segments' if i == 0 else "")
            ax1.text(seg_time, ax1.get_ylim()[1] * 0.9, f'S{i+1}',
                    ha='center', va='bottom', fontsize=8, color='green', weight='bold')

    ax1.set_ylabel('RMS Energy (dB)')
    ax1.set_title(f'Audio Segmentation - {os.path.basename(audio_file)}')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    if len(beat_times) > 0:
        beat_energy = np.interp(beat_times, rms_t, rms_db)
        ax2.scatter(beat_times, beat_energy, color='orange', s=30, alpha=0.6,
                   label='Beats', marker='|', linewidth=2)

        if len(downbeats) > 0:
            downbeat_energy = np.interp(downbeats, rms_t, rms_db)
            ax2.scatter(downbeats, downbeat_energy, color='purple', s=80, alpha=0.9,
                       label='Downbeats', marker='o', zorder=5)

        if len(segments) > 0:
            for seg_time in segments:
                ax2.axvline(x=seg_time, color='green', alpha=0.5, linewidth=1, linestyle='--')
    else:
        ax2.plot(rms_t, rms_db, 'b-', alpha=0.7, label='RMS Energy')

    ax2.set_ylabel('Energy (dB)')
    ax2.set_title('Beat Tracking')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    if beat_energy_debug and "beat_times" in beat_energy_debug:
        beat_times_energy = np.array(beat_energy_debug["beat_times"])
        beat_energy = np.array(beat_energy_debug.get("E", []))
        spread = np.array(beat_energy_debug.get("spread", []))

        if len(beat_times_energy) > 0 and len(beat_energy) > 0:
            min_len = min(len(beat_times_energy), len(beat_energy))
            ax3.plot(beat_times_energy[:min_len], beat_energy[:min_len], 'b-', alpha=0.6, linewidth=1, label='Beat Energy')
            if len(spread) > 0:
                min_len_spread = min(len(beat_times_energy), len(spread))
                ax3.plot(beat_times_energy[:min_len_spread], spread[:min_len_spread], 'purple', alpha=0.7, linewidth=1.5, label='Spread')

            if len(segments) > 0:
                for seg_time in segments:
                    ax3.axvline(x=seg_time, color='green', alpha=0.8, linewidth=2)

            ax3.set_ylabel('Energy / Spread')
            ax3.set_title('Beat Energy Analysis')
    elif bar_novelty and len(bar_novelty) > 1:
        bar_times, novelty_scores = bar_novelty
        if len(bar_times) > 0 and len(novelty_scores) > 0:
            min_len = min(len(bar_times), len(novelty_scores))
            ax3.plot(bar_times[:min_len], novelty_scores[:min_len], 'c-', alpha=0.8, linewidth=2,
                    label='Bar Novelty')

            if len(segments) > 0:
                for seg_time in segments:
                    ax3.axvline(x=seg_time, color='green', alpha=0.8, linewidth=2)

            ax3.set_ylabel('Novelty Score')
            ax3.set_title('Bar-Level Novelty')
    else:
        ax3.plot(rms_t, rms_db, 'b-', alpha=0.7, label='RMS Energy')
        ax3.set_ylabel('Energy (dB)')
        ax3.set_title('RMS Energy')

    ax3.set_xlabel('Time (seconds)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

__all__ = [
    "UnifiedMusicAnalyzer",
    "analyze_audio",
    "analyze_audio_file",
    "analyze_audio_bytes",
    "analyze_and_plot",
    "extract_music_features",
    "load_audio_file",
    "load_audio_bytes"
]

