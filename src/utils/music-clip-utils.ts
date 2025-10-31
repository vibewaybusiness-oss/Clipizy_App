import type { MusicTrack, TrackDescriptions } from '@/types/domains';
import { createValidatedBlobURL } from '@/utils/memory-management';

// UUID validation function
export const isValidUUID = (uuid: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

// Validation function for track descriptions
export const hasValidDescription = (
  track: MusicTrack,
  trackDescriptions: Record<string, string>,
  sharedDescription?: string,
  reuse_content?: boolean, // CHANGED: was useSameVideoForAll
  minLength: number = 10
): boolean => {
  // Check if track has its own description
  const trackDescription = trackDescriptions[track.id] || track.videoDescription;

  // Check if using shared description
  const description = reuse_content && sharedDescription // CHANGED: was useSameVideoForAll
    ? sharedDescription
    : trackDescription;

  return Boolean(description && description.trim().length >= minLength);
};

// Format duration helper - use formatTimeWithHours from @/lib/utils instead

// File to data URI converter - use @/lib/utils instead

// Calculate total duration of tracks
export const getTotalDuration = (tracks: MusicTrack[]): number => {
  return tracks.reduce((total, track) => total + track.duration, 0);
};

// Extract audio duration from file using HTML5 Audio API
export const getAudioDuration = (file: File): Promise<number> => {
  return new Promise((resolve, reject) => {
    const audio = new Audio();
    const url = createValidatedBlobURL(file);
    
    const cleanup = () => {
      // Cleanup is handled by the centralized memory management system
      audio.removeEventListener('loadedmetadata', onLoadedMetadata);
      audio.removeEventListener('error', onError);
    };
    
    const onLoadedMetadata = () => {
      const duration = audio.duration;
      cleanup();
      if (isNaN(duration) || duration === Infinity) {
        reject(new Error('Invalid audio duration'));
      } else {
        resolve(duration);
      }
    };
    
    const onError = (error: Event) => {
      cleanup();
      reject(new Error('Failed to load audio file'));
    };
    
    audio.addEventListener('loadedmetadata', onLoadedMetadata);
    audio.addEventListener('error', onError);
    
    // Set a timeout to prevent hanging
    const timeout = setTimeout(() => {
      cleanup();
      reject(new Error('Audio duration extraction timeout'));
    }, 10000); // 10 second timeout
    
    audio.src = url;
    audio.load();
    
    // Clear timeout when metadata is loaded
    audio.addEventListener('loadedmetadata', () => {
      clearTimeout(timeout);
    });
  });
};

// Duration validation constants
export const DURATION_VALIDATION = {
  MIN_DURATION_SECONDS: 5, // Minimum 5 seconds
  MAX_DURATION_SECONDS: 600, // Maximum 10 minutes
  MIN_DURATION_HUMAN: '5 seconds',
  MAX_DURATION_HUMAN: '10 minutes'
} as const;

// Duration validation function
export const isValidDuration = (duration: number): { isValid: boolean; error?: string } => {
  if (isNaN(duration) || duration === Infinity || duration === -Infinity) {
    return { isValid: false, error: 'Invalid audio duration detected' };
  }
  
  if (duration < DURATION_VALIDATION.MIN_DURATION_SECONDS) {
    return { 
      isValid: false, 
      error: `Audio duration must be at least ${DURATION_VALIDATION.MIN_DURATION_HUMAN}` 
    };
  }
  
  if (duration > DURATION_VALIDATION.MAX_DURATION_SECONDS) {
    return { 
      isValid: false, 
      error: `Audio duration must not exceed ${DURATION_VALIDATION.MAX_DURATION_HUMAN}` 
    };
  }
  
  return { isValid: true };
};

// Enhanced audio duration extraction with validation
export const getValidatedAudioDuration = async (file: File): Promise<{ duration: number; isValid: boolean; error?: string }> => {
  try {
    const duration = await getAudioDuration(file);
    const validation = isValidDuration(duration);
    
    return {
      duration,
      isValid: validation.isValid,
      error: validation.error
    };
  } catch (error) {
    return {
      duration: 0,
      isValid: false,
      error: error instanceof Error ? error.message : 'Failed to extract audio duration'
    };
  }
};

// Storage keys constants
export const STORAGE_KEYS = {
  CURRENT_STEP: 'clipizy_current_step',
  MAX_REACHED_STEP: 'clipizy_max_reached_step',
  GENERATION_MODE: 'clipizy_generation_mode',
  MUSIC_PROMPT: 'clipizy_music_prompt',
  SETTINGS: 'clipizy_settings',
  PROMPTS: 'clipizy_prompts',
  CURRENT_PROJECT_ID: 'clipizy_current_project_id',
  IS_PROJECT_CREATED: 'clipizy_is_project_created',
  MUSIC_TRACKS_TO_GENERATE: 'clipizy_music_tracks_to_generate',
  IS_INSTRUMENTAL: 'clipizy_is_instrumental',
  SCENES: 'clipizy_scenes',
  ANALYZED_SCENES: 'clipizy_analyzed_scenes',
  SHOW_SCENE_CONTROLS: 'clipizy_show_scene_controls',
  GENERATED_VIDEO_URI: 'clipizy_generated_video_uri',
  CHANNEL_ANIMATION_FILE: 'clipizy_channel_animation_file',
} as const;

// Helper functions for localStorage persistence
export function getFromStorage<T>(key: string, defaultValue: T): T {
  if (typeof window === 'undefined') return defaultValue;

  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.warn(`Failed to parse ${key} from localStorage:`, error);
    return defaultValue;
  }
}

export function saveToStorage<T>(key: string, value: T): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.warn(`Failed to save ${key} to localStorage:`, error);
  }
}

// Clear all localStorage data
export const clearAllStorageData = () => {
  Object.values(STORAGE_KEYS).forEach(key => {
    localStorage.removeItem(key);
  });
};
