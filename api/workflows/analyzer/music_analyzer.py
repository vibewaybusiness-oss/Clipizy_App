import io
import os
from functools import lru_cache

import librosa
import numpy as np
import ruptures as rpt
import soundfile as sf
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, savgol_filter

# Optional matplotlib import for visualization
MATPLOTLIB_AVAILABLE = False
plt = None

# Only try to import matplotlib if we're actually going to use it
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

# =============================================================================
# IMPROVED SEGMENT DETECTION (Based on MusicAnalyzerPeaks_fromgit.py)
# =============================================================================

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

    # MULTI-LEVEL PEAK DETECTION
    def find_peaks_multi_level(score_z, times, rms_db, base_thr):
        all_peaks = []
        
        # Level 1: High confidence peaks
        peaks1, props1 = find_peaks(
            score_z,
            height=base_thr,
            distance=min_dist_frames,
            prominence=np.std(score_z) * 0.6
        )
        all_peaks.extend([(p, score_z[p], 1.0) for p in peaks1])
        
        # Level 2: Medium confidence peaks (lower threshold)
        peaks2, props2 = find_peaks(
            score_z,
            height=base_thr * 0.7,
            distance=max(1, min_dist_frames // 2),
            prominence=np.std(score_z) * 0.3
        )
        # Filter out peaks too close to level 1 peaks
        for p in peaks2:
            if all(abs(times[p] - times[existing_p]) >= min_gap_seconds 
                   for existing_p, _, _ in all_peaks):
                all_peaks.append((p, score_z[p], 0.7))
        
        # Level 3: Energy-based peaks in high-energy regions
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
    
    # DUAL ANALYSIS: TEMPO PEAKS + SEGMENT DETECTION
    def dual_analysis_approach(peaks, times, duration, score_z, rms_db):
        if not peaks:
            return min_peaks, [], []
        
        # Sort by confidence (score * level)
        peaks_with_confidence = [(p, s, l, s * l) for p, s, l in peaks]
        peaks_with_confidence.sort(key=lambda x: x[3], reverse=True)
        
        print("="*60)
        print("STAGE 1: TEMPO-BASED PEAKS (RED)")
        print("="*60)
        
        # STAGE 1: TEMPO-BASED PEAKS (KEEP THESE)
        def get_tempo_peaks(score_z, rms_db, times, duration):
            # Calculate tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
            try:
                tempo = float(tempo)
            except Exception:
                tempo = 120.0  # Default tempo
            
            print(f"Detected tempo: {tempo:.1f} BPM")
            
            # Calculate tempo-based phrase length (more sensitive)
            if tempo > 0:
                seconds_per_beat = 60.0 / tempo
                # Use 4-beat phrases for more tempo peaks (increased sensitivity)
                phrase_length = seconds_per_beat * 4
            else:
                phrase_length = 6.0  # Default 6 seconds (more sensitive)
            
            # Calculate tempo-based peak count
            tempo_based_count = max(5, int(duration / phrase_length))
            
            print(f"Tempo-based phrase length: {phrase_length:.2f} seconds")
            print(f"Tempo-based peak count: {tempo_based_count}")
            
            # Select tempo peaks from available peaks
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
        
        # STAGE 2: MOVING AVERAGE GAP SEGMENT DETECTION
        def detect_segments_ma_gap(score_z, rms_db, times, duration, ma_short, ma_long):
            # Calculate window size for analysis (adaptive based on duration, less sensitive)
            window_size = max(8.0, duration / 15.0)  # 15 windows across duration (larger windows)
            window_frames = int(window_size * sr / hop_length)
            
            print(f"Using window size: {window_size:.2f} seconds")
            print("Using moving average values for gap calculation")
            
            # Find local maxima and minima in each window using moving averages
            segments = []
            segment_starts = [0]  # Always start with beginning
            
            # Add the first segment starting at 0.0 to ensure we don't have an empty first segment
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
                
                if end_idx - start_idx < window_frames // 2:  # Skip too small windows
                    continue
                
                # Extract window data using moving averages
                window_ma_short = ma_short[start_idx:end_idx]
                window_ma_long = ma_long[start_idx:end_idx]
                window_times = times[start_idx:end_idx]
                
                if len(window_ma_short) < 10:  # Skip very small windows
                    continue
                
                # Find local maxima and minima in moving averages
                ma_short_max_idx = np.argmax(window_ma_short)
                ma_short_min_idx = np.argmin(window_ma_short)
                ma_long_max_idx = np.argmax(window_ma_long)
                ma_long_min_idx = np.argmin(window_ma_long)
                
                # Calculate max-min gaps using moving averages
                ma_short_gap = window_ma_short[ma_short_max_idx] - window_ma_short[ma_short_min_idx]
                ma_long_gap = window_ma_long[ma_long_max_idx] - window_ma_long[ma_long_min_idx]
                
                # Calculate MA divergence (difference between short and long MA)
                ma_divergence = np.mean(np.abs(window_ma_short - window_ma_long))
                
                # Calculate MA change rates
                ma_short_changes = np.abs(np.diff(window_ma_short))
                ma_long_changes = np.abs(np.diff(window_ma_long))
                ma_combined_changes = 0.7 * ma_short_changes + 0.3 * ma_long_changes
                
                # Combined gap score using moving average metrics (more selective)
                combined_gap = 0.4 * ma_short_gap + 0.3 * ma_long_gap + 0.3 * ma_divergence
                
                # Apply minimum threshold for segment detection (reduce sensitivity)
                min_gap_threshold = 3.0  # Minimum combined gap to consider
                min_divergence_threshold = 0.5  # Minimum divergence to consider
                
                if combined_gap < min_gap_threshold or ma_divergence < min_divergence_threshold:
                    continue  # Skip this window if not significant enough
                
                # Find the most significant transition point in this window
                # Look for the point with highest MA change
                if len(ma_combined_changes) > 0:
                    max_change_idx = np.argmax(ma_combined_changes)
                    segment_time = window_times[max_change_idx + 1]  # +1 because of diff
                    
                    # More selective: require larger gaps between segments
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
            
            # Add end point
            segments.append({
                'time': times[-1],
                'ma_short_gap': 0,
                'ma_long_gap': 0,
                'ma_divergence': 0,
                'combined_gap': 0,
                'window_start': times[-1],
                'window_end': times[-1]
            })
            
            # Sort segments by time
            segments.sort(key=lambda x: x['time'])
            
            print(f"Detected {len(segments)} segments using moving average gap analysis")
            
            # Print segment information
            for i, seg in enumerate(segments):
                print(f"Segment {i+1}: {seg['time']:.2f}s (ma_short_gap: {seg['ma_short_gap']:.2f}, ma_long_gap: {seg['ma_long_gap']:.2f}, divergence: {seg['ma_divergence']:.2f})")
            
            return segments
        
        segments = detect_segments_ma_gap(score_z, rms_db, times, duration, ma_short, ma_long)
        
        # FIT SEGMENTS TO TEMPO POINTS (excluding t0 and tf)
        def fit_segments_to_tempo_points(segments, tempo_peaks, times):
            # Extract tempo peak times (excluding boundary points t0 and tf)
            tempo_times = [times[p] for p, s, l, conf in tempo_peaks]
            
            # Filter out boundary points (t0 and tf)
            duration = times[-1]
            internal_tempo_times = [t for t in tempo_times if t > 1.0 and t < duration - 1.0]
            
            print(f"Internal tempo peaks (excluding t0/tf): {len(internal_tempo_times)}")
            
            # Fit segments to internal tempo points
            fitted_segments = []
            for i, seg in enumerate(segments[:-1]):  # Exclude the last segment (tf)
                seg_time = seg['time']
                
                # Special handling for the first segment - always keep it at 0.0
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
                
                # Find the closest internal tempo peak to this segment
                if internal_tempo_times:
                    closest_tempo_idx = np.argmin([abs(seg_time - t) for t in internal_tempo_times])
                    closest_tempo_time = internal_tempo_times[closest_tempo_idx]
                    
                    # Only use tempo point if it's reasonably close (within 5 seconds)
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
                        # Keep original segment if no close tempo point
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
                    # No internal tempo points, keep original
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
            
            # Add the end point (tf) as the last segment
            fitted_segments.append(segments[-1])
            
            return fitted_segments
        
        fitted_segments = fit_segments_to_tempo_points(segments, tempo_peaks, times)
        
        print("\n" + "="*60)
        print("DUAL ANALYSIS SUMMARY")
        print("="*60)
        print(f"Tempo-based peaks (RED): {len(tempo_peaks)}")
        print(f"Original segments: {len(segments)}")
        print(f"Fitted segments (GREEN): {len(fitted_segments)}")
        
        # Count how many segments were fitted to tempo points
        fitted_count = sum(1 for seg in fitted_segments[:-1] if seg.get('fitted_to_tempo', False))
        print(f"Segments fitted to tempo points: {fitted_count}")
        print("="*60)
        
        # Return both tempo peaks and fitted segments
        return len(tempo_peaks), tempo_peaks, fitted_segments

    # Get both tempo peaks and segments
    tempo_count, tempo_peaks, segments = dual_analysis_approach(all_peaks, times, times[-1], score_z, rms_db)
    
    # Use tempo peaks as the main selection
    selected_peaks = tempo_peaks

    # ADD BOUNDARY POINTS IF REQUESTED
    if include_boundaries:
        # Add start point (t0)
        if not selected_peaks or times[selected_peaks[0][0]] > 1.0:
            selected_peaks.insert(0, (0, score_z[0], 1.0, score_z[0]))
        
        # Add end point (tf)
        end_idx = len(times) - 1
        if not selected_peaks or times[selected_peaks[-1][0]] < times[-1] - 1.0:
            selected_peaks.append((end_idx, score_z[-1], 1.0, score_z[-1]))

    # EXTRACT FINAL RESULTS
    final_peak_times = np.array([times[p] for p, s, l, conf in selected_peaks])
    final_peak_scores = np.array([s for p, s, l, conf in selected_peaks])

    # SORT BY TIME
    order = np.argsort(final_peak_times)
    final_peak_times = final_peak_times[order]
    final_peak_scores = final_peak_scores[order]

    return final_peak_times, final_peak_scores, times, rms_db[:L], ma_short, ma_long, score_z, segments

# =============================================================================
# CORE SEGMENTATION FUNCTIONS
# =============================================================================

def _beat_times(y, sr):
    """Extract beat times and tempo from audio."""
    tempo, bt = librosa.beat.beat_track(y=y, sr=sr, units="time")
    return tempo, np.asarray(bt)

# --- helper: extend downbeats to the audio edges -----------------

def _extend_downbeats_to_edges(downbeats, duration):
    """Extend downbeat grid to cover full audio duration."""
    if len(downbeats) == 0:
        return np.array([0.0, duration])
    db = np.asarray(downbeats, dtype=float)
    # robust bar duration
    bar = np.median(np.diff(db)) if len(db) > 1 else (duration / max(1, round(duration / 2.0)))
    # extend backwards
    t = db[0]
    back = []
    while t - bar > 0:
        t -= bar
        back.append(t)
    if t > 0:
        back.append(0.0)
    # extend forwards
    fwd = list(db)
    t = db[-1]
    while t + bar < duration:
        t += bar
        fwd.append(t)
    if fwd[-1] < duration:
        fwd.append(duration)
    grid = np.array(sorted(back) + fwd, dtype=float)
    # dedupe/monotone
    grid = grid[np.r_[True, np.diff(grid) > 1e-3]]
    return grid

def _downbeats_from_beats(beat_times, prefer=(4,3), duration=None):
    """Extract downbeats from beat times using stable bar duration."""
    if len(beat_times) < 4:
        return np.array(beat_times)
    # pick k (beats/bar) with the most stable bar duration
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
    # extend to [0, duration]
    return _extend_downbeats_to_edges(db, duration)


def _average_close_boundaries(
    times: np.ndarray,
    min_gap_sec: float,
    beat_times: np.ndarray = None,
    rms_t: np.ndarray = None,
    rms: np.ndarray = None,
    snap_window_sec: float = 1.0,
    beat_snap_sec: float = 0.25
    ) -> np.ndarray:
    """Merge boundaries that are too close by averaging them."""
    if len(times) <= 1:
        return times.astype(float)

    t = list(times.astype(float))
    out = []
    i = 0

    def snap_to_best_position(t0):
        """Snap time to RMS dip and nearest beat."""
        if rms_t is not None and rms is not None:
            i0 = np.searchsorted(rms_t, max(0.0, t0 - snap_window_sec))
            i1 = np.searchsorted(rms_t, t0 + snap_window_sec)
            if i1 > i0:
                inv = 1.0 - (rms / (np.max(rms) + 1e-9))
                k = i0 + int(np.argmax(inv[i0:i1]))
                t0 = float(rms_t[k])

        if beat_times is not None and len(beat_times):
            future = beat_times[beat_times >= t0]
            if len(future) and (future[0] - t0) <= beat_snap_sec:
                return float(future[0])
            return float(beat_times[np.argmin(np.abs(beat_times - t0))])
        return t0

    while i < len(t):
        if i == len(t) - 1:
            out.append(t[i])
            break

        if t[i+1] - t[i] < min_gap_sec:
            j = i + 1
            while j + 1 < len(t) and (t[j+1] - t[j] < min_gap_sec):
                j += 1
            avg = 0.5 * (t[i] + t[j])
            out.append(snap_to_best_position(avg))
            i = j + 1
        else:
            out.append(t[i])
            i += 1

    return np.array(sorted(np.unique(np.round(out, 6))), float)

# --- bar novelty (also returns a complete downbeat grid) ---------

def _bar_novelty_with_grid(y, sr, duration, prefer_meters=(3,4)):
    """Compute bar-level novelty scores for segmentation."""
    # beat-synced features (chroma + MFCC over beats)
    hop = 512
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))**2
    mel = librosa.feature.melspectrogram(S=S, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    mfcc  = librosa.feature.mfcc(S=librosa.power_to_db(mel), sr=sr, n_mfcc=13)
    tempo, bt = librosa.beat.beat_track(y=y, sr=sr, units="time")
    if len(bt) < 3:
        return np.array([]), np.array([]), np.array([0.0, duration])

    bf = librosa.time_to_frames(bt, sr=sr, hop_length=hop)
    sync = lambda X: librosa.util.sync(X, bf, aggregate=np.mean)
    Fb = np.vstack([sync(chroma), sync(mfcc)]).T  # (T_beats × D)

    # pick beats-per-bar by stability of bar duration
    best_k, best_score, best_grid = 4, -np.inf, None
    for k in prefer_meters:
        cand = bt[::k]
        if len(cand) < 3:
            continue
        score = -np.std(np.diff(cand))  # stable bar duration
        if score > best_score:
            best_k, best_score, best_grid = k, score, cand
    downbeats = best_grid if best_grid is not None else bt[::4]

    # extend downbeats to edges [0, duration]
    downbeats_full = _extend_downbeats_to_edges(downbeats, duration)

    # compute bar-level means
    bar_idx = np.searchsorted(downbeats_full, bt, side="right") - 1
    n_bars  = int(bar_idx.max()) + 1
    D = Fb.shape[1]
    B = np.zeros((n_bars, D))
    counts = np.zeros(n_bars) + 1e-9
    for i,b in enumerate(bar_idx):
        if 0 <= b < n_bars:
            B[b] += Fb[i]
            counts[b] += 1
    B /= counts[:,None]

    # novelty between adjacent bars -> attached to internal boundaries
    diff = np.linalg.norm(B[1:] - B[:-1], axis=1)
    if len(diff) >= 7:
        # light smoothing
        w = max(5, ((len(diff)//20)*2)+1)
        diff = savgol_filter(diff, w, 3, mode="interp")
    diff = (diff - diff.min()) / (diff.max() - diff.min() + 1e-9)

    # internal boundaries & scores
    boundary_times = downbeats_full[1:-1]
    # Ensure novelty array matches boundary_times length
    min_len = min(len(boundary_times), len(diff))
    boundary_times = boundary_times[:min_len]
    novelty = diff[:min_len]
    return boundary_times, novelty, downbeats_full

# =============================================================================
# BEAT ENERGY SEGMENTATION
# =============================================================================

def _beat_energy(y, sr, hop=512):
    """Compute beat-synchronous energy for segmentation."""
    tempo, bt = _beat_times(y, sr)
    if len(bt) < 3:
        # fallback to fixed 0.5s bins
        step = 0.5
        bt = np.arange(0, len(y)/sr + step, step)
    # frame energies
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))**2
    pow_t = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop)
    pow_sum = S.sum(axis=0)  # broadband power
    # integrate per beat interval by summing frames inside (b[i-1], b[i]]
    e = []
    for i in range(1, len(bt)):
        m = (pow_t > bt[i-1]) & (pow_t <= bt[i])
        e.append(pow_sum[m].sum())
    e = np.array(e, dtype=float)
    # log scale and normalize
    e = np.log1p(e)
    e = (e - e.min()) / (e.max() - e.min() + 1e-9)
    # align to beats from index 1..K-1
    return bt[1:], e

def _calculate_beat_energy_for_times(y, sr, beat_times, hop=512):
    """Calculate beat energy for specific beat times."""
    if len(beat_times) < 3:
        return np.array([])

    # frame energies
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))**2
    pow_t = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop)
    pow_sum = S.sum(axis=0)  # broadband power

    # integrate per beat interval by summing frames inside (b[i-1], b[i]]
    e = []
    for i in range(1, len(beat_times)):
        m = (pow_t > beat_times[i-1]) & (pow_t <= beat_times[i])
        e.append(pow_sum[m].sum())
    e = np.array(e, dtype=float)

    # log scale and normalize
    e = np.log1p(e)
    e = (e - e.min()) / (e.max() - e.min() + 1e-9)

    return e

def _moving_average(x, n):
    """Apply moving average filter to signal."""
    if n <= 1:
        return x.copy()
    k = np.ones(n)/n
    y = np.convolve(x, k, mode="same")
    y[:n//2] = y[n//2]
    y[-n//2:] = y[-n//2-1]
    return y

def _merge_close_boundaries(
    cut_times: np.ndarray,
    beat_times: np.ndarray,
    rms_t: np.ndarray,
    rms: np.ndarray,
    med_beat: float,
    beats_per_bar: int = 4,
    closeness: float = 0.95,
    min_beats_between: int = 1,
    snap_window_bars: float = 0.75,
    beat_snap: float = 0.25,
    prefer: str = "median"
    ) -> np.ndarray:
    """Merge boundaries that are too close together."""
    if len(cut_times) <= 1:
        return cut_times

    def beats_apart(t0, t1):
        return abs(t1 - t0) / max(med_beat, 1e-6)

    bar_len = beats_per_bar * med_beat
    thr_time = closeness * bar_len

    # Cluster close boundaries
    clusters, cur = [], [cut_times[0]]
    for t in cut_times[1:]:
        if (t - cur[-1] < thr_time) or (beats_apart(t, cur[-1]) <= min_beats_between):
            cur.append(t)
        else:
            clusters.append(cur)
            cur = [t]
    clusters.append(cur)

    # RMS preparation for snapping
    inv = 1.0 - (rms / (np.max(rms) + 1e-9))
    half_w = max(med_beat * snap_window_bars * beats_per_bar / 2.0, med_beat)

    def snap_to_dip_and_beat(t):
        i0 = np.searchsorted(rms_t, max(0.0, t - half_w))
        i1 = np.searchsorted(rms_t, t + half_w)
        if i1 > i0:
            k = i0 + int(np.argmax(inv[i0:i1]))
            t = float(rms_t[k])

        future = beat_times[beat_times >= t]
        if len(future) and (future[0] - t) <= beat_snap:
            return float(future[0])
        return float(beat_times[np.argmin(np.abs(beat_times - t))])

    # Merge clusters
    merged = []
    for cluster in clusters:
        if len(cluster) == 1:
            t = cluster[0]
        elif len(cluster) == 2:
            t = float(np.mean(cluster)) if prefer == "mean" else float(np.median(cluster))
        else:
            # Choose position with strongest RMS dip
            local_means = [np.mean(rms[np.searchsorted(rms_t, max(0.0, ti - half_w)):
                                     np.searchsorted(rms_t, ti + half_w)]) for ti in cluster]
            idx = int(np.argmin(local_means))
            t = float(cluster[idx])
        merged.append(snap_to_dip_and_beat(t))

    # Remove boundaries that are still too close
    merged = np.array(sorted(np.unique(np.round(merged, 6))), float)
    keep = [merged[0]]
    for t in merged[1:]:
        if beats_apart(t, keep[-1]) >= max(1, min_beats_between):
            keep.append(t)
    return np.array(keep, float)

def segments_from_beat_energy_pro(
    y, sr,
    short_ma_beats=4,
    long_ma_beats=16,
    min_gap_seconds=11.0,
    max_gap_seconds=45.0,
    keep_quantile=0.62,
    max_segments=11,
    pelt_penalty=4.5,
    binseg_n_bkps=18,
    beat_times=None
    ):
    """Segment audio using beat energy analysis with changepoint detection."""
    duration = len(y) / sr

    # Use provided beat times or calculate new ones
    if beat_times is not None:
        bt = np.array(beat_times)
        # Calculate beat energy for the provided beat times
        E = _calculate_beat_energy_for_times(y, sr, bt)
    else:
        bt, E = _beat_energy(y, sr)

    if len(bt) < long_ma_beats + 4:
        return np.array([0.0, duration]), {"beat_times": bt.tolist(), "E": E.tolist()}

    S = _moving_average(E, short_ma_beats)
    L = _moving_average(E, long_ma_beats)
    spread = S - L

    def nrm(x):
        x = (x - np.min(x)) / (np.max(x) - np.min(x) + 1e-9)
        return x
    E_n, spread_n = nrm(E), nrm(spread)

    med_beat = float(np.median(np.diff(bt)))
    min_gap_beats = max(2, int(round(min_gap_seconds / max(med_beat, 1e-6))))
    max_gap_beats = max(min_gap_beats + 1, int(round(max_gap_seconds / max(med_beat, 1e-6))))

    Z = np.vstack([E_n, spread_n]).T
    pelt = rpt.Pelt(model="rbf", min_size=min_gap_beats).fit(Z)
    cps_pelt = np.array(pelt.predict(pen=pelt_penalty))[:-1]

    binseg = rpt.Binseg(model="l2", min_size=min_gap_beats).fit(E_n.reshape(-1, 1))
    # Ensure n_bkps is valid for the data length
    max_possible_bkps = max(1, (len(Z) - 2 * min_gap_beats) // min_gap_beats)
    n_bkps = min(binseg_n_bkps, max_possible_bkps)
    if n_bkps <= 0:
        cps_bin = np.array([])
    else:
        cps_bin = np.array(binseg.predict(n_bkps=n_bkps))[:-1]

    # --- NEW: zero-cross/large-slope heuristic on spread ---
    dspread = np.diff(spread)
    zc_idx = np.where((spread[:-1] <= 0) & (spread[1:] > 0) & (np.abs(dspread) > np.quantile(np.abs(dspread), 0.75)))[0] + 1

    cand = np.unique(np.clip(np.r_[cps_pelt, cps_bin, zc_idx], 1, len(bt)-2))

    # scoring
    def window_means(c, w):
        L0, R0 = max(0, c - w), c - 1
        R1, R2 = c, min(len(bt)-1, c + w - 1)
        mEL = E_n[L0:R0+1].mean(); mER = E_n[R1:R2+1].mean()
        mSL = spread_n[L0:R0+1].mean(); mSR = spread_n[R1:R2+1].mean()
        return abs(mER - mEL), abs(mSR - mSL)

    scores = []
    wctx = min_gap_beats  # context window
    for c in cand:
        dE, dS = window_means(int(c), wctx)
        local = abs(E_n[max(0, c-1)] - E_n[min(len(E_n)-1, c+1)])
        scores.append(0.55*dE + 0.35*dS + 0.10*local)
    scores = np.array(scores) if len(cand) else np.array([])

    kept = []
    if len(cand):
        thresh = np.quantile(scores, keep_quantile)
        order = np.argsort(-scores)
        for k in order:
            if scores[k] < thresh: break
            c = int(cand[k])
            if any(abs(c - j) < min_gap_beats for j in kept):
                continue
            kept.append(c)
            if len(kept) >= max_segments: break
        kept = sorted(kept)

    # Convert kept indices → times
    cuts = bt[np.array(kept, dtype=int)] if len(kept) else np.array([])

    # --- NEW: merge boundaries that are too close (≈ same bar) ---
    # compute RMS once for snapping
    hop = 512
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    rms_t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)

    cuts = _merge_close_boundaries(
        cut_times=cuts,
        beat_times=bt,
        rms_t=rms_t,
        rms=rms,
        med_beat=np.median(np.diff(bt)),
        beats_per_bar=4,
        closeness=0.95,          # ~one bar
        min_beats_between=1,     # avoid successive bars
        snap_window_bars=0.75,
        beat_snap=0.25,
        prefer="median"
    )

    # Average/merge close boundaries (do NOT drop)
    cuts = _average_close_boundaries(
        cuts,
        min_gap_sec=min_gap_seconds,
        beat_times=bt,
        rms_t=rms_t, rms=rms,
        snap_window_sec=0.75 * 4 * np.median(np.diff(bt)),  # ~¾ bar window
        beat_snap_sec=0.25
    )

    # convert + backfill
    def beats_to_segments(indices):
        cuts = indices if len(indices) else np.array([])
        return np.array(np.r_[0.0, cuts, duration], float)

    segs = beats_to_segments(cuts)

    def backfill_once(segs):
        gaps = np.diff(segs)
        i = int(np.argmax(gaps))
        if gaps[i] <= max_gap_seconds + 1e-6:
            return segs, False
        t0, t1 = segs[i], segs[i+1]
        inside = np.where((bt > t0 + 0.5*med_beat) & (bt < t1 - 0.5*med_beat))[0]
        if len(inside) == 0: return segs, False
        # pick best candidate inside by score; if none, use steepest |dspread|
        mask = (bt[cand] > t0) & (bt[cand] < t1)
        if np.any(mask):
            j = int(cand[mask][np.argmax(scores[mask])])
        else:
            j = inside[:-1][np.argmax(np.abs(dspread[inside[:-1]]))]
        return np.sort(np.r_[segs, bt[j]]), True

    while len(segs) - 2 < max_segments:
        segs, changed = backfill_once(segs)
        if not changed: break

    # Optional: tidy after backfill
    cuts = segs[1:-1]  # extract internal boundaries
    if len(cuts) > 0:
        cuts = _average_close_boundaries(
            cuts, min_gap_sec=min_gap_seconds, beat_times=bt, rms_t=rms_t, rms=rms,
            snap_window_sec=0.75 * 4 * np.median(np.diff(bt)), beat_snap_sec=0.25
        )
        segs = np.array(np.r_[0.0, cuts, duration], float)

    # Clamp segments to [0, duration] and ensure uniqueness
    segs = np.clip(segs, 0.0, duration)
    segs = np.unique(np.round(segs, 6))  # 1ms tolerance for uniqueness

    # FINAL BEAT SNAPPING: Snap segments to closest beats before returning
    segs = snap_segments_to_beats(segs, bt, snap_threshold=0.5)

    return segs, {
        "beat_times": bt.tolist(),
        "E": E.tolist(),
        "short_ma": S.tolist(),
        "long_ma": L.tolist(),
        "spread": spread.tolist(),
        "candidates_beats": (cand.tolist() if len(cand) else []),
        "candidate_scores": (scores.tolist() if len(scores) else []),
        "kept_beats": (kept if isinstance(kept, list) else kept.tolist()),
        "zero_crossings": (zc_idx.tolist() if len(cand) else []),
        "merged_boundaries": cuts.tolist(),
        "boundary_merging": {
            "original_count": len(kept),
            "merged_count": len(cuts),
            "clusters_merged": len(kept) - len(cuts) if len(kept) > len(cuts) else 0
        }
    }

# --- sparse selector using peaks + minima + DP + NMS -------------

def bar_level_segments(
    y, sr, duration,
    min_segment_seconds=14.0,
    max_segment_seconds=55.0,
    target_segments=6,
    max_segments=8,
    hi_q=0.70,
    lo_q=0.35,
    penalty_hi=1.6,
    nms_bar_gap=1,
    w_novelty=0.6, w_energy=0.25, w_flux=0.15,
    beat_times=None
    ):
    """Segment audio using bar-level novelty analysis."""
    # --- bar candidates & novelty ---
    b_times, nov, downbeats_full = _bar_novelty_with_grid(y, sr, duration)
    if len(b_times) == 0:
        return np.array([0.0, duration]), downbeats_full, {"novelty": [], "picked": []}

    # --- derive bars <-> seconds ---
    bar_len = np.median(np.diff(downbeats_full))
    min_bars = max(3, int(round(min_segment_seconds / max(bar_len, 1e-6))))
    max_bars = max(min_bars + 1, int(round(max_segment_seconds / max(bar_len, 1e-6))))

    # --- auxiliary bar-wise signals: energy jump & percussive flux ---
    # bar energies (RMS per bar) on the same grid used in _bar_novelty_with_grid
    hop = 512
    import librosa
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    t_rms = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    # bar mean RMS
    b_idx = np.searchsorted(downbeats_full, t_rms, side="right") - 1
    E = np.zeros(len(downbeats_full)); C = np.zeros(len(downbeats_full)) + 1e-9
    for i, bi in enumerate(b_idx):
        if 0 <= bi < len(E):
            E[bi] += rms[i]; C[bi] += 1
    E = (E / C)[:len(downbeats_full)]
    # energy "jump" at boundaries
    dE = np.abs(np.diff(E))
    dE = (dE - dE.min()) / (dE.max() - dE.min() + 1e-9)
    dE = dE[:len(b_times)]

    # percussive flux (fast changes)
    S = librosa.stft(y, n_fft=2048, hop_length=hop)
    H, P = librosa.decompose.hpss(S)
    flux = np.maximum(0.0, np.diff(np.abs(P), axis=1)).mean(axis=0)
    flux = np.r_[0.0, flux]
    t_flux = librosa.frames_to_time(np.arange(len(flux)), sr=sr, hop_length=hop)
    # bar mean flux and jump
    f_idx = np.searchsorted(downbeats_full, t_flux, side="right") - 1
    F = np.zeros(len(downbeats_full)); C2 = np.zeros(len(downbeats_full)) + 1e-9
    for i, bi in enumerate(f_idx):
        if 0 <= bi < len(F):
            F[bi] += flux[i]; C2[bi] += 1
    F = (F / C2)
    dF = np.abs(np.diff(F))
    dF = (dF - dF.min()) / (dF.max() - dF.min() + 1e-9)
    dF = dF[:len(b_times)]

    # --- combined score on boundaries ---
    base = w_novelty * nov + w_energy * dE + w_flux * dF
    base = (base - base.min()) / (base.max() - base.min() + 1e-9)

    # allow both strong peaks and strong minima of novelty (hysteresis)
    hi = np.quantile(nov, hi_q)
    lo = np.quantile(nov, lo_q)
    peaks, _ = find_peaks(nov)
    mins,  _ = find_peaks(-nov)

    strong = np.zeros_like(base) - 1e3
    strong[peaks[nov[peaks] >= hi]] = base[peaks[nov[peaks] >= hi]]
    strong[mins[nov[mins]  <= lo]]  = np.maximum(strong[mins[nov[mins] <= lo]],
                                                 1.0 - nov[mins[nov[mins] <= lo]])

    # --- DP with binary search to meet target sparsity ---
    n = len(b_times)
    best = -1e12*np.ones(n+1); prev = -np.ones(n+1, dtype=int)
    def solve(lam):
        best[:] = -1e12; prev[:] = -1; best[0] = 0.0
        for i in range(n):
            if best[i] <= -1e9: continue
            j0, j1 = i + min_bars, min(n, i + max_bars)
            for j in range(j0, j1 + 1):
                sc = strong[j-1]
                if sc < -1e2:  # disallowed
                    continue
                val = best[i] + sc - lam
                if val > best[j]:
                    best[j] = val; prev[j] = i
        j = int(np.argmax(best)); idx=[]
        while j>0 and prev[j]>=0:
            idx.append(j-1); j=int(prev[j])
        return np.array(sorted(idx), dtype=int)

    lo_p, hi_p = 0.0, penalty_hi
    chosen = solve(hi_p)
    for _ in range(18):
        mid = 0.5*(lo_p + hi_p)
        idx = solve(mid)
        if len(idx) > max_segments or len(idx) > target_segments:
            lo_p = mid
        else:
            chosen = idx; hi_p = mid
        if hi_p - lo_p < 1e-3: break

    # --- NMS in bar domain ---
    if len(chosen) > 1:
        keep = [chosen[0]]
        for i in chosen[1:]:
            if i - keep[-1] <= nms_bar_gap:
                if base[i] > base[keep[-1]]: keep[-1] = i
            else:
                keep.append(i)
        chosen = np.array(keep, dtype=int)

    cuts = b_times[chosen] if len(chosen) else np.array([])

    # --- Apply boundary merging to bar-level segments ---
    cuts = _merge_close_boundaries(
        cut_times=cuts,
        beat_times=downbeats_full,   # snap to bar grid
        rms_t=t_rms,
        rms=rms,
        med_beat=np.median(np.diff(downbeats_full))/max(1, 4),  # ~one beat from bar len
        beats_per_bar=4,
        closeness=0.95,
        min_beats_between=1,
        snap_window_bars=0.75,
        beat_snap=0.25,
        prefer="median"
    )

    # Average/merge close boundaries (use bar-based min gap)
    bar_len = np.median(np.diff(downbeats_full))
    cuts = _average_close_boundaries(
        cuts,
        min_gap_sec=3 * bar_len,            # same logic as your min_bars
        beat_times=downbeats_full,          # snap to bar grid
        rms_t=t_rms, rms=rms,
        snap_window_sec=0.75 * bar_len,
        beat_snap_sec=0.25
    )

    # --- Safety net backfill: ensure no gap > max_segment_seconds ---
    segs = np.r_[0.0, cuts, duration]
    def backfill_once(segs):
        gaps = np.diff(segs)
        i = int(np.argmax(gaps))
        if gaps[i] <= max_segment_seconds + 1e-6:
            return segs, False
        # search best boundary inside this gap by combined base score
        t0, t1 = segs[i], segs[i+1]
        mask = (b_times > t0 + bar_len*0.5) & (b_times < t1 - bar_len*0.5)
        if not np.any(mask):
            return segs, False
        j = np.argmax(base[mask])
        t_best = b_times[mask][j]
        return np.sort(np.r_[segs, t_best]), True

    changed = True
    while changed and len(segs) - 2 < max_segments:
        segs, changed = backfill_once(segs)

    # Optional: tidy after backfill
    cuts = segs[1:-1]  # extract internal boundaries
    if len(cuts) > 0:
        bar_len = np.median(np.diff(downbeats_full))
        cuts = _average_close_boundaries(
            cuts,
            min_gap_sec=3 * bar_len,            # same logic as your min_bars
            beat_times=downbeats_full,          # snap to bar grid
            rms_t=t_rms, rms=rms,
            snap_window_sec=0.75 * bar_len,
            beat_snap_sec=0.25
        )
        segs = np.array(np.r_[0.0, cuts, duration], float)

    # Clamp segments to [0, duration] and ensure uniqueness
    segments_all = np.clip(segs, 0.0, duration)
    segments_all = np.unique(np.round(segments_all, 6))  # 1ms tolerance for uniqueness

    # FINAL BEAT SNAPPING: Snap segments to closest beats before returning
    # Use provided beat times or calculate new ones
    if beat_times is not None:
        beat_times_for_snapping = np.array(beat_times)
    else:
        tempo, beat_times_for_snapping = _beat_times(y, sr)

    segments_all = snap_segments_to_beats(segments_all, beat_times_for_snapping, snap_threshold=0.5)

    debug = {
        "boundary_times": b_times.tolist(),
        "novelty": nov.tolist(),
        "score_base": base.tolist(),
        "chosen_idx": chosen.tolist()
    }
    return segments_all, downbeats_full, debug

# =============================================================================
# BEAT SNAPPING UTILITIES
# =============================================================================

def snap_segments_to_beats(segments, beat_times, snap_threshold=0.5, debug=False):
    """Snap segment boundaries to the closest beat within threshold."""
    if len(segments) <= 2 or len(beat_times) == 0:
        return segments

    snapped_segments = [segments[0]]  # Keep start time
    snap_info = []

    for i in range(1, len(segments) - 1):  # Skip first and last (start/end)
        segment_time = segments[i]

        # Find closest beat
        closest_beat_idx = np.argmin(np.abs(beat_times - segment_time))
        closest_beat_time = beat_times[closest_beat_idx]
        distance = abs(closest_beat_time - segment_time)

        # Always snap to closest beat, regardless of threshold
        snapped_segments.append(closest_beat_time)
        if debug:
            snap_info.append(f"Segment {i}: {segment_time:.3f}s -> {closest_beat_time:.3f}s (Δ{distance:.3f}s, beat_idx={closest_beat_idx})")

    snapped_segments.append(segments[-1])  # Keep end time

    # Print snap info for debugging if requested
    if debug and snap_info:
        print("BEAT SNAPPING RESULTS:")
        for info in snap_info:
            print(f"  {info}")

    return np.array(snapped_segments)

# =============================================================================
# VISUALIZATION
# =============================================================================

def create_visualization(y, sr, rms_t, rms, beat_times, downbeats, segments, bar_novelty, audio_file="audio.wav", beat_energy_debug=None):
    """Create visualization for audio segmentation analysis"""
    if not _import_matplotlib():
        print("⚠️ Matplotlib not available, skipping visualization")
        return None
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))

    rms_db = 20 * np.log10(rms + 1e-9)

    # Plot 1: RMS Energy with segments
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

    # Plot 2: Beat tracking
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

    # Plot 3: Analysis details
    if beat_energy_debug and "beat_times" in beat_energy_debug:
        beat_times_energy = np.array(beat_energy_debug["beat_times"])
        beat_energy = np.array(beat_energy_debug.get("E", []))
        spread = np.array(beat_energy_debug.get("spread", []))

        if len(beat_times_energy) > 0 and len(beat_energy) > 0:
            # Ensure arrays have the same length
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

# =============================================================================
# MAIN ANALYSIS INTERFACE
# =============================================================================

def load_audio_bytes(data: bytes, sr=22050):
    """Load and preprocess audio from bytes."""
    y, file_sr = sf.read(io.BytesIO(data), always_2d=False, dtype='float32')

    # Convert to mono if stereo
    if y.ndim > 1:
        y = np.mean(y, axis=1)

    # Resample if needed
    if file_sr != sr:
        y = librosa.resample(y, orig_sr=file_sr, target_sr=sr)

    # Ensure audio is floating-point and normalized
    y = y.astype(np.float32)
    y = librosa.util.normalize(y)

    return y, sr

def analyze_audio_bytes(data: bytes, sr=22050, hop=512, create_plot=False, audio_file="audio.wav",
                       target_segments=6, max_segments=8, hi_q=0.70, lo_q=0.35,
                       w_novelty=0.6, w_energy=0.25, w_flux=0.15, use_precise_detection=True,
                       short_ma_beats=4, long_ma_beats=16, min_gap_seconds=11.0,
                       spread_prom_q=0.75, use_pelt=True, pelt_penalty=4.5):
    """Analyze audio and return segmentation results."""
    y, sr = load_audio_bytes(data, sr)
    duration = len(y) / sr

    # Get basic audio features
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    rms_t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    tempo, beat_times = _beat_times(y, sr)
    
    # Choose segmentation method
    if use_precise_detection:
        # Use the new precise segment detection method
        try:
            print("🎵 Using PRECISE segment detection method...")
            peak_times, peak_scores, times, rms_db, ma_short, ma_long, score_z, segments = detect_music_segments_precise(
                y, sr,
                min_peaks=2,
                max_peaks=None,
                window_size=2048,
                hop_length=hop,
                min_gap_seconds=2.0,
                short_ma_sec=0.50,
                long_ma_sec=3.00,
                include_boundaries=True
            )
            
            # Convert segments to the expected format
            segments_all = np.array([seg['time'] for seg in segments])
            
            # Ensure the first segment always starts at 0.0
            if len(segments_all) > 0 and segments_all[0] != 0.0:
                segments_all = np.concatenate([[0.0], segments_all])
            
            # Ensure the last segment always ends at duration
            if len(segments_all) > 0 and segments_all[-1] != duration:
                segments_all = np.concatenate([segments_all, [duration]])
            
            # Remove duplicates and sort
            segments_all = np.unique(segments_all)
            
            downbeats_full = _downbeats_from_beats(beat_times, duration=duration)
            
            # Create debug info
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
            print(f"⚠️ Precise detection failed: {e}")
            print("🔄 Falling back to beat energy segmentation...")
            # Fall back to beat energy segmentation
            try:
                segments_all, beat_energy_debug = segments_from_beat_energy_pro(
                    y, sr,
                    short_ma_beats=short_ma_beats,
                    long_ma_beats=long_ma_beats,
                    min_gap_seconds=min_gap_seconds,
                    max_gap_seconds=45.0,
                    keep_quantile=0.62,
                    max_segments=11,
                    pelt_penalty=pelt_penalty,
                    binseg_n_bkps=18,
                    beat_times=beat_times
                )
            except Exception as e2:
                print(f"⚠️ Beat energy segmentation also failed: {e2}")
                print("🔄 Falling back to simple segmentation...")
                segments_all = np.array([0.0, duration])
                beat_energy_debug = {"method": "fallback", "error": str(e2), "beat_times": beat_times}
            downbeats_full = _downbeats_from_beats(np.array(beat_energy_debug["beat_times"]), duration=duration)
            debug = beat_energy_debug
            bar_novelty = None
    else:
        # Use beat energy segmentation (PRO version)
        try:
            segments_all, beat_energy_debug = segments_from_beat_energy_pro(
                y, sr,
                short_ma_beats=short_ma_beats,
                long_ma_beats=long_ma_beats,
                min_gap_seconds=min_gap_seconds,
                max_gap_seconds=45.0,
                keep_quantile=0.62,
                max_segments=11,
                pelt_penalty=pelt_penalty,
                binseg_n_bkps=18,
                beat_times=beat_times
            )
        except Exception as e:
            print(f"⚠️ Beat energy segmentation failed: {e}")
            print("🔄 Falling back to simple segmentation...")
            # Fall back to simple segmentation
            segments_all = np.array([0.0, duration])
            beat_energy_debug = {"method": "fallback", "error": str(e), "beat_times": beat_times}
        downbeats_full = _downbeats_from_beats(np.array(beat_energy_debug["beat_times"]), duration=duration)
        debug = beat_energy_debug
        bar_novelty = None

    # Calculate segment lengths (segments_all includes 0 and duration)
    segment_lengths = []
    if len(segments_all) > 1:
        for i in range(len(segments_all) - 1):
            segment_lengths.append(segments_all[i+1] - segments_all[i])

    # Convert RMS to dB for better visualization
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    rms_db = np.nan_to_num(rms_db, nan=np.min(rms_db))

    result = {
        "duration": duration,
        "tempo": float(tempo),
        "segments_sec": segments_all.tolist(),
        "beat_times_sec": beat_times.tolist(),
        "downbeats_sec": downbeats_full.tolist(),
        "rms_energy": {
            "times": rms_t.tolist(),
            "values": rms_db.tolist(),
            "min_energy": float(np.min(rms_db)),
            "max_energy": float(np.max(rms_db))
        },
        "debug": {
            "method": "precise_detection" if use_precise_detection else "beat_energy",
            "num_segments": len(segments_all) - 1,
            "segment_lengths": segment_lengths
        }
    }

    # Create visualization if requested
    if create_plot:
        fig = create_visualization(y, sr, rms_t, rms, beat_times, downbeats_full, segments_all, bar_novelty, audio_file, beat_energy_debug)
        if fig is not None:
            result["plot"] = fig

    return result

def analyze_and_plot(data: bytes, audio_file="audio.wav", output_dir="."):
    """Analyze audio and save visualization plot."""
    result = analyze_audio_bytes(data, create_plot=True, audio_file=audio_file)

    if "plot" in result and _import_matplotlib():
        fig = result["plot"]
        output_image = os.path.join(output_dir, f"bar_level_analysis_{os.path.splitext(os.path.basename(audio_file))[0]}.png")
        fig.savefig(output_image, dpi=300, bbox_inches='tight')
        plt.close(fig)
        result["plot_saved"] = output_image
        del result["plot"]  # Remove the figure object from the result
    else:
        print("⚠️ Plot not created - matplotlib not available")

    return result

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Simple test execution
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        current_dir = os.path.dirname(os.path.abspath("api/processing/music/analysis/test_analysis11.py"))

    audio_file = os.path.join(current_dir, "audio.wav")

    if os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            data = f.read()

        result = analyze_audio_bytes(data, create_plot=True, audio_file="audio.wav",
                                   use_beat_energy=True,
                                   short_ma_beats=4, long_ma_beats=16, min_gap_seconds=11.0)

        print(f"Analysis complete: {result['debug']['num_segments']} segments found")
        print(f"Segments: {[f'{s:.2f}s' for s in result['segments_sec']]}")

        analyze_and_plot(data, audio_file="audio.wav", output_dir=".")
        print("Visualization saved")
    else:
        print(f"No audio file found at: {audio_file}")