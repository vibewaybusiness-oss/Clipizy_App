/**
 * Generic Project Types
 * Supports multiple project types (music-clip, video-edit, etc.)
 */

export type ProjectType = 'music-clip' | 'video-edit' | 'audio-edit' | 'image-edit' | 'custom';

export interface BaseProject {
  id: string;
  name: string;
  description?: string;
  type: ProjectType;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
  user_id: string;
  metadata?: Record<string, any>;
  preview_url?: string;
  thumbnail_url?: string;
  export_id?: string;
  media_counts?: {
    tracks: number;
    videos: number;
    images: number;
  };
}

export type ProjectStatus = 
  | 'draft' 
  | 'processing' 
  | 'queued' 
  | 'completed' 
  | 'failed' 
  | 'archived';

export interface ProjectSettings {
  [key: string]: any;
}

export interface ProjectData {
  settings?: ProjectSettings;
  tracks?: any[];
  analysis?: any;
  media?: any[];
  metadata?: Record<string, any>;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  type: ProjectType;
  settings?: ProjectSettings;
  metadata?: Record<string, any>;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: ProjectStatus;
  settings?: ProjectSettings;
  metadata?: Record<string, any>;
}

export interface ProjectStorageConfig {
  projectType: ProjectType;
  storagePrefix: string;
  allowedFileTypes: string[];
  maxFileSize: number;
  supportedOperations: string[];
}

// Project type specific configurations
export const PROJECT_CONFIGS: Record<ProjectType, ProjectStorageConfig> = {
  'music-clip': {
    projectType: 'music-clip',
    storagePrefix: 'music-clip',
    allowedFileTypes: ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg'],
    maxFileSize: 50 * 1024 * 1024, // 50MB
    supportedOperations: ['upload', 'generate', 'analyze', 'export']
  },
  'video-edit': {
    projectType: 'video-edit',
    storagePrefix: 'video-edit',
    allowedFileTypes: ['video/mp4', 'video/avi', 'video/mov', 'video/webm'],
    maxFileSize: 500 * 1024 * 1024, // 500MB
    supportedOperations: ['upload', 'edit', 'render', 'export']
  },
  'audio-edit': {
    projectType: 'audio-edit',
    storagePrefix: 'audio-edit',
    allowedFileTypes: ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac'],
    maxFileSize: 100 * 1024 * 1024, // 100MB
    supportedOperations: ['upload', 'edit', 'mix', 'export']
  },
  'image-edit': {
    projectType: 'image-edit',
    storagePrefix: 'image-edit',
    allowedFileTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    maxFileSize: 20 * 1024 * 1024, // 20MB
    supportedOperations: ['upload', 'edit', 'filter', 'export']
  },
  'custom': {
    projectType: 'custom',
    storagePrefix: 'custom',
    allowedFileTypes: ['*/*'],
    maxFileSize: 100 * 1024 * 1024, // 100MB
    supportedOperations: ['upload', 'process', 'export']
  }
};

export interface ProjectTypeHandler {
  projectType: ProjectType;
  createProject: (data: CreateProjectRequest) => Promise<BaseProject>;
  updateProject: (id: string, data: UpdateProjectRequest) => Promise<BaseProject>;
  deleteProject: (id: string) => Promise<void>;
  getProject: (id: string) => Promise<BaseProject>;
  getProjects: (userId: string) => Promise<BaseProject[]>;
  saveProjectData: (id: string, data: ProjectData) => Promise<void>;
  loadProjectData: (id: string) => Promise<ProjectData>;
  uploadFile: (projectId: string, file: File, metadata?: any) => Promise<string>;
  deleteFile: (projectId: string, fileId: string) => Promise<void>;
  getProjectFiles: (projectId: string) => Promise<any[]>;
}

export interface ProjectManager {
  getHandler: (projectType: ProjectType) => ProjectTypeHandler;
  createProject: (type: ProjectType, data: CreateProjectRequest) => Promise<BaseProject>;
  updateProject: (id: string, data: UpdateProjectRequest) => Promise<BaseProject>;
  deleteProject: (id: string) => Promise<void>;
  getProject: (id: string) => Promise<BaseProject>;
  getProjects: (userId: string, type?: ProjectType) => Promise<BaseProject[]>;
  saveProjectData: (id: string, data: ProjectData) => Promise<void>;
  loadProjectData: (id: string) => Promise<ProjectData>;
}
