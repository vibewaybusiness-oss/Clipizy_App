// PROJECT DOMAIN TYPES
import type { MusicTrack } from './music';

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'draft' | 'active' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
  user_id: string;
  settings?: ProjectSettings;
  tracks?: MusicTrack[];
  analysis?: ProjectAnalysis;
}

export interface ProjectSettings {
  videoType: string;
  budget: number[];
  user_price?: number;
  videoStyle: string;
  animationStyle: string;
  createIndividualVideos: boolean;
  createCompilation: boolean;
  reuse_content: boolean; // CHANGED: was useSameVideoForAll
}

export interface ProjectAnalysis {
  [key: string]: any;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  settings?: Partial<ProjectSettings>;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: Project['status'];
  settings?: Partial<ProjectSettings>;
}

// Re-export MusicTrack for convenience
export type { MusicTrack } from './music';
