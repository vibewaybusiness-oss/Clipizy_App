// CALENDAR DOMAIN TYPES
import { BlogPost as BaseBlogPost } from './blog';

export interface ContentCalendar {
  id: string;
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  totalWeeks: number;
  postsPerWeek: number;
  clusters: ContentCluster[];
  posts: CalendarBlogPost[];
  settings: CalendarSettings;
}

export interface CalendarBlogPost extends BaseBlogPost {
  priority: 'high' | 'medium' | 'low';
  keywords: string[];
  secondaryKeywords?: string[];
  cluster: string;
  week: number;
  month: number;
  seoTitle?: string;
  metaDescription?: string;
}

export interface ContentCluster {
  id: string;
  name: string;
  description: string;
  color: string;
  keywords: string[];
  targetAudience: string;
  priority: 'high' | 'medium' | 'low';
}

export interface CalendarSettings {
  publishingDays: string[];
  timezone: string;
  autoGenerate: boolean;
  geminiApiKey?: string;
  promptPrefix: string;
  promptSuffix: string;
  defaultAuthor: {
    name: string;
    email: string;
  };
}

export interface CalendarWeek {
  weekNumber: number;
  startDate: string;
  endDate: string;
  posts: CalendarBlogPost[];
  status: 'completed' | 'in-progress' | 'upcoming';
}

export interface CalendarMonth {
  monthNumber: number;
  monthName: string;
  year: number;
  weeks: CalendarWeek[];
  totalPosts: number;
  completedPosts: number;
  theme: string;
}

export interface GeminiPrompt {
  id: string;
  name: string;
  description: string;
  prefix: string;
  suffix: string;
  variables: string[];
  example: string;
  category: string;
}
