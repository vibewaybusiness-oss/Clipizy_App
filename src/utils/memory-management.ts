"use client";

/**
 * Memory Management Utilities
 * Provides comprehensive memory management for blob URLs, event listeners, and other resources
 */

import { useEffect, useRef, useCallback } from 'react';

// Types for memory management
export interface BlobURLManager {
  createURL: (file: File | Blob) => string;
  revokeURL: (url: string) => void;
  revokeAll: () => void;
  getActiveURLs: () => string[];
  cleanup: () => void;
  findExistingValidURL: (file: File | Blob) => string | null;
  validateBlobURL: (url: string) => Promise<boolean>;
}

export interface EventListenerManager {
  add: (element: EventTarget, event: string, handler: EventListener, options?: AddEventListenerOptions) => void;
  remove: (element: EventTarget, event: string, handler: EventListener) => void;
  removeAll: () => void;
  cleanup: () => void;
}

export interface TimerManager {
  setTimeout: (callback: () => void, delay: number) => number;
  setInterval: (callback: () => void, delay: number) => number;
  clearTimeout: (id: number) => void;
  clearInterval: (id: number) => void;
  clearAll: () => void;
  cleanup: () => void;
}

export interface AnimationFrameManager {
  request: (callback: FrameRequestCallback) => number;
  cancel: (id: number) => void;
  clearAll: () => void;
  cleanup: () => void;
}

// Global managers for tracking resources
class GlobalBlobURLManager implements BlobURLManager {
  private activeURLs = new Set<string>();
  private urlToFile = new Map<string, File | Blob>();
  private fileToUrl = new Map<string, string>(); // Track file hash to URL mapping

  // Generate a unique hash for a file/blob
  private getFileHash(file: File | Blob): string {
    if (file instanceof File) {
      return `${file.name}_${file.size}_${file.type}_${file.lastModified}`;
    }
    return `${file.size}_${file.type}_${Date.now()}`;
  }

  // Check if a valid blob URL already exists for this file
  private findExistingValidURL(file: File | Blob): string | null {
    const fileHash = this.getFileHash(file);
    const existingUrl = this.fileToUrl.get(fileHash);
    
    if (existingUrl && this.activeURLs.has(existingUrl)) {
      // For now, assume existing URLs are valid to avoid false positives
      // The validation will happen when the URL is actually used
      return existingUrl;
    }
    
    return null;
  }

  createURL(file: File | Blob): string {
    // Check for existing valid blob URL first
    const existingUrl = this.findExistingValidURL(file);
    if (existingUrl) {
      console.debug(`MemoryManager: Reusing existing blob URL for ${file instanceof File ? file.name : 'blob'}`);
      return existingUrl;
    }

    // Create new blob URL
    const url = URL.createObjectURL(file);
    const fileHash = this.getFileHash(file);
    
    this.activeURLs.add(url);
    this.urlToFile.set(url, file);
    this.fileToUrl.set(fileHash, url);
    
    console.debug(`MemoryManager: Created new blob URL for ${file instanceof File ? file.name : 'blob'}`);
    return url;
  }

  revokeURL(url: string): void {
    if (this.activeURLs.has(url)) {
      try {
        URL.revokeObjectURL(url);
        this.activeURLs.delete(url);
        
        // Clean up file-to-URL mapping
        const file = this.urlToFile.get(url);
        if (file) {
          const fileHash = this.getFileHash(file);
          this.fileToUrl.delete(fileHash);
        }
        
        this.urlToFile.delete(url);
        console.debug('MemoryManager: Revoked blob URL');
      } catch (error) {
        console.warn('MemoryManager: Failed to revoke blob URL:', error);
      }
    }
  }

  revokeAll(): void {
    const urls = Array.from(this.activeURLs);
    urls.forEach(url => this.revokeURL(url));
    if (urls.length > 0) {
      console.debug(`MemoryManager: Revoked ${urls.length} blob URLs`);
    }
  }

  getActiveURLs(): string[] {
    return Array.from(this.activeURLs);
  }

  // Public method to find existing valid URL for a file
  findExistingValidURL(file: File | Blob): string | null {
    const fileHash = this.getFileHash(file);
    const existingUrl = this.fileToUrl.get(fileHash);
    
    if (existingUrl && this.activeURLs.has(existingUrl)) {
      return existingUrl;
    }
    
    return null;
  }

  // Public method to validate if a blob URL is still valid
  validateBlobURL(url: string): Promise<boolean> {
    return new Promise((resolve) => {
      if (!url.startsWith('blob:') || !this.activeURLs.has(url)) {
        resolve(false);
        return;
      }

      const testAudio = new Audio();
      testAudio.onerror = () => {
        console.warn('Blob URL validation failed:', url);
        resolve(false);
      };
      testAudio.onloadedmetadata = () => {
        console.debug('Blob URL validation successful:', url);
        resolve(true);
      };
      testAudio.onabort = () => {
        console.warn('Blob URL validation aborted:', url);
        resolve(false);
      };

      // Set a timeout to avoid hanging
      setTimeout(() => {
        console.warn('Blob URL validation timeout:', url);
        resolve(false);
      }, 2000);

      testAudio.src = url;
    });
  }

  cleanup(): void {
    this.revokeAll();
    this.activeURLs.clear();
    this.urlToFile.clear();
    this.fileToUrl.clear();
  }
}

class GlobalEventListenerManager implements EventListenerManager {
  private listeners = new Map<string, { element: EventTarget; event: string; handler: EventListener; options?: AddEventListenerOptions }>();

  add(element: EventTarget, event: string, handler: EventListener, options?: AddEventListenerOptions): void {
    const key = `${element.constructor.name}_${event}_${Date.now()}_${Math.random()}`;
    this.listeners.set(key, { element, event, handler, options });
    element.addEventListener(event, handler, options);
    console.debug(`MemoryManager: Added event listener for ${event}`);
  }

  remove(element: EventTarget, event: string, handler: EventListener): void {
    for (const [key, listener] of this.listeners.entries()) {
      if (listener.element === element && listener.event === event && listener.handler === handler) {
        element.removeEventListener(event, handler, listener.options);
        this.listeners.delete(key);
        console.debug(`MemoryManager: Removed event listener for ${event}`);
        return;
      }
    }
  }

  removeAll(): void {
    const count = this.listeners.size;
    for (const [key, listener] of this.listeners.entries()) {
      listener.element.removeEventListener(listener.event, listener.handler, listener.options);
      this.listeners.delete(key);
    }
    if (count > 0) {
      console.debug(`MemoryManager: Removed ${count} event listeners`);
    }
  }

  cleanup(): void {
    this.removeAll();
    this.listeners.clear();
  }
}

class GlobalTimerManager implements TimerManager {
  private timeouts = new Set<number>();
  private intervals = new Set<number>();

  setTimeout(callback: () => void, delay: number): number {
    const id = window.setTimeout(() => {
      this.timeouts.delete(id);
      callback();
    }, delay);
    this.timeouts.add(id);
    console.debug(`MemoryManager: Created timeout ${id}`);
    return id;
  }

  setInterval(callback: () => void, delay: number): number {
    const id = window.setInterval(callback, delay);
    this.intervals.add(id);
    console.debug(`MemoryManager: Created interval ${id}`);
    return id;
  }

  clearTimeout(id: number): void {
    if (this.timeouts.has(id)) {
      window.clearTimeout(id);
      this.timeouts.delete(id);
      console.debug(`MemoryManager: Cleared timeout ${id}`);
    }
  }

  clearInterval(id: number): void {
    if (this.intervals.has(id)) {
      window.clearInterval(id);
      this.intervals.delete(id);
      console.debug(`MemoryManager: Cleared interval ${id}`);
    }
  }

  clearAll(): void {
    const timeoutCount = this.timeouts.size;
    const intervalCount = this.intervals.size;
    this.timeouts.forEach(id => window.clearTimeout(id));
    this.intervals.forEach(id => window.clearInterval(id));
    if (timeoutCount > 0 || intervalCount > 0) {
      console.debug(`MemoryManager: Cleared ${timeoutCount} timeouts and ${intervalCount} intervals`);
    }
    this.timeouts.clear();
    this.intervals.clear();
  }

  cleanup(): void {
    this.clearAll();
  }
}

class GlobalAnimationFrameManager implements AnimationFrameManager {
  private frames = new Set<number>();

  request(callback: FrameRequestCallback): number {
    const id = window.requestAnimationFrame((time) => {
      this.frames.delete(id);
      callback(time);
    });
    this.frames.add(id);
    console.debug(`MemoryManager: Requested animation frame ${id}`);
    return id;
  }

  cancel(id: number): void {
    if (this.frames.has(id)) {
      window.cancelAnimationFrame(id);
      this.frames.delete(id);
      console.debug(`MemoryManager: Cancelled animation frame ${id}`);
    }
  }

  clearAll(): void {
    const frameCount = this.frames.size;
    this.frames.forEach(id => window.cancelAnimationFrame(id));
    if (frameCount > 0) {
      console.debug(`MemoryManager: Cancelled ${frameCount} animation frames`);
    }
    this.frames.clear();
  }

  cleanup(): void {
    this.clearAll();
  }
}

// Global instances
export const globalBlobManager = new GlobalBlobURLManager();
export const globalEventListenerManager = new GlobalEventListenerManager();
export const globalTimerManager = new GlobalTimerManager();
export const globalAnimationFrameManager = new GlobalAnimationFrameManager();

// React hooks for memory management
export function useBlobURLManager(): BlobURLManager {
  const managerRef = useRef<BlobURLManager | null>(null);

  if (!managerRef.current) {
    managerRef.current = {
      createURL: (file: File | Blob) => globalBlobManager.createURL(file),
      revokeURL: (url: string) => globalBlobManager.revokeURL(url),
      revokeAll: () => globalBlobManager.revokeAll(),
      getActiveURLs: () => globalBlobManager.getActiveURLs(),
      cleanup: () => globalBlobManager.cleanup(),
      findExistingValidURL: (file: File | Blob) => globalBlobManager.findExistingValidURL(file),
      validateBlobURL: (url: string) => globalBlobManager.validateBlobURL(url),
    };
  }

  // DON'T cleanup on unmount - blob URLs should persist globally
  useEffect(() => {
    return () => {
      // Don't call cleanup() - blob URLs should persist for the lifetime of the app
      console.debug('BlobURLManager: Component unmounting but NOT cleaning up blob URLs');
    };
  }, []);

  return managerRef.current;
}

export function useEventListenerManager(): EventListenerManager {
  const managerRef = useRef<EventListenerManager | null>(null);

  if (!managerRef.current) {
    managerRef.current = {
      add: (element, event, handler, options) => globalEventListenerManager.add(element, event, handler, options),
      remove: (element, event, handler) => globalEventListenerManager.remove(element, event, handler),
      removeAll: () => globalEventListenerManager.removeAll(),
      cleanup: () => globalEventListenerManager.cleanup(),
    };
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (managerRef.current) {
        managerRef.current.cleanup();
      }
    };
  }, []);

  return managerRef.current;
}

export function useTimerManager(): TimerManager {
  const managerRef = useRef<TimerManager | null>(null);

  if (!managerRef.current) {
    managerRef.current = {
      setTimeout: (callback, delay) => globalTimerManager.setTimeout(callback, delay),
      setInterval: (callback, delay) => globalTimerManager.setInterval(callback, delay),
      clearTimeout: (id) => globalTimerManager.clearTimeout(id),
      clearInterval: (id) => globalTimerManager.clearInterval(id),
      clearAll: () => globalTimerManager.clearAll(),
      cleanup: () => globalTimerManager.cleanup(),
    };
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (managerRef.current) {
        managerRef.current.cleanup();
      }
    };
  }, []);

  return managerRef.current;
}

export function useAnimationFrameManager(): AnimationFrameManager {
  const managerRef = useRef<AnimationFrameManager | null>(null);

  if (!managerRef.current) {
    managerRef.current = {
      request: (callback) => globalAnimationFrameManager.request(callback),
      cancel: (id) => globalAnimationFrameManager.cancel(id),
      clearAll: () => globalAnimationFrameManager.clearAll(),
      cleanup: () => globalAnimationFrameManager.cleanup(),
    };
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (managerRef.current) {
        managerRef.current.cleanup();
      }
    };
  }, []);

  return managerRef.current;
}

// Comprehensive memory management hook
export function useMemoryManagement() {
  const blobManager = useBlobURLManager();
  const eventManager = useEventListenerManager();
  const timerManager = useTimerManager();
  const animationManager = useAnimationFrameManager();

  const cleanup = useCallback(() => {
    blobManager.cleanup();
    eventManager.cleanup();
    timerManager.cleanup();
    animationManager.cleanup();
  }, [blobManager, eventManager, timerManager, animationManager]);

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return {
    blobManager,
    eventManager,
    timerManager,
    animationManager,
    cleanup,
  };
}

// Utility functions for common memory management tasks
export function createManagedBlobURL(file: File | Blob): string {
  return globalBlobManager.createURL(file);
}

export function revokeManagedBlobURL(url: string): void {
  globalBlobManager.revokeURL(url);
}

// Centralized blob creation with validation
export function createValidatedBlobURL(file: File | Blob): string {
  // Check for existing valid blob URL first
  const existingUrl = globalBlobManager.findExistingValidURL(file);
  if (existingUrl) {
    console.debug('Using existing valid blob URL for file:', file instanceof File ? file.name : 'blob');
    return existingUrl;
  }

  // Create new blob URL
  return globalBlobManager.createURL(file);
}

// Validate and recreate blob URL if needed
export async function ensureValidBlobURL(file: File | Blob, currentUrl?: string): Promise<string> {
  // If we have a current URL, validate it first
  if (currentUrl && currentUrl.startsWith('blob:')) {
    const isValid = await globalBlobManager.validateBlobURL(currentUrl);
    if (isValid) {
      return currentUrl;
    }
    
    // URL is invalid, clean it up
    globalBlobManager.revokeURL(currentUrl);
  }

  // Create or get a valid blob URL
  return createValidatedBlobURL(file);
}

export function addManagedEventListener(
  element: EventTarget,
  event: string,
  handler: EventListener,
  options?: AddEventListenerOptions
): void {
  globalEventListenerManager.add(element, event, handler, options);
}

export function removeManagedEventListener(
  element: EventTarget,
  event: string,
  handler: EventListener
): void {
  globalEventListenerManager.remove(element, event, handler);
}

export function createManagedTimeout(callback: () => void, delay: number): number {
  return globalTimerManager.setTimeout(callback, delay);
}

export function createManagedInterval(callback: () => void, delay: number): number {
  return globalTimerManager.setInterval(callback, delay);
}

export function createManagedAnimationFrame(callback: FrameRequestCallback): number {
  return globalAnimationFrameManager.request(callback);
}

// Global cleanup function for emergency memory management
export function emergencyCleanup(): void {
  console.warn('MemoryManager: Performing emergency cleanup');
  globalBlobManager.cleanup();
  globalEventListenerManager.cleanup();
  globalTimerManager.cleanup();
  globalAnimationFrameManager.cleanup();
}

// Memory monitoring utilities
export function getMemoryStats() {
  return {
    activeBlobURLs: globalBlobManager.getActiveURLs().length,
    activeEventListeners: globalEventListenerManager['listeners'].size,
    activeTimeouts: globalTimerManager['timeouts'].size,
    activeIntervals: globalTimerManager['intervals'].size,
    activeAnimationFrames: globalAnimationFrameManager['frames'].size,
  };
}

// Auto-cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', emergencyCleanup);
  window.addEventListener('unload', emergencyCleanup);
}

// Development mode memory monitoring
if (process.env.NODE_ENV === 'development') {
  // Log memory stats every 30 seconds in development
  setInterval(() => {
    const stats = getMemoryStats();
    if (stats.activeBlobURLs > 0 || stats.activeEventListeners > 0 || stats.activeTimeouts > 0) {
      console.debug('MemoryManager: Current stats:', stats);
    }
  }, 30000);
}
