// USER DOMAIN TYPES
import { UserSettings } from '../settings';
export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  username?: string;
  avatar?: string;
  bio?: string;
  website?: string;
  location?: string;
  created_at: string;
  updated_at: string;
}

// UserSettings is imported from '../settings'

export interface UserStats {
  total_projects: number;
  total_videos: number;
  total_views: number;
  credits_balance: number;
  join_date: string;
  last_active: string;
}
