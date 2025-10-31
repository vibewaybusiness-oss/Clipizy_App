"""
Vercel compatibility layer for heavy ML dependencies
Provides fallback implementations when heavy libraries are not available
"""

import json
import os
import tempfile
import warnings
from typing import Any, Dict, List, Optional, Union

# Suppress warnings for cleaner logs
warnings.filterwarnings("ignore")

# Try to import heavy dependencies, fallback to None if not available
try:
    import librosa

    LIBROSA_AVAILABLE = True
except ImportError:
    librosa = None
    LIBROSA_AVAILABLE = False

try:
    import music21

    MUSIC21_AVAILABLE = True
except ImportError:
    music21 = None
    MUSIC21_AVAILABLE = False

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    from scipy.ndimage import gaussian_filter1d
    from scipy.signal import find_peaks

    SCIPY_AVAILABLE = True
except ImportError:
    find_peaks = None
    gaussian_filter1d = None
    SCIPY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    MATPLOTLIB_AVAILABLE = False

try:
    import ruptures as rpt

    RUPTURES_AVAILABLE = True
except ImportError:
    rpt = None
    RUPTURES_AVAILABLE = False

try:
    import soundfile as sf

    SOUNDFILE_AVAILABLE = True
except ImportError:
    sf = None
    SOUNDFILE_AVAILABLE = False


class VercelCompatibilityError(Exception):
    """Raised when a feature is not available in Vercel environment"""

    pass


def check_ml_availability():
    """Check which ML libraries are available"""
    return {
        "librosa": LIBROSA_AVAILABLE,
        "music21": MUSIC21_AVAILABLE,
        "numpy": NUMPY_AVAILABLE,
        "scipy": SCIPY_AVAILABLE,
        "matplotlib": MATPLOTLIB_AVAILABLE,
        "ruptures": RUPTURES_AVAILABLE,
        "soundfile": SOUNDFILE_AVAILABLE,
    }


def require_ml_library(library_name: str):
    """Decorator to require specific ML library"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not globals().get(f"{library_name.upper()}_AVAILABLE", False):
                raise VercelCompatibilityError(
                    f"Feature requires {library_name} which is not available in Vercel environment"
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


class LightweightAudioAnalyzer:
    """Lightweight audio analysis without heavy ML dependencies"""

    def __init__(self):
        self.available = check_ml_availability()

    def analyze_audio_basic(self, file_path: str) -> Dict[str, Any]:
        """Basic audio analysis using only available libraries"""
        try:
            # Basic file info
            file_size = os.path.getsize(file_path)

            # Try to get basic audio info using mutagen
            try:
                from mutagen import File as MutagenFile

                audio_file = MutagenFile(file_path)
                if audio_file is not None:
                    duration = audio_file.info.length if hasattr(audio_file.info, "length") else 0
                    bitrate = audio_file.info.bitrate if hasattr(audio_file.info, "bitrate") else 0
                    sample_rate = audio_file.info.sample_rate if hasattr(audio_file.info, "sample_rate") else 0
                else:
                    duration = 0
                    bitrate = 0
                    sample_rate = 0
            except Exception:
                duration = 0
                bitrate = 0
                sample_rate = 0

            return {
                "file_size": file_size,
                "duration": duration,
                "bitrate": bitrate,
                "sample_rate": sample_rate,
                "analysis_type": "basic",
                "ml_available": self.available,
                "message": "Basic analysis completed (ML libraries not available in Vercel)",
            }
        except Exception as e:
            return {"error": str(e), "analysis_type": "basic", "ml_available": self.available}

    def analyze_music_peaks_basic(self, file_path: str) -> Dict[str, Any]:
        """Basic peak detection without librosa"""
        try:
            # Simple time-based peak simulation
            duration = 0
            try:
                from mutagen import File as MutagenFile

                audio_file = MutagenFile(file_path)
                if audio_file is not None:
                    duration = audio_file.info.length if hasattr(audio_file.info, "length") else 0
            except Exception:
                pass

            # Generate basic peaks based on duration
            if duration > 0:
                # Simple peak generation - every 30 seconds
                peak_interval = 30
                peak_times = list(range(0, int(duration), peak_interval))
                peak_scores = [0.8] * len(peak_times)
            else:
                peak_times = []
                peak_scores = []

            return {
                "peak_times": peak_times,
                "peak_scores": peak_scores,
                "total_peaks": len(peak_times),
                "analysis_duration": duration,
                "analysis_type": "basic_peaks",
                "ml_available": self.available,
            }
        except Exception as e:
            return {"error": str(e), "analysis_type": "basic_peaks", "ml_available": self.available}


class LightweightMusicAnalyzer:
    """Lightweight music analysis service for Vercel"""

    def __init__(self):
        self.audio_analyzer = LightweightAudioAnalyzer()
        self.available = check_ml_availability()

    def analyze_music_comprehensive(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive music analysis with fallbacks"""
        try:
            # Basic analysis
            basic_analysis = self.audio_analyzer.analyze_audio_basic(file_path)
            peak_analysis = self.audio_analyzer.analyze_music_peaks_basic(file_path)

            # Genre detection (simplified)
            genre = self._detect_genre_basic(file_path)

            # Tempo estimation (simplified)
            tempo = self._estimate_tempo_basic(file_path)

            return {
                "basic_analysis": basic_analysis,
                "peak_analysis": peak_analysis,
                "genre": genre,
                "tempo": tempo,
                "analysis_type": "comprehensive_lightweight",
                "ml_available": self.available,
                "message": "Comprehensive analysis completed with lightweight fallbacks",
            }
        except Exception as e:
            return {"error": str(e), "analysis_type": "comprehensive_lightweight", "ml_available": self.available}

    def _detect_genre_basic(self, file_path: str) -> str:
        """Basic genre detection based on file metadata"""
        try:
            from mutagen import File as MutagenFile

            audio_file = MutagenFile(file_path)
            if audio_file is not None and hasattr(audio_file, "tags"):
                genre = audio_file.tags.get("genre", ["Unknown"])[0] if audio_file.tags else "Unknown"
                return str(genre)
        except Exception:
            pass
        return "Unknown"

    def _estimate_tempo_basic(self, file_path: str) -> float:
        """Basic tempo estimation"""
        try:
            from mutagen import File as MutagenFile

            audio_file = MutagenFile(file_path)
            if audio_file is not None and hasattr(audio_file.info, "length"):
                duration = audio_file.info.length
                # Simple tempo estimation based on duration
                if duration > 0:
                    # Assume 4/4 time, estimate BPM based on duration
                    estimated_bpm = 120  # Default BPM
                    return float(estimated_bpm)
        except Exception:
            pass
        return 120.0


def get_analysis_service():
    """Get appropriate analysis service based on environment"""
    # Check for core ML libraries (librosa, numpy, scipy, soundfile)
    ml_available = check_ml_availability()
    core_libraries = ["librosa", "numpy", "scipy", "soundfile"]
    core_available = all(ml_available.get(lib, False) for lib in core_libraries)

    if core_available:
        # Core ML capabilities available
        try:
            from api.services.media.analysis_service import AnalysisService

            return AnalysisService()
        except ImportError:
            pass

    # Fallback to lightweight service
    return LightweightMusicAnalyzer()


def get_music_analyzer_service():
    """Get appropriate music analyzer service based on environment"""
    # Check for core ML libraries (librosa, numpy, scipy, soundfile)
    ml_available = check_ml_availability()
    core_libraries = ["librosa", "numpy", "scipy", "soundfile"]
    core_available = all(ml_available.get(lib, False) for lib in core_libraries)

    if core_available:
        # Core ML capabilities available
        try:
            from api.services.media.music_analyzer_service import MusicAnalyzerService

            return MusicAnalyzerService()
        except ImportError:
            pass

    # Fallback to lightweight service
    return LightweightMusicAnalyzer()
