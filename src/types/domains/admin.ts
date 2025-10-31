// ADMIN DOMAIN TYPES
import type { User } from './auth';
import type { Project } from './project';

export interface AdminStats {
  total_users: number;
  total_projects: number;
  total_videos: number;
  total_views: number;
  active_users: number;
  revenue: number;
  growth_rate: number;
}

export interface AdminUser extends User {
  last_login: string;
  is_active: boolean;
  projects_count: number;
  videos_count: number;
  credits_balance: number;
}

export interface AdminProject extends Project {
  user: {
    id: string;
    name: string;
    email: string;
  };
  tracks_count: number;
  videos_count: number;
}

// Re-export types for convenience
export type { User } from './auth';
export type { Project } from './project';
