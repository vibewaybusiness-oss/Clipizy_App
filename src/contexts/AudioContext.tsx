"use client";

import React, { createContext, useContext, useRef, useState, useCallback, useEffect } from 'react';
import { useToast } from '@/hooks/ui/use-toast';
import { useGlobalAudioMemoryManagement } from '@/hooks/storage';
import { createValidatedBlobURL, ensureValidBlobURL } from '@/utils/memory-management';

interface Track {
  id: string;
  file?: File;
  url?: string;
  name?: string;
}

interface AudioContextType {
  playTrack: (track: Track, startTime?: number) => void;
  playSegment: (track: Track, startTime: number, endTime: number) => void;
  pauseAll: () => void;
  stopAll: () => void;
  currentlyPlayingId: string | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  audioRef: React.RefObject<HTMLAudioElement>;
  setHasTracks: (hasTracks: boolean) => void;
}

const AudioContext = createContext<AudioContextType | undefined>(undefined);

export function AudioProvider({ children }: { children: React.ReactNode }) {
  const [currentlyPlayingId, setCurrentlyPlayingId] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [hasTracks, setHasTracks] = useState<boolean>(false);
  
  // Memory management
  const audioMemoryManager = useGlobalAudioMemoryManagement();
  
  // Centralized blob URL creation using the global memory manager
  const createSafeBlobUrl = useCallback((file: File): string => {
    // Check if file is valid before creating blob URL
    if (!file || file.size === 0) {
      throw new Error('Invalid file provided for blob URL creation');
    }
    
    // Use centralized blob creation with validation
    return createValidatedBlobURL(file);
  }, []);
  
  // Safe blob URL revocation using centralized system
  const revokeSafeBlobUrl = useCallback((url: string) => {
    audioMemoryManager.revokeAudioBlobURL(url);
  }, [audioMemoryManager]);

  // Validate blob URL using centralized system
  const validateBlobUrl = useCallback(async (url: string): Promise<boolean> => {
    return await audioMemoryManager.validateBlobURL(url);
  }, [audioMemoryManager]);
  
  // Debug wrapper for setHasTracks
  const setHasTracksWithDebug = useCallback((value: boolean) => {
    console.log('setHasTracks called with:', value);
    setHasTracks(value);
  }, []);
  
  // Initialize hasTracks to false on mount
  useEffect(() => {
    console.log('AudioProvider mounted, initializing hasTracks to false');
    setHasTracks(false);
  }, []);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { toast } = useToast();

  // Helper function to log audio element state
  const logAudioState = (context: string) => {
    const audio = audioRef.current;
    if (audio) {
      console.log(`Audio state [${context}]:`, {
        src: audio.src,
        currentTime: audio.currentTime,
        duration: audio.duration,
        paused: audio.paused,
        ended: audio.ended,
        readyState: audio.readyState,
        networkState: audio.networkState,
        error: audio.error,
        volume: audio.volume,
        muted: audio.muted
      });
    }
  };

  // Helper function to get audio format from URL or file
  const getAudioFormat = (url?: string, file?: File): { mimeType: string; format: string } => {
    console.log('getAudioFormat called with:', { url, file: file ? { name: file.name, type: file.type } : null });
    
    // PRIORITIZE FILE TYPE OVER URL - files have more reliable type information
    if (file && file.type) {
      const mimeType = file.type;
      const format = file.type.split('/')[1]?.toUpperCase() || 'UNKNOWN';
      console.log('Using file.type:', { mimeType, format });
      return { mimeType, format };
    }
    
    // FALLBACK TO FILE NAME EXTENSION if file.type is not available
    if (file && file.name) {
      const fileName = file.name.toLowerCase();
      console.log('Using file.name extension:', fileName);
      if (fileName.endsWith('.mp3')) {
        const result = { mimeType: 'audio/mpeg', format: 'MP3' };
        console.log('Detected MP3 from filename:', result);
        return result;
      }
      if (fileName.endsWith('.wav')) {
        const result = { mimeType: 'audio/wav', format: 'WAV' };
        console.log('Detected WAV from filename:', result);
        return result;
      }
      if (fileName.endsWith('.ogg')) {
        const result = { mimeType: 'audio/ogg', format: 'OGG' };
        console.log('Detected OGG from filename:', result);
        return result;
      }
      if (fileName.endsWith('.flac')) {
        const result = { mimeType: 'audio/flac', format: 'FLAC' };
        console.log('Detected FLAC from filename:', result);
        return result;
      }
      if (fileName.endsWith('.aac')) {
        const result = { mimeType: 'audio/aac', format: 'AAC' };
        console.log('Detected AAC from filename:', result);
        return result;
      }
      if (fileName.endsWith('.m4a')) {
        const result = { mimeType: 'audio/mp4', format: 'M4A' };
        console.log('Detected M4A from filename:', result);
        return result;
      }
    }
    
    // FALLBACK TO URL EXTENSION (for non-blob URLs)
    if (url && !url.startsWith('blob:')) {
      const urlLower = url.toLowerCase();
      console.log('Using URL extension:', urlLower);
      if (urlLower.includes('.mp3')) return { mimeType: 'audio/mpeg', format: 'MP3' };
      if (urlLower.includes('.wav')) return { mimeType: 'audio/wav', format: 'WAV' };
      if (urlLower.includes('.ogg')) return { mimeType: 'audio/ogg', format: 'OGG' };
      if (urlLower.includes('.flac')) return { mimeType: 'audio/flac', format: 'FLAC' };
      if (urlLower.includes('.aac')) return { mimeType: 'audio/aac', format: 'AAC' };
      if (urlLower.includes('.m4a')) return { mimeType: 'audio/mp4', format: 'M4A' };
    }
    
    // FOR BLOB URLS - try to detect from file if available
    if (url && url.startsWith('blob:') && file) {
      console.log('Blob URL detected, trying to use file information');
      // This should have been caught by the file.type or file.name checks above
      // But if we get here, the file might not have proper type/name info
      console.warn('Blob URL with file but no type/name info, defaulting to MP3');
      return { mimeType: 'audio/mpeg', format: 'MP3' };
    }
    
    // DEFAULT FALLBACK - assume MP3 for unknown formats
    console.warn('Could not determine audio format, defaulting to MP3');
    return { mimeType: 'audio/mpeg', format: 'MP3' };
  };

  // Helper function to check browser audio format support
  const getSupportedFormats = (): string[] => {
    const testAudio = new Audio();
    const formats = [
      { mimeType: 'audio/mpeg', name: 'MP3' },
      { mimeType: 'audio/wav', name: 'WAV' },
      { mimeType: 'audio/ogg', name: 'OGG' },
      { mimeType: 'audio/flac', name: 'FLAC' },
      { mimeType: 'audio/aac', name: 'AAC' },
      { mimeType: 'audio/mp4', name: 'M4A' }
    ];
    
    return formats
      .filter(format => testAudio.canPlayType(format.mimeType))
      .map(format => format.name);
  };

  // Helper function to validate audio file integrity
  const validateAudioFile = (file: File): { isValid: boolean; error?: string } => {
    console.log('Validating audio file:', {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified
    });
    
    // Check file size
    if (file.size === 0) {
      return { isValid: false, error: 'File is empty' };
    }
    
    // Check file size limits (100MB max)
    if (file.size > 100 * 1024 * 1024) {
      return { isValid: false, error: 'File is too large (max 100MB)' };
    }
    
    // Check file type
    const fileType = file.type || '';
    const fileName = file.name || '';
    const supportedTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/m4a', 'audio/aac', 'audio/flac'];
    const supportedExtensions = /\.(mp3|wav|ogg|m4a|aac|flac)$/i;
    
    const hasValidMimeType = fileType && supportedTypes.some(type => fileType.includes(type));
    const hasValidExtension = fileName && supportedExtensions.test(fileName);
    
    console.log('File validation results:', {
      hasValidMimeType,
      hasValidExtension,
      fileType,
      fileName
    });
    
    // For MP3 files, be more lenient with MIME type validation
    if (fileName.toLowerCase().endsWith('.mp3')) {
      console.log('MP3 file detected, using lenient validation');
      return { isValid: true };
    }
    
    if (!hasValidMimeType && !hasValidExtension) {
      return { isValid: false, error: 'Unsupported file format' };
    }
    
    return { isValid: true };
  };

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) {
      console.warn('Audio element not available in useEffect');
      return;
    }

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration || 0);
    };

    const handleEnded = () => {
      setCurrentlyPlayingId(null);
      setIsPlaying(false);
      setCurrentTime(0);
    };

    const handleError = (e: Event) => {
      const audioElement = e.target as HTMLAudioElement;
      const error = audioElement?.error;
      
      // Log detailed audio state when error occurs
      logAudioState('ERROR');
      console.log('handleError called, hasTracks:', hasTracks);
      
      // Early return if audio element is not available
      if (!audioElement) {
        console.warn('Audio error handler called but audio element is not available');
        return;
      }
      
      let errorMessage = "Unknown audio error";
      let errorDescription = "An unknown error occurred while playing audio.";
      
      // Simple error logging
      console.log('Audio error:', {
        code: error?.code,
        message: error?.message,
        src: audioElement?.src,
        readyState: audioElement?.readyState,
        networkState: audioElement?.networkState
      });
      
      if (error) {
        // Check if we should ignore this error when no tracks are available
        if (!hasTracks && (error.code === MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED || 
                          error.message?.includes('Empty src attribute') ||
                          audioElement.src?.includes('/dashboard/create/music-clip'))) {
          console.log('Ignoring media error - no tracks available, error code:', error.code);
          return;
        }
        
        switch (error.code) {
          case MediaError.MEDIA_ERR_ABORTED:
            errorMessage = "Audio playback aborted";
            errorDescription = "Audio playback was aborted by the user.";
            break;
          case MediaError.MEDIA_ERR_NETWORK:
            errorMessage = "Network error";
            errorDescription = "A network error occurred while loading the audio.";
            break;
          case MediaError.MEDIA_ERR_DECODE:
            errorMessage = "Audio decode error";
            errorDescription = "The audio file could not be decoded. It may be corrupted or in an unsupported format.";
            break;
          case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
            console.warn('Unsupported audio format encountered', {
              trackId: currentlyPlayingId,
              src: audioElement.src,
              hasTracks,
              isBlobUrl: audioElement.src?.startsWith('blob:'),
              audioElementReadyState: audioElement.readyState,
              audioElementNetworkState: audioElement.networkState,
              errorMessage: error.message
            });
            
            // Handle blob URL issues gracefully
            if (audioElement.src?.startsWith('blob:')) {
              // Check if this is a temporary loading issue
              const isTemporaryError = audioElement.readyState === 0 || audioElement.networkState === 1;
              
              if (isTemporaryError) {
                // Silently handle temporary loading issues
                return;
              }
              
              // For persistent blob URL issues, try to recreate the blob URL
              if (track.file) {
                try {
                  const newBlobUrl = createSafeBlobUrl(track.file);
                  audioElement.src = newBlobUrl;
                  audioElement.load();
                  
                  // Try to play again silently
                  setTimeout(() => {
                    audioElement.play().catch(() => {
                      // If it still fails, just stop trying
                    });
                  }, 100);
                  
                  return; // Don't show error toast
                } catch (recreateError) {
                  // If recreation fails, show a simple error
                  errorMessage = "Audio playback issue";
                  errorDescription = "There was a problem playing this audio file. Please try again.";
                }
              } else {
                // No file available, show simple error
                errorMessage = "Audio playback issue";
                errorDescription = "There was a problem playing this audio file. Please try again.";
              }
            } else {
              // Silently ignore non-blob URL errors to avoid spamming toasts
              return;
            }
            break;
          default:
            errorMessage = `Audio error (code: ${error.code})`;
            errorDescription = `An audio error occurred with code ${error.code}.`;
        }
      } else {
        // Handle case where error object is null/undefined
        errorMessage = "Audio error (no error details)";
        errorDescription = "An audio error occurred but no specific error details are available.";
        
        // Check for common issues
        if (!audioElement.src || audioElement.src === '') {
          // IGNORE ERROR WHEN TRACK LIST IS EMPTY
          console.log('Empty src error detected, hasTracks:', hasTracks);
          if (!hasTracks) {
            console.log('Ignoring empty src error - no tracks available');
            return;
          }
          errorMessage = "No audio source";
          errorDescription = "No audio source was provided for playback.";
        } else if (audioElement.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) {
          errorMessage = "No audio source available";
          errorDescription = "The audio source is not available or accessible.";
        } else if (audioElement.src && audioElement.src.includes('/dashboard/create/music-clip')) {
          // IGNORE ERROR WHEN SRC IS POINTING TO THE CURRENT PAGE (NO TRACKS LOADED)
          console.log('Invalid src error detected (pointing to current page), hasTracks:', hasTracks);
          if (!hasTracks) {
            console.log('Ignoring invalid src error - no tracks available');
            return;
          }
          errorMessage = "Invalid audio source";
          errorDescription = "The audio source is invalid or not accessible.";
        }
      }
      
      // Only show error toast for persistent issues
      if (errorMessage && errorDescription) {
        try {
          toast({
            variant: "destructive",
            title: errorMessage,
            description: errorDescription,
          });
        } catch (toastError) {
          console.error('Failed to show error toast:', toastError);
        }
      }
      
      setCurrentlyPlayingId(null);
      setIsPlaying(false);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [toast, hasTracks]);

  const playTrack = useCallback(async (track: Track, startTime?: number) => {
    if (!audioRef.current) return;

    const audio = audioRef.current;
    
    // Check if we're trying to resume the same track that's currently paused
    if (currentlyPlayingId === track.id && !isPlaying && audio.src) {
      console.log('Resuming paused track:', track.id);
      try {
        await audio.play();
        setIsPlaying(true);
        console.log('Successfully resumed playback');
      } catch (error) {
        console.error('Failed to resume playback:', error);
        toast({
          variant: "destructive",
          title: "Resume Error",
          description: "Failed to resume audio playback.",
        });
      }
      return;
    }
    
    if (!track.url && !track.file) {
      console.warn('No audio source available for track:', {
        trackId: track.id,
        trackName: track.name,
        hasUrl: !!track.url,
        hasFile: !!track.file
      });
      toast({
        variant: "destructive",
        title: "Playback Error",
        description: "No audio source available for this track.",
      });
      return;
    }

    let audioSrc = '';
    
    console.log('Audio source selection for track:', {
      trackId: track.id,
      trackName: track.name,
      hasUrl: !!track.url,
      hasFile: !!track.file,
      hasBlob: !!(track as any).blob,
      hasBlobUrl: !!(track as any).blobUrl,
      url: track.url,
      blobUrl: (track as any).blobUrl,
      fileSize: track.file?.size
    });
    
    // Use available URL (blob or backend) for audio playback
    if (track.url && track.url.trim() !== '') {
      // Use URL directly for audio playback (blob URLs are fine while project is open)
      audioSrc = track.url;
      console.log('✅ Using URL for audio playback:', {
        url: audioSrc,
        isBlobUrl: track.url.startsWith('blob:'),
        fileName: track.file?.name,
        fileSize: track.file?.size,
        fileType: track.file?.type
      });
    } else {
      console.warn('⚠️ No URL available for track');
    }

    if (!audioSrc) {
      toast({
        variant: "destructive",
        title: "Playback Error",
        description: "Failed to create audio source for this track.",
      });
      return;
    }

    // Get audio format information
    const { mimeType, format } = getAudioFormat(track.url, track.file);
    
    // Log format detection for debugging
    console.log('Audio format detection:', {
      trackId: track.id,
      trackName: track.name,
      fileType: track.file?.type,
      fileName: track.file?.name,
      url: track.url,
      detectedMimeType: mimeType,
      detectedFormat: format,
      audioSrc: audioSrc
    });
    
    // Check if browser supports this audio format
    const browserSupport = audio.canPlayType(mimeType);
    console.log('Browser format support check:', {
      mimeType,
      format,
      browserSupport,
      trackId: track.id,
      trackName: track.name
    });
    
    // Only check format support if we have a valid MIME type
    if (mimeType && mimeType !== 'audio/mpeg' && browserSupport === '') {
      console.warn('Browser does not support audio format:', {
        mimeType,
        format,
        trackId: track.id,
        trackName: track.name,
        browserSupport
      });
      
      // For MP3 files, try alternative MIME types
      if (format === 'MP3' || track.file?.name?.toLowerCase().endsWith('.mp3')) {
        console.log('Trying alternative MP3 MIME types');
        const alternativeMimeTypes = ['audio/mp3', 'audio/mpeg3', 'audio/x-mpeg-3'];
        let foundAlternative = false;
        
        for (const altMimeType of alternativeMimeTypes) {
          const altSupport = audio.canPlayType(altMimeType);
          console.log(`Alternative MIME type ${altMimeType}: ${altSupport}`);
          if (altSupport !== '') {
            console.log(`Using alternative MIME type: ${altMimeType}`);
            foundAlternative = true;
            break;
          }
        }
        
        if (!foundAlternative) {
          console.warn('No alternative MIME type found for MP3, but continuing with playback attempt');
        }
      } else {
        console.warn('Unsupported format detected, but continuing with playback attempt');
      }
    }

    try {
      // Set up error handling before setting src
      const handleAudioError = (e: Event) => {
        console.error('Audio element error during playback:', {
          error: e,
          audioSrc: audioSrc,
          trackId: track.id,
          trackName: track.name,
          audioElement: audio,
          audioError: audio.error
        });
        
        // Handle blob URL errors gracefully
        if (audioSrc.startsWith('blob:') && audio.error?.code === MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED) {
          // Try to recreate blob URL if we have the file
          if (track.file) {
            try {
              const newBlobUrl = createSafeBlobUrl(track.file);
              audio.src = newBlobUrl;
              audio.load();
              
              // Try to play again silently
              setTimeout(() => {
                audio.play().catch(() => {
                  // If it still fails, just stop trying
                });
              }, 100);
            } catch (recreateError) {
              // If recreation fails, just continue - the main error handler will deal with it
            }
          }
        }
      };
      
      // Add temporary error listener
      audio.addEventListener('error', handleAudioError, { once: true });
      
      // Set the audio source
      audio.src = audioSrc;
      audio.volume = 0.7;
      
      // Set start time if provided
      if (startTime !== undefined && startTime > 0) {
        audio.currentTime = startTime;
      }
      
      // Add some debugging information
      console.log('Attempting to play audio:', {
        trackId: track.id,
        trackName: track.name,
        startTime: startTime,
        audioSrc: audioSrc,
        audioElement: audio,
        audioReadyState: audio.readyState,
        audioNetworkState: audio.networkState
      });
      
      // Log audio state before attempting to play
      logAudioState('BEFORE_PLAY');
      
      await audio.play();
      setCurrentlyPlayingId(track.id);
      setIsPlaying(true);
      
      console.log('Successfully started playing audio:', track.id, startTime ? `from ${startTime}s` : '');
    } catch (error) {
      console.error('Failed to play audio:', {
        error,
        trackId: track.id,
        trackName: track.name,
        audioSrc: audioSrc,
        audioElement: audio,
        audioReadyState: audio.readyState,
        audioNetworkState: audio.networkState,
        audioError: audio.error
      });
      
      let errorMessage = "Failed to start playback";
      let errorDescription = "An error occurred while trying to start audio playback.";
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage = "Audio playback blocked";
          errorDescription = "Audio playback was blocked by the browser. Please click on the page first to enable audio.";
        } else if (error.name === 'NotSupportedError') {
          errorMessage = "Audio format not supported";
          errorDescription = "The audio format is not supported by your browser.";
        } else {
          errorDescription = error.message || errorDescription;
        }
      }
      
      toast({
        variant: "destructive",
        title: errorMessage,
        description: errorDescription,
      });
    }
  }, [toast, currentlyPlayingId, isPlaying]);

  const playSegment = useCallback(async (track: Track, startTime: number, endTime: number) => {
    if (!audioRef.current) return;

    const audio = audioRef.current;
    
    if (!track.url && !track.file) {
      console.log('No audio source available for track:', track.id);
      return;
    }

    let audioSrc = '';
    
    if (track.url && track.url.trim() !== '') {
      audioSrc = track.url;
    } else if (track.file && track.file.size > 0) {
      audioSrc = audioMemoryManager.createAudioBlobURL(track.file);
    }

    if (!audioSrc) {
      console.log('Failed to create audio source for track:', track.id);
      return;
    }

    // Get audio format information
    const { mimeType, format } = getAudioFormat(track.url, track.file);
    
    // Log format detection for debugging
    console.log('Audio format detection (segment):', {
      trackId: track.id,
      trackName: track.name,
      fileType: track.file?.type,
      fileName: track.file?.name,
      url: track.url,
      detectedMimeType: mimeType,
      detectedFormat: format,
      audioSrc: audioSrc
    });
    
    // Check if browser supports this audio format
    if (mimeType && !audio.canPlayType(mimeType)) {
      console.warn('Browser does not support audio format (segment):', {
        mimeType,
        format,
        trackId: track.id,
        trackName: track.name,
        browserSupport: audio.canPlayType(mimeType)
      });
      
      toast({
        variant: "destructive",
        title: "Unsupported Audio Format",
        description: `The audio format ${format} is not supported by your browser. Please try a different audio file.`,
      });
      return;
    }

    try {
      audio.src = audioSrc;
      audio.volume = 0.7;
      audio.currentTime = startTime;
      
      // Add some debugging information
      console.log('Attempting to play segment:', {
        trackId: track.id,
        trackName: track.name,
        startTime,
        endTime,
        audioSrc: audioSrc,
        audioElement: audio,
        audioReadyState: audio.readyState,
        audioNetworkState: audio.networkState
      });
      
      await audio.play();
      setCurrentlyPlayingId(track.id);
      setIsPlaying(true);

      const checkEndTime = () => {
        if (audio.currentTime >= endTime) {
          audio.pause();
          setCurrentlyPlayingId(null);
          setIsPlaying(false);
        } else if (!audio.paused) {
          requestAnimationFrame(checkEndTime);
        }
      };
      
      requestAnimationFrame(checkEndTime);
      console.log('Successfully started playing segment:', track.id, `(${startTime}s - ${endTime}s)`);
    } catch (error) {
      console.error('Failed to play segment:', {
        error,
        trackId: track.id,
        trackName: track.name,
        startTime,
        endTime,
        audioSrc: audioSrc,
        audioElement: audio,
        audioReadyState: audio.readyState,
        audioNetworkState: audio.networkState,
        audioError: audio.error
      });
      
      let errorMessage = "Failed to start segment playback";
      let errorDescription = "An error occurred while trying to start segment playback.";
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage = "Audio playback blocked";
          errorDescription = "Audio playback was blocked by the browser. Please click on the page first to enable audio.";
        } else if (error.name === 'NotSupportedError') {
          errorMessage = "Audio format not supported";
          errorDescription = "The audio format is not supported by your browser.";
        } else {
          errorDescription = error.message || errorDescription;
        }
      }
      
      toast({
        variant: "destructive",
        title: errorMessage,
        description: errorDescription,
      });
    }
  }, [toast]);

  const pauseAll = useCallback(() => {
    if (audioRef.current && !audioRef.current.paused) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  }, []);

  const stopAll = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      // Clean up audio element using memory manager
      audioMemoryManager.cleanupAudioElement(audioRef.current);
    }
    setCurrentlyPlayingId(null);
    setIsPlaying(false);
    setCurrentTime(0);
  }, [audioMemoryManager]);

  // Helper function to clean up temporary blob URLs
  const cleanupTempBlobURL = useCallback((track: Track) => {
    if ((track as any)._tempBlobUrl) {
      console.log('🧹 Cleaning up temporary blob URL:', (track as any)._tempBlobUrl);
      URL.revokeObjectURL((track as any)._tempBlobUrl);
      delete (track as any)._tempBlobUrl;
    }
  }, []);

  const value: AudioContextType = {
    playTrack,
    playSegment,
    pauseAll,
    stopAll,
    currentlyPlayingId,
    isPlaying,
    currentTime,
    duration,
    audioRef,
    setHasTracks: setHasTracksWithDebug
  };

  // DON'T cleanup blob URLs on unmount - they should persist for the lifetime of the app
  // Only cleanup when explicitly requested or when the app closes
  useEffect(() => {
    return () => {
      // Clean up audio element but NOT blob URLs
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        audioRef.current.src = '';
      }
      // Don't call audioMemoryManager.cleanup() here - it would revoke all blob URLs
    };
  }, []);

  // Periodic cleanup is now handled by the centralized memory management system

  // Cleanup is now handled by the centralized memory management system

  // Debug utility - expose to window for testing
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).debugAudioContext = {
        getSupportedFormats,
        validateAudioFile,
        getAudioFormat,
        audioMemoryManager,
        logAudioState: (context: string) => logAudioState(context),
        testBlobURL: (file: File) => {
          console.log('Testing blob URL creation for file:', file.name);
          try {
            const url = audioMemoryManager.createAudioBlobURL(file);
            console.log('Created blob URL:', url);
            
            // Test if it can be loaded
            const testAudio = new Audio();
            testAudio.onloadedmetadata = () => console.log('Blob URL test: SUCCESS');
            testAudio.onerror = (e) => console.error('Blob URL test: FAILED', e);
            testAudio.src = url;
            
            return url;
          } catch (error) {
            console.error('Blob URL creation failed:', error);
            return null;
          }
        },
        testDirectBlobURL: (file: File) => {
          console.log('Testing direct blob URL creation for file:', file.name);
          try {
            // Create blob URL directly without going through memory manager
            const directUrl = URL.createObjectURL(file);
            console.log('Created direct blob URL:', directUrl);
            
            // Test if it can be loaded
            const testAudio = new Audio();
            testAudio.onloadedmetadata = () => {
              console.log('Direct blob URL test: SUCCESS');
              // Clean up
              URL.revokeObjectURL(directUrl);
            };
            testAudio.onerror = (e) => {
              console.error('Direct blob URL test: FAILED', e);
              // Clean up
              URL.revokeObjectURL(directUrl);
            };
            testAudio.src = directUrl;
            
            return directUrl;
          } catch (error) {
            console.error('Direct blob URL creation failed:', error);
            return null;
          }
        },
        compareFileIntegrity: (originalFile: File, processedFile: File) => {
          console.log('Comparing file integrity:');
          console.log('Original file:', {
            name: originalFile.name,
            size: originalFile.size,
            type: originalFile.type,
            lastModified: originalFile.lastModified
          });
          console.log('Processed file:', {
            name: processedFile.name,
            size: processedFile.size,
            type: processedFile.type,
            lastModified: processedFile.lastModified
          });
          
          const sizeMatch = originalFile.size === processedFile.size;
          const typeMatch = originalFile.type === processedFile.type;
          const nameMatch = originalFile.name === processedFile.name;
          
          console.log('Integrity check results:', {
            sizeMatch,
            typeMatch,
            nameMatch,
            allMatch: sizeMatch && typeMatch && nameMatch
          });
          
          return { sizeMatch, typeMatch, nameMatch, allMatch: sizeMatch && typeMatch && nameMatch };
        },
        testFileDirectly: (file: File) => {
          console.log('Testing file directly without any processing:');
          console.log('File details:', {
            name: file.name,
            size: file.size,
            type: file.type,
            lastModified: file.lastModified
          });
          
          // Test direct blob URL creation
          try {
            const directUrl = URL.createObjectURL(file);
            console.log('Direct blob URL created:', directUrl);
            
            // Test if it can be loaded
            const testAudio = new Audio();
            testAudio.onloadedmetadata = () => {
              console.log('Direct file test: SUCCESS - file is valid');
              URL.revokeObjectURL(directUrl);
            };
            testAudio.onerror = (e) => {
              console.error('Direct file test: FAILED - file is corrupted or invalid', e);
              URL.revokeObjectURL(directUrl);
            };
            testAudio.src = directUrl;
            
            return { success: true, url: directUrl };
          } catch (error) {
            console.error('Direct file test failed:', error);
            return { success: false, error };
          }
        }
      };
    }
  }, [getSupportedFormats, validateAudioFile, getAudioFormat, audioMemoryManager, logAudioState]);

  return (
    <AudioContext.Provider value={value}>
      {children}
      <audio ref={audioRef} style={{ display: 'none' }} />
    </AudioContext.Provider>
  );
}

export function useAudio() {
  const context = useContext(AudioContext);
  if (context === undefined) {
    throw new Error('useAudio must be used within an AudioProvider');
  }
  return context;
}
