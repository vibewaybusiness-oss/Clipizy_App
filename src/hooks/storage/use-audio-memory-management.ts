/**
 * AUDIO MEMORY MANAGEMENT HOOK
 * Centralized audio resource management with middleware support
 * Prevents memory leaks and provides consistent audio handling across the app
 */

import { useRef, useCallback, useEffect } from 'react';
import { useMemoryManagement } from '@/utils/memory-management';

export interface AudioMemoryManager {
  createAudioBlobURL: (file: File) => string;
  revokeAudioBlobURL: (url: string) => void;
  createAudioElement: (src: string) => HTMLAudioElement;
  cleanupAudioElement: (audio: HTMLAudioElement) => void;
  addAudioEventListener: (audio: HTMLAudioElement, event: string, handler: EventListener) => void;
  removeAudioEventListener: (audio: HTMLAudioElement, event: string, handler: EventListener) => void;
  cleanup: () => void;
  getStats: () => AudioMemoryStats;
}

export interface AudioMemoryStats {
  audioElements: number;
  audioBlobURLs: number;
  totalMemoryUsage: number;
}

export interface AudioMiddleware {
  onAudioCreate?: (audio: HTMLAudioElement) => void;
  onAudioDestroy?: (audio: HTMLAudioElement) => void;
  onBlobURLCreate?: (url: string, file: File) => void;
  onBlobURLRevoke?: (url: string) => void;
}

export function useAudioMemoryManagement(middleware?: AudioMiddleware): AudioMemoryManager {
  const { blobManager, eventManager, cleanup: globalCleanup } = useMemoryManagement();
  const audioElementsRef = useRef<Set<HTMLAudioElement>>(new Set());
  const audioBlobURLsRef = useRef<Set<string>>(new Set());

  const createAudioBlobURL = useCallback((file: File): string => {
    const url = blobManager.createURL(file);
    audioBlobURLsRef.current.add(url);
    
    // Call middleware
    middleware?.onBlobURLCreate?.(url, file);
    
    console.debug(`AudioMemoryManager: Created audio blob URL for ${file.name}`);
    return url;
  }, [blobManager, middleware]);

  const revokeAudioBlobURL = useCallback((url: string): void => {
    if (audioBlobURLsRef.current.has(url)) {
      blobManager.revokeURL(url);
      audioBlobURLsRef.current.delete(url);
      
      // Call middleware
      middleware?.onBlobURLRevoke?.(url);
      
      console.debug('AudioMemoryManager: Revoked audio blob URL');
    }
  }, [blobManager, middleware]);

  const createAudioElement = useCallback((src: string): HTMLAudioElement => {
    const audio = new Audio(src);
    audioElementsRef.current.add(audio);
    
    // Call middleware
    middleware?.onAudioCreate?.(audio);
    
    console.debug('AudioMemoryManager: Created audio element');
    return audio;
  }, [middleware]);

  const cleanupAudioElement = useCallback((audio: HTMLAudioElement): void => {
    if (audioElementsRef.current.has(audio)) {
      // Call middleware before cleanup
      middleware?.onAudioDestroy?.(audio);
      
      // Pause and reset audio
      audio.pause();
      audio.currentTime = 0;
      audio.src = '';
      audio.load();
      
      // Remove from tracking
      audioElementsRef.current.delete(audio);
      console.debug('AudioMemoryManager: Cleaned up audio element');
    }
  }, [middleware]);

  const addAudioEventListener = useCallback((
    audio: HTMLAudioElement,
    event: string,
    handler: EventListener
  ): void => {
    eventManager.add(audio, event, handler);
    console.debug(`AudioMemoryManager: Added ${event} listener to audio element`);
  }, [eventManager]);

  const removeAudioEventListener = useCallback((
    audio: HTMLAudioElement,
    event: string,
    handler: EventListener
  ): void => {
    eventManager.remove(audio, event, handler);
    console.debug(`AudioMemoryManager: Removed ${event} listener from audio element`);
  }, [eventManager]);

  const getStats = useCallback((): AudioMemoryStats => {
    return {
      audioElements: audioElementsRef.current.size,
      audioBlobURLs: audioBlobURLsRef.current.size,
      totalMemoryUsage: audioElementsRef.current.size * 1024 + audioBlobURLsRef.current.size * 512 // Rough estimate
    };
  }, []);

  const cleanup = useCallback((): void => {
    const audioCount = audioElementsRef.current.size;
    const blobCount = audioBlobURLsRef.current.size;
    
    audioElementsRef.current.forEach(audio => {
      middleware?.onAudioDestroy?.(audio);
      audio.pause();
      audio.currentTime = 0;
      audio.src = '';
      audio.load();
    });
    audioElementsRef.current.clear();

    audioBlobURLsRef.current.forEach(url => {
      middleware?.onBlobURLRevoke?.(url);
      blobManager.revokeURL(url);
    });
    audioBlobURLsRef.current.clear();

    globalCleanup();

    if (audioCount > 0 || blobCount > 0) {
      console.debug(`AudioMemoryManager: Cleaned up ${audioCount} audio elements and ${blobCount} blob URLs`);
    }
  }, [blobManager, globalCleanup, middleware]);

  // DON'T cleanup on unmount - blob URLs should persist
  // The cleanup function should only be called explicitly when needed
  useEffect(() => {
    return () => {
      // Don't call cleanup() here - it would revoke all blob URLs
      // Blob URLs should persist for the lifetime of the app
      console.debug('AudioMemoryManager: Component unmounting but NOT cleaning up blob URLs');
    };
  }, []);

  return {
    createAudioBlobURL,
    revokeAudioBlobURL,
    createAudioElement,
    cleanupAudioElement,
    addAudioEventListener,
    removeAudioEventListener,
    cleanup,
    getStats,
  };
}

// =========================
// GLOBAL AUDIO MIDDLEWARE
// =========================

// Global middleware registry for audio events
const globalAudioMiddleware: AudioMiddleware[] = [];

export function registerAudioMiddleware(middleware: AudioMiddleware): () => void {
  globalAudioMiddleware.push(middleware);
  
  // Return unregister function
  return () => {
    const index = globalAudioMiddleware.indexOf(middleware);
    if (index > -1) {
      globalAudioMiddleware.splice(index, 1);
    }
  };
}

// Enhanced audio memory management with global middleware
export function useGlobalAudioMemoryManagement(): AudioMemoryManager {
  const combinedMiddleware: AudioMiddleware = {
    onAudioCreate: (audio) => {
      globalAudioMiddleware.forEach(m => m.onAudioCreate?.(audio));
    },
    onAudioDestroy: (audio) => {
      globalAudioMiddleware.forEach(m => m.onAudioDestroy?.(audio));
    },
    onBlobURLCreate: (url, file) => {
      globalAudioMiddleware.forEach(m => m.onBlobURLCreate?.(url, file));
    },
    onBlobURLRevoke: (url) => {
      globalAudioMiddleware.forEach(m => m.onBlobURLRevoke?.(url));
    }
  };

  return useAudioMemoryManagement(combinedMiddleware);
}

// =========================
// UTILITY HOOKS
// =========================

// Utility hook for managing a single audio element
export function useManagedAudioElement(src?: string) {
  const audioManager = useGlobalAudioMemoryManagement();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const currentSrcRef = useRef<string | null>(null);

  const setAudioSrc = useCallback((newSrc: string) => {
    // Clean up previous audio element
    if (audioRef.current) {
      audioManager.cleanupAudioElement(audioRef.current);
      audioRef.current = null;
    }

    // Revoke previous blob URL if it was a blob
    if (currentSrcRef.current && currentSrcRef.current.startsWith('blob:')) {
      audioManager.revokeAudioBlobURL(currentSrcRef.current);
    }

    // Create new audio element
    if (newSrc) {
      audioRef.current = audioManager.createAudioElement(newSrc);
      currentSrcRef.current = newSrc;
    }
  }, [audioManager]);

  const cleanup = useCallback(() => {
    if (audioRef.current) {
      audioManager.cleanupAudioElement(audioRef.current);
      audioRef.current = null;
    }
    if (currentSrcRef.current && currentSrcRef.current.startsWith('blob:')) {
      audioManager.revokeAudioBlobURL(currentSrcRef.current);
      currentSrcRef.current = null;
    }
  }, [audioManager]);

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  // Set initial src if provided
  useEffect(() => {
    if (src) {
      setAudioSrc(src);
    }
  }, [src, setAudioSrc]);

  return {
    audioElement: audioRef.current,
    setAudioSrc,
    cleanup,
  };
}

// Hook for managing audio file uploads with automatic cleanup
export function useManagedAudioFile(file?: File) {
  const audioManager = useGlobalAudioMemoryManagement();
  const blobURLRef = useRef<string | null>(null);

  const createBlobURL = useCallback((audioFile: File): string => {
    // Clean up previous blob URL
    if (blobURLRef.current) {
      audioManager.revokeAudioBlobURL(blobURLRef.current);
    }

    // Create new blob URL
    const url = audioManager.createAudioBlobURL(audioFile);
    blobURLRef.current = url;
    return url;
  }, [audioManager]);

  const cleanup = useCallback(() => {
    if (blobURLRef.current) {
      audioManager.revokeAudioBlobURL(blobURLRef.current);
      blobURLRef.current = null;
    }
  }, [audioManager]);

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  // Create blob URL when file changes
  useEffect(() => {
    if (file) {
      createBlobURL(file);
    } else {
      cleanup();
    }
  }, [file, createBlobURL, cleanup]);

  return {
    blobURL: blobURLRef.current,
    createBlobURL,
    cleanup,
  };
}

// =========================
// AUDIO MIDDLEWARE UTILITIES
// =========================

// Logging middleware for debugging
export function createLoggingMiddleware(): AudioMiddleware {
  return {
    onAudioCreate: (audio) => {
      console.debug('🎵 Audio element created:', audio.src);
    },
    onAudioDestroy: (audio) => {
      console.debug('🎵 Audio element destroyed:', audio.src);
    },
    onBlobURLCreate: (url, file) => {
      console.debug('🎵 Blob URL created:', file.name, url);
    },
    onBlobURLRevoke: (url) => {
      console.debug('🎵 Blob URL revoked:', url);
    }
  };
}

// Performance monitoring middleware
export function createPerformanceMiddleware(): AudioMiddleware {
  const startTimes = new Map<string, number>();
  
  return {
    onAudioCreate: (audio) => {
      startTimes.set(audio.src, performance.now());
    },
    onAudioDestroy: (audio) => {
      const startTime = startTimes.get(audio.src);
      if (startTime) {
        const duration = performance.now() - startTime;
        console.debug(`🎵 Audio element lifetime: ${duration.toFixed(2)}ms`);
        startTimes.delete(audio.src);
      }
    },
    onBlobURLCreate: (url, file) => {
      startTimes.set(url, performance.now());
    },
    onBlobURLRevoke: (url) => {
      const startTime = startTimes.get(url);
      if (startTime) {
        const duration = performance.now() - startTime;
        console.debug(`🎵 Blob URL lifetime: ${duration.toFixed(2)}ms`);
        startTimes.delete(url);
      }
    }
  };
}
