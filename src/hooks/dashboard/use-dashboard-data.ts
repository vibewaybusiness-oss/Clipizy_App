import { useState, useEffect, useMemo, useCallback } from 'react';
import { useProjects } from '@/hooks/storage/use-projects';
import { useCredits } from '@/hooks/business/use-credits';
import { useAuth } from '@/contexts/auth-context';
import { 
  categorizeProjects, 
  calculateProjectStats, 
  filterProjects, 
  sortProjects,
  type Project,
  type ProjectFilters,
  type ProjectStats
} from '@/lib/dashboard-utils';

// =========================
// DASHBOARD DATA HOOK
// =========================

export interface DashboardData {
  projects: Project[];
  stats: ProjectStats;
  categorized: {
    ongoing: Project[];
    completed: Project[];
    drafts: Project[];
    failed: Project[];
  };
  latest: Project[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useDashboardData(): DashboardData {
  const { projects, loading: projectsLoading, error: projectsError, fetchProjects } = useProjects();
  const { balance, loading: creditsLoading } = useCredits();
  const { user } = useAuth();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Memoized project processing
  const processedData = useMemo(() => {
    if (!projects || !Array.isArray(projects)) {
      return {
        stats: {
          total: 0,
          completed: 0,
          ongoing: 0,
          drafts: 0,
          failed: 0,
          completionRate: 0
        },
        categorized: {
          ongoing: [],
          completed: [],
          drafts: [],
          failed: []
        },
        latest: []
      };
    }

    const categorized = categorizeProjects(projects);
    const stats = calculateProjectStats(projects);
    const latest = sortProjects(projects, 'created_at', 'desc').slice(0, 4);

    return {
      stats,
      categorized,
      latest
    };
  }, [projects]);

  // Combined loading state
  useEffect(() => {
    setLoading(projectsLoading || creditsLoading);
  }, [projectsLoading, creditsLoading]);

  // Combined error state
  useEffect(() => {
    setError(projectsError);
  }, [projectsError]);

  const refetch = useCallback(() => {
    fetchProjects();
  }, [fetchProjects]);

  return {
    projects: projects || [],
    stats: processedData.stats,
    categorized: processedData.categorized,
    latest: processedData.latest,
    loading,
    error,
    refetch
  };
}

// =========================
// PROJECT FILTERING HOOK
// =========================

export interface UseProjectFiltersOptions {
  initialFilters?: Partial<ProjectFilters>;
  debounceMs?: number;
}

export function useProjectFilters(
  projects: Project[],
  options: UseProjectFiltersOptions = {}
) {
  const { initialFilters = {}, debounceMs = 300 } = options;
  
  const [filters, setFilters] = useState<ProjectFilters>({
    searchQuery: '',
    selectedType: 'all',
    selectedStatus: 'all',
    ...initialFilters
  });

  const [debouncedFilters, setDebouncedFilters] = useState<ProjectFilters>(filters);

  // Debounce filter changes
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(filters);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [filters, debounceMs]);

  // Memoized filtered projects
  const filteredProjects = useMemo(() => {
    return filterProjects(projects, debouncedFilters);
  }, [projects, debouncedFilters]);

  const updateFilters = useCallback((newFilters: Partial<ProjectFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      searchQuery: '',
      selectedType: 'all',
      selectedStatus: 'all'
    });
  }, []);

  return {
    filters,
    debouncedFilters,
    filteredProjects,
    updateFilters,
    clearFilters,
    hasActiveFilters: filters.searchQuery !== '' || filters.selectedType !== 'all' || filters.selectedStatus !== 'all'
  };
}

// =========================
// PROJECT SELECTION HOOK
// =========================

export interface UseProjectSelectionOptions {
  onSelectionChange?: (selectedIds: Set<string>) => void;
}

export function useProjectSelection(
  projects: Project[],
  options: UseProjectSelectionOptions = {}
) {
  const { onSelectionChange } = options;
  
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedProjects, setSelectedProjects] = useState<Set<string>>(new Set());
  const [lastSelectedIndex, setLastSelectedIndex] = useState<number>(-1);

  // Notify parent of selection changes
  useEffect(() => {
    onSelectionChange?.(selectedProjects);
  }, [selectedProjects, onSelectionChange]);

  const toggleSelectionMode = useCallback(() => {
    setSelectionMode(prev => !prev);
    setSelectedProjects(new Set());
    setLastSelectedIndex(-1);
  }, []);

  const selectProject = useCallback((projectId: string, selected: boolean) => {
    if (!selectionMode) return;

    setSelectedProjects(prev => {
      const newSet = new Set(prev);
      if (selected) {
        newSet.add(projectId);
      } else {
        newSet.delete(projectId);
      }
      return newSet;
    });

    const projectIndex = projects.findIndex(p => p.id === projectId);
    setLastSelectedIndex(projectIndex);
  }, [selectionMode, projects]);

  const selectAll = useCallback(() => {
    if (selectedProjects.size === projects.length) {
      setSelectedProjects(new Set());
    } else {
      setSelectedProjects(new Set(projects.map(p => p.id)));
    }
  }, [selectedProjects.size, projects]);

  const clearSelection = useCallback(() => {
    setSelectedProjects(new Set());
    setLastSelectedIndex(-1);
  }, []);

  return {
    selectionMode,
    selectedProjects,
    lastSelectedIndex,
    toggleSelectionMode,
    selectProject,
    selectAll,
    clearSelection,
    isAllSelected: selectedProjects.size === projects.length && projects.length > 0,
    isPartiallySelected: selectedProjects.size > 0 && selectedProjects.size < projects.length
  };
}

// =========================
// DASHBOARD STATS HOOK
// =========================

export interface DashboardStats {
  totalProjects: number;
  completedProjects: number;
  ongoingProjects: number;
  draftProjects: number;
  failedProjects: number;
  completionRate: number;
  creditsBalance: number;
  creditsLoading: boolean;
}

export function useDashboardStats(): DashboardStats {
  const { projects, loading: projectsLoading } = useProjects();
  const { balance, loading: creditsLoading } = useCredits();

  const stats = useMemo(() => {
    if (!projects || !Array.isArray(projects)) {
      return {
        totalProjects: 0,
        completedProjects: 0,
        ongoingProjects: 0,
        draftProjects: 0,
        failedProjects: 0,
        completionRate: 0,
        creditsBalance: 0,
        creditsLoading
      };
    }

    const projectStats = calculateProjectStats(projects);
    
    return {
      totalProjects: projectStats.total,
      completedProjects: projectStats.completed,
      ongoingProjects: projectStats.ongoing,
      draftProjects: projectStats.drafts,
      failedProjects: projectStats.failed,
      completionRate: projectStats.completionRate,
      creditsBalance: balance?.current_balance || 0,
      creditsLoading
    };
  }, [projects, balance, creditsLoading]);

  return stats;
}
