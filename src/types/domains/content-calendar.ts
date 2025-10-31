// CONTENT CALENDAR DOMAIN TYPES

export interface ContentCalendar {
  id: string;
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  totalWeeks: number;
  postsPerWeek: number;
  clusters: ContentCluster[];
  settings: CalendarSettings;
  createdAt: string;
  updatedAt: string;
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

export interface CalendarBlogPost {
  id: string;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  author: Author;
  scheduledFor?: string;
  publishedAt?: string;
  tags: string[];
  category: string;
  status: 'draft' | 'scheduled' | 'published' | 'archived';
  priority: 'high' | 'medium' | 'low';
  keywords: string[];
  cluster: string;
  week: number;
  month: number;
  views: number;
  likes: number;
  readTime: number;
  createdAt: string;
  updatedAt: string;
}

export interface Author {
  name: string;
  email: string;
  avatar?: string;
  bio?: string;
}

export interface CalendarSettings {
  publishingDays: string[];
  timezone: string;
  defaultAuthor: Author;
}



