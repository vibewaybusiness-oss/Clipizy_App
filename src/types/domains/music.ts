// MUSIC DOMAIN TYPES
import { GenerationMode } from '../components/vibewave.types';

// Re-export GenerationMode for convenience
export type { GenerationMode };
export interface MusicTrack {
  id: string;
  file?: File;
  url: string;
  duration: number;
  name: string;
  prompt?: string;
  videoDescription?: string;
  description?: string;
  generatedAt: Date;
  genre?: string;
  isGenerated?: boolean;
  metadata?: {
    duration?: number;
    format?: string;
    sample_rate?: number;
    channels?: number;
    bitrate?: number;
    size_mb?: number;
  };
  status: string;
  created_at: string;
  updated_at?: string;
  sunoId?: string;
  lyrics?: string;
  error?: string;
  uploaded?: boolean;
  isInstrumental?: boolean;
  s3_url?: string;
  filename?: string;
  size?: number;
  generation_method?: string;

  // Enhanced file traceability
  originalFileInfo?: {
    name: string;
    size: number;
    type: string;
    lastModified: number;
    checksum?: string; // For file integrity verification
    uploadSource?: 'file_upload' | 'generated' | 'imported';
    uploadTimestamp?: string;
    projectId?: string;
    userId?: string;
  };

  // Analysis data stored directly in track
  analysis?: {
    duration: number;
    tempo: number;
    segments_sec: number[];
    beat_times_sec: number[];
    downbeats_sec: number[];
    debug: {
      method: string;
      num_segments: number;
      segment_lengths: number[];
    };
    title: string;
    audio_features: {
      duration: number;
      tempo: number;
      spectral_centroid: number;
      rms_energy: number;
      harmonic_ratio: number;
      onset_rate: number;
    };
    music_descriptors: string[];
    segments: any[];
    segment_analysis: any[];
    // Add RMS energy data for waveform visualization
    rms_energy?: {
      times: number[];
      values: number[];
      min_energy: number;
      max_energy: number;
    };
    // Add other backend fields
    features?: any;
    genre_scores?: Record<string, number>;
    predicted_genre?: string;
    confidence?: number;
    peak_analysis?: any;
    analysis_timestamp?: string;
    metadata?: any;
  };

  // Legacy backend storage removed - using unified PostgreSQL JSONB
  filePath: string;
  bucket?: string;
  region?: string;
  uploadMethod?: 's3' | 'local';
  storageUrl?: string;
}

export interface MusicAnalysisResult {
  trackId: string;
  analysis: {
    duration: number;
    tempo: number;
    segments_sec: number[];
    beat_times_sec: number[];
    downbeats_sec: number[];
    debug: {
      method: string;
      num_segments: number;
      segment_lengths: number[];
    };
    title: string;
    audio_features: {
      duration: number;
      tempo: number;
      spectral_centroid: number;
      rms_energy: number;
      harmonic_ratio: number;
      onset_rate: number;
    };
    music_descriptors: string[];
    segments: Array<{
      segment_index: number;
      start_time: number;
      end_time: number;
      duration: number;
      features: {
        duration: number;
        tempo: number;
        spectral_centroid: number;
        rms_energy: number;
        harmonic_ratio: number;
        onset_rate: number;
        start_time: number;
        end_time: number;
      };
      descriptors: string[];
    }>;
  };
}

export interface TrackDescriptions {
  [trackId: string]: string;
}

export interface TrackGenres {
  [trackId: string]: string;
}

// GenerationMode is imported from components/vibewave.types

export interface AudioPlaybackState {
  currentlyPlayingId: string | null;
  isPlaying: boolean;
  currentAudio: HTMLAudioElement | null;
}
