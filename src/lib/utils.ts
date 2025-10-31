import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// =========================
// TIME FORMATTING UTILITIES
// =========================

export function formatTime(seconds: number): string {
  if (isNaN(seconds) || seconds < 0) return "00:00";
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`;
}

export function formatTimeWithHours(seconds: number): string {
  if (isNaN(seconds) || seconds < 0) return "00:00:00";
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`;
  } else {
    return `${minutes.toString().padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`;
  }
}

export function formatDuration(seconds: number): string {
  return formatTimeWithHours(seconds);
}

// =========================
// AUDIO UTILITIES
// =========================

export function getEnergyLevel(energy: number): string {
  if (!energy || isNaN(energy)) return "Unknown";
  if (energy > 0.7) return "High";
  if (energy > 0.4) return "Medium";
  return "Low";
}

export function getHarmonicLevel(harmonic: number): string {
  if (!harmonic || isNaN(harmonic)) return "Unknown";
  if (harmonic > 0.7) return "Harmonic";
  if (harmonic > 0.4) return "Mixed";
  return "Percussive";
}

export function getTempoDescription(tempo: number): string {
  if (tempo < 60) return 'Very Slow (Largo)';
  if (tempo < 80) return 'Slow (Adagio)';
  if (tempo < 100) return 'Moderate (Andante)';
  if (tempo < 120) return 'Moderately Fast (Moderato)';
  if (tempo < 140) return 'Fast (Allegro)';
  if (tempo < 180) return 'Very Fast (Presto)';
  return 'Extremely Fast (Prestissimo)';
}

// =========================
// PERFORMANCE UTILITIES
// =========================

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// =========================
// VALIDATION UTILITIES
// =========================

export function isValidAudioFile(file: File): boolean {
  const supportedTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/m4a', 'audio/aac'];
  const fileType = file.type || '';
  
  return supportedTypes.some(type => fileType.includes(type)) || 
         file.name.match(/\.(mp3|wav|ogg|m4a|aac)$/i) !== null;
}

export function isValidImageFile(file: File): boolean {
  return file.type.startsWith('image/');
}

export function isValidVideoFile(file: File): boolean {
  return file.type.startsWith('video/');
}

// =========================
// STRING UTILITIES
// =========================

export function truncateText(text: string | undefined | null, maxLength: number = 20): string {
  if (!text) return 'Untitled';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export function capitalizeFirst(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// =========================
// ARRAY UTILITIES
// =========================

export function areArraysEqual<T>(a: T[], b: T[]): boolean {
  if (a.length !== b.length) return false;
  return a.every((val, index) => val === b[index]);
}

export function areObjectsEqual<T extends Record<string, any>>(a: T, b: T): boolean {
  const aKeys = Object.keys(a);
  const bKeys = Object.keys(b);
  if (aKeys.length !== bKeys.length) return false;
  for (const key of aKeys) {
    if (a[key] !== b[key]) return false;
  }
  return true;
}

// =========================
// FILE UTILITIES
// =========================

export function fileToDataUri(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
}
