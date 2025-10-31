// =========================
// DASHBOARD UTILITIES
// =========================

import { debounce, throttle } from './utils';

export interface Project {
  id: string;
  name: string | null;
  description: string | null;
  status: 'created' | 'uploading' | 'analyzing' | 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled' | 'draft';
  type: 'music-clip' | 'video-clip' | 'short-clip';
  created_at: string;
  updated_at: string;
  user_id: string;
  preview_url?: string;
  thumbnail_url?: string;
  export_id?: string;
  media_counts?: {
    tracks: number;
    videos: number;
    images: number;
  };
}

// =========================
// PROJECT STATUS UTILITIES
// =========================

export const PROJECT_STATUS_CONFIG = {
  completed: {
    color: 'bg-emerald-500',
    text: 'Completed',
    variant: 'success' as const
  },
  processing: {
    color: 'bg-indigo-500',
    text: 'Processing',
    variant: 'processing' as const
  },
  queued: {
    color: 'bg-amber-500',
    text: 'Queued',
    variant: 'warning' as const
  },
  analyzing: {
    color: 'bg-purple-500',
    text: 'Analyzing',
    variant: 'processing' as const
  },
  uploading: {
    color: 'bg-orange-500',
    text: 'Uploading',
    variant: 'processing' as const
  },
  draft: {
    color: 'bg-gray-500',
    text: 'Draft',
    variant: 'secondary' as const
  },
  created: {
    color: 'bg-gray-500',
    text: 'Draft',
    variant: 'secondary' as const
  },
  failed: {
    color: 'bg-red-500',
    text: 'Failed',
    variant: 'destructive' as const
  },
  cancelled: {
    color: 'bg-gray-500',
    text: 'Cancelled',
    variant: 'secondary' as const
  }
} as const;

export function getStatusColor(status: string): string {
  return PROJECT_STATUS_CONFIG[status as keyof typeof PROJECT_STATUS_CONFIG]?.color || 'bg-gray-500';
}

export function getStatusText(status: string): string {
  return PROJECT_STATUS_CONFIG[status as keyof typeof PROJECT_STATUS_CONFIG]?.text || 'Unknown';
}

export function getStatusVariant(status: string) {
  return PROJECT_STATUS_CONFIG[status as keyof typeof PROJECT_STATUS_CONFIG]?.variant || 'secondary';
}

// =========================
// DATE FORMATTING UTILITIES
// =========================

export function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
  
  if (diffInHours < 1) return 'Just now';
  if (diffInHours < 24) return `${diffInHours}h ago`;
  if (diffInHours < 48) return 'Yesterday';
  return date.toLocaleDateString();
}

export function formatAbsoluteDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// =========================
// PROJECT FILTERING UTILITIES
// =========================

export interface ProjectFilters {
  searchQuery: string;
  selectedType: string;
  selectedStatus: string;
}

export function filterProjects(projects: Project[], filters: ProjectFilters): Project[] {
  let filtered = Array.isArray(projects) ? projects : [];
  
  // Handle case where projects might be an object with a projects property
  if (!Array.isArray(projects) && projects && typeof projects === 'object' && 'projects' in projects) {
    filtered = Array.isArray((projects as any).projects) ? (projects as any).projects : [];
  }

  if (filters.searchQuery) {
    const query = filters.searchQuery.toLowerCase();
    filtered = filtered.filter(project =>
      (project.name?.toLowerCase().includes(query) || false) ||
      (project.description?.toLowerCase().includes(query) || false)
    );
  }

  if (filters.selectedType !== 'all') {
    filtered = filtered.filter(project => project.type === filters.selectedType);
  }

  if (filters.selectedStatus !== 'all') {
    filtered = filtered.filter(project => {
      // Handle 'created' status as 'draft'
      const projectStatus = project.status === 'created' ? 'draft' : project.status;
      return projectStatus === filters.selectedStatus;
    });
  }

  return filtered;
}

// =========================
// PROJECT SORTING UTILITIES
// =========================

export type SortField = 'created_at' | 'name' | 'status' | 'type';
export type SortDirection = 'asc' | 'desc';

export function sortProjects(
  projects: Project[], 
  field: SortField = 'created_at', 
  direction: SortDirection = 'desc'
): Project[] {
  return [...projects].sort((a, b) => {
    let aValue: any = a[field];
    let bValue: any = b[field];

    // Handle date sorting
    if (field === 'created_at') {
      aValue = new Date(aValue).getTime();
      bValue = new Date(bValue).getTime();
    }

    // Handle string sorting
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (direction === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });
}

// =========================
// PROJECT CATEGORIZATION UTILITIES
// =========================

export function categorizeProjects(projects: Project[]) {
  const ongoing = projects.filter(project => 
    ['processing', 'queued', 'analyzing', 'uploading'].includes(project.status)
  );

  const completed = projects.filter(project => 
    project.status === 'completed'
  );

  const drafts = projects.filter(project => 
    ['draft', 'created'].includes(project.status)
  );

  const failed = projects.filter(project => 
    ['failed', 'cancelled'].includes(project.status)
  );

  return {
    ongoing,
    completed,
    drafts,
    failed,
    total: projects.length
  };
}

// =========================
// PROJECT STATISTICS UTILITIES
// =========================

export interface ProjectStats {
  total: number;
  completed: number;
  ongoing: number;
  drafts: number;
  failed: number;
  completionRate: number;
  averageProcessingTime?: number;
}

export function calculateProjectStats(projects: Project[]): ProjectStats {
  const categorized = categorizeProjects(projects);
  
  return {
    total: categorized.total,
    completed: categorized.completed.length,
    ongoing: categorized.ongoing.length,
    drafts: categorized.drafts.length,
    failed: categorized.failed.length,
    completionRate: categorized.total > 0 ? (categorized.completed.length / categorized.total) * 100 : 0
  };
}

// =========================
// PROJECT TYPE UTILITIES
// =========================

export const PROJECT_TYPES = [
  { value: 'all', label: 'All Projects', icon: null },
  { value: 'music-clip', label: 'Music Clips', icon: 'Music' },
  { value: 'video-clip', label: 'Video Clips', icon: 'Video' },
  { value: 'short-clip', label: 'Short Clips', icon: 'Film' },
] as const;

export const PROJECT_STATUSES = [
  { value: 'all', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'processing', label: 'Processing' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
  { value: 'cancelled', label: 'Cancelled' },
] as const;

// PERFORMANCE UTILITIES
export const debounceSearch = debounce;
export const throttleScroll = throttle;
