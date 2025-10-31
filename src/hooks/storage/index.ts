// Unified Storage System - All project types supported
export { useGenericProjectManagement as useProjectManagement } from './use-project-management';
export { useGenericDataPersistence as useDataPersistence } from './use-data-persistence';
export { useGenericUrlStorageIntegration as useUrlStorageIntegration } from './use-url-storage-integration';

// Project Factory - Create project-specific handlers
export { 
  useProjectFactory, 
  useMusicClipProject, 
  useVideoEditProject, 
  useAudioEditProject, 
  useImageEditProject, 
  useCustomProject 
} from './use-project-factory';

// Core Storage Hooks
export { useFileUploadHandlers } from './use-file-upload-handlers';
export { useMusicTracks } from './use-music-tracks';
export { useProjectLoading } from './use-project-loading';
export { useProjects, useProject } from './use-projects';

// Audio Memory Management
export { 
  useAudioMemoryManagement, 
  useGlobalAudioMemoryManagement,
  useManagedAudioElement, 
  useManagedAudioFile,
  registerAudioMiddleware,
  createLoggingMiddleware,
  createPerformanceMiddleware,
  type AudioMemoryManager,
  type AudioMemoryStats,
  type AudioMiddleware
} from './use-audio-memory-management';

// Type Exports
export type { 
  ProjectManagementState, 
  ProjectManagementActions 
} from './use-generic-project-management';
