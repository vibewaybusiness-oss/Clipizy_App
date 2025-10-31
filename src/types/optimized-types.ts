// =========================
// OPTIMIZED TYPE DEFINITIONS
// =========================

// =========================
// CORE TYPES
// =========================

export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}


// =========================
// PROJECT TYPES
// =========================

export interface Project extends BaseEntity {
  name: string;
  description?: string;
  status: ProjectStatus;
  type: ProjectType;
  userId: string;
  settings: ProjectSettings;
  metadata: ProjectMetadata;
}

export type ProjectStatus = 'draft' | 'processing' | 'completed' | 'failed' | 'archived';
export type ProjectType = 'music-clip' | 'video' | 'audio' | 'image';

export interface ProjectSettings {
  quality: 'low' | 'medium' | 'high' | 'ultra';
  format: 'mp4' | 'mov' | 'avi' | 'webm';
  resolution: {
    width: number;
    height: number;
  };
  duration?: number;
  customSettings?: Record<string, any>;
}

export interface ProjectMetadata {
  fileCount: number;
  totalSize: number;
  processingTime?: number;
  creditsUsed: number;
  tags: string[];
  category?: string;
}

// =========================
// TRACK TYPES
// =========================

export interface Track extends BaseEntity {
  name: string;
  fileName: string;
  fileSize: number;
  mimeType: string;
  duration: number;
  projectId: string;
  userId: string;
  analysis?: AudioAnalysis;
  metadata: TrackMetadata;
}

export interface AudioAnalysis {
  tempo: number;
  key: string;
  energy: number;
  valence: number;
  danceability: number;
  acousticness: number;
  instrumentalness: number;
  speechiness: number;
  loudness: number;
  segments: AudioSegment[];
  sections: AudioSection[];
  bars: AudioBar[];
  beats: AudioBeat[];
  tatums: AudioTatum[];
}

export interface AudioSegment {
  start: number;
  duration: number;
  confidence: number;
  loudnessStart: number;
  loudnessMax: number;
  loudnessMaxTime: number;
  loudnessEnd: number;
  pitches: number[];
  timbre: number[];
}

export interface AudioSection {
  start: number;
  duration: number;
  confidence: number;
  loudness: number;
  tempo: number;
  tempoConfidence: number;
  key: number;
  keyConfidence: number;
  mode: number;
  modeConfidence: number;
  timeSignature: number;
  timeSignatureConfidence: number;
}

export interface AudioBar {
  start: number;
  duration: number;
  confidence: number;
}

export interface AudioBeat {
  start: number;
  duration: number;
  confidence: number;
}

export interface AudioTatum {
  start: number;
  duration: number;
  confidence: number;
}

export interface TrackMetadata {
  artist?: string;
  album?: string;
  genre?: string;
  year?: number;
  bitrate?: number;
  sampleRate?: number;
  channels?: number;
  codec?: string;
}


// =========================
// API TYPES
// =========================

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
  pagination?: PaginationInfo;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
  cache?: boolean;
  cacheDuration?: number;
}

// =========================
// SANITIZER TYPES
// =========================
// Note: Sanitizer types are now imported from './sanitizer'


// =========================
// ADMIN TYPES
// =========================

export interface AdminStats {
  totalUsers: number;
  activeUsers: number;
  totalProjects: number;
  totalRevenue: number;
  conversionRate: number;
}


// =========================
// MEMORY MANAGEMENT TYPES
// =========================

// BlobURLManager and EventListenerManager are imported from utils/memory-management

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

// =========================
// UTILITY TYPES
// =========================

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type NonNullable<T> = T extends null | undefined ? never : T;

export type Prettify<T> = {
  [K in keyof T]: T[K];
} & {};

// =========================
// FORM TYPES
// =========================

export interface FormField<T = any> {
  value: T;
  error?: string;
  touched: boolean;
  dirty: boolean;
  valid: boolean;
}

export interface FormState<T = Record<string, any>> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  dirty: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
  isSubmitting: boolean;
  isDirty: boolean;
}

export interface FormActions<T = Record<string, any>> {
  setValue: (field: keyof T, value: T[keyof T]) => void;
  setError: (field: keyof T, error: string) => void;
  setTouched: (field: keyof T, touched: boolean) => void;
  setDirty: (field: keyof T, dirty: boolean) => void;
  reset: () => void;
  submit: () => Promise<void>;
  validate: () => boolean;
}

// =========================
// HOOK TYPES
// =========================

export interface UseAsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: any[]) => Promise<T>;
  reset: () => void;
}

export interface UsePaginationState<T> {
  items: T[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  loadMore: () => void;
  refresh: () => void;
  reset: () => void;
}

export interface UseSearchState<T> {
  query: string;
  results: T[];
  loading: boolean;
  error: string | null;
  search: (query: string) => void;
  clear: () => void;
}

// =========================
// EXPORT ALL TYPES
// =========================

export * from './components';
export * from './sanitizer';
export * from './settings';
