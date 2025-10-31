'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Music,
  Video,
  Film,
  Search,
  CheckSquare,
  Square,
  Trash2
} from 'lucide-react';
import { useProjects } from '@/hooks/storage/use-projects';
import { Project } from '@/lib/dashboard-utils';
import { ProjectCard } from '@/components/projects/project-card';
import { ClipizyLoading } from '@/components/ui/clipizy-loading';
import { useProjectFilters, useProjectSelection } from '@/hooks/dashboard';
import { PROJECT_TYPES, PROJECT_STATUSES } from '@/lib/dashboard-utils';

// Project types and statuses are now imported from shared utilities


export default function ProjectsPage() {
  const router = useRouter();
  const { projects, loading, error, deleteProject } = useProjects();
  
  // Convert API projects to dashboard format
  const dashboardProjects = useMemo(() => {
    return (projects || []).map(project => ({
      ...project,
      description: project.description || null,
      name: project.name || null,
      status: project.status === 'archived' ? 'draft' : project.status as any,
      type: project.type === 'custom' ? 'music-clip' : project.type as any
    }));
  }, [projects]);

  // Use optimized filtering hook
  const {
    filters,
    filteredProjects,
    updateFilters,
    clearFilters,
    hasActiveFilters
  } = useProjectFilters(dashboardProjects);
  
  // Extract filter values for easier access
  const { searchQuery, selectedType, selectedStatus } = filters;

  // Use optimized selection hook
  const {
    selectionMode,
    selectedProjects,
    toggleSelectionMode,
    selectProject,
    selectAll,
    clearSelection,
    isAllSelected,
    isPartiallySelected
  } = useProjectSelection(filteredProjects);

  const handleDeleteProject = useCallback(async (projectId: string) => {
    try {
      await deleteProject(projectId);
    } catch (error) {
      console.error('Error deleting project:', error);
    }
  }, [deleteProject]);

  const handlePlayProject = useCallback((project: any) => {
    // Navigate to generation overview for processing/completed projects, otherwise to create page
    if (project.status === 'processing' || project.status === 'completed' || project.status === 'queued') {
      router.push(`/dashboard/create/generation-overview?projectId=${project.id}`);
    } else {
      // All draft/created projects go to the unified create page
      router.push(`/dashboard/create?projectId=${project.id}`);
    }
  }, [router]);


  const handleDeleteSelected = useCallback(async () => {
    if (selectedProjects.size === 0) return;
    
    const confirmed = confirm(`Are you sure you want to delete ${selectedProjects.size} project(s)?`);
    if (!confirmed) return;

    try {
      for (const projectId of selectedProjects) {
        await deleteProject(projectId);
      }
      clearSelection();
    } catch (error) {
      console.error('Error deleting projects:', error);
    }
  }, [selectedProjects, deleteProject, clearSelection]);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <ClipizyLoading message="Loading projects..." size="lg" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center py-12">
          <div className="text-red-500 mb-4">
            <Music className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading projects</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-gray-600">
            Manage your video and music projects
            {!loading && (
              <span className="ml-2 text-sm">
                ({filteredProjects.length} {filteredProjects.length === 1 ? 'project' : 'projects'})
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {selectionMode && selectedProjects.size > 0 && (
            <Button variant="destructive" onClick={handleDeleteSelected}>
              <Trash2 className="w-4 h-4 mr-2" />
              Delete ({selectedProjects.size})
            </Button>
          )}
          <Button variant={selectionMode ? "default" : "outline"} onClick={toggleSelectionMode}>
            {selectionMode ? (
              <>
                <CheckSquare className="w-4 h-4 mr-2" />
                Exit Selection
              </>
            ) : (
              <>
                <Square className="w-4 h-4 mr-2" />
                Select
              </>
            )}
          </Button>
          <Button onClick={() => router.push('/dashboard/create')}>
            <Music className="w-4 h-4 mr-2" />
            New Project
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search projects..."
              value={filters.searchQuery}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateFilters({ searchQuery: e.target.value })}
              className="pl-10"
            />
          </div>
          <Select value={filters.selectedType} onValueChange={(value) => updateFilters({ selectedType: value })}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              {PROJECT_TYPES.map((type) => {
                const IconComponent = type.icon;
                return (
                  <SelectItem key={type.value} value={type.value}>
                    <div className="flex items-center">
                      {IconComponent && <IconComponent className="w-4 h-4 mr-2" />}
                      {type.label}
                    </div>
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
          <Select value={filters.selectedStatus} onValueChange={(value) => updateFilters({ selectedStatus: value })}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              {PROJECT_STATUSES.map((status) => (
                <SelectItem key={status.value} value={status.value}>
                  {status.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Active Filters */}
        {hasActiveFilters && (
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm text-gray-600">Active filters:</span>
            {filters.searchQuery && (
              <Badge variant="secondary" className="gap-1">
                Search: "{filters.searchQuery}"
                <button
                  onClick={() => updateFilters({ searchQuery: '' })}
                  className="ml-1 hover:text-destructive"
                >
                  ×
                </button>
              </Badge>
            )}
            {filters.selectedType !== 'all' && (
              <Badge variant="secondary" className="gap-1">
                Type: {PROJECT_TYPES.find(t => t.value === filters.selectedType)?.label}
                <button
                  onClick={() => updateFilters({ selectedType: 'all' })}
                  className="ml-1 hover:text-destructive"
                >
                  ×
                </button>
              </Badge>
            )}
            {filters.selectedStatus !== 'all' && (
              <Badge variant="secondary" className="gap-1">
                Status: {PROJECT_STATUSES.find(s => s.value === filters.selectedStatus)?.label}
                <button
                  onClick={() => updateFilters({ selectedStatus: 'all' })}
                  className="ml-1 hover:text-destructive"
                >
                  ×
                </button>
              </Badge>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="text-xs h-7"
            >
              Clear all
            </Button>
          </div>
        )}
      </div>

      {selectionMode && filteredProjects.length > 0 && (
        <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
          <button
            onClick={selectAll}
            className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            {isAllSelected ? (
              <CheckSquare className="w-4 h-4" />
            ) : (
              <Square className="w-4 h-4" />
            )}
            {isAllSelected ? 'Deselect All' : 'Select All'}
          </button>
          <div className="text-sm text-gray-600">
            {selectedProjects.size} of {filteredProjects.length} selected
          </div>
        </div>
      )}

      <Tabs defaultValue="grid" className="w-full">
        <TabsList>
          <TabsTrigger value="grid">Grid View</TabsTrigger>
          <TabsTrigger value="list">List View</TabsTrigger>
        </TabsList>

        <TabsContent value="grid" className="space-y-4">
          {!Array.isArray(filteredProjects) || filteredProjects.length === 0 ? (
            <div className="text-center py-12">
              <Music className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
              <p className="text-gray-600 mb-4">
                {searchQuery || selectedType !== 'all' || selectedStatus !== 'all'
                  ? 'Try adjusting your search or filters'
                  : 'Get started by creating your first project'
                }
              </p>
              <Button onClick={() => router.push('/dashboard/create')}>
                <Music className="w-4 h-4 mr-2" />
                Create Project
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.isArray(filteredProjects) && filteredProjects.map((project) => (
                <ProjectCard
                  key={project.id}
                  project={{
                    ...project,
                    name: project.name || '',
                    description: project.description || undefined,
                    type: project.type === 'video-clip' ? 'video-edit' : 
                          project.type === 'short-clip' ? 'custom' : 
                          project.type as any,
                    status: project.status === 'created' ? 'draft' : 
                            project.status === 'uploading' ? 'processing' :
                            project.status === 'analyzing' ? 'processing' :
                            project.status === 'queued' ? 'processing' :
                            project.status === 'cancelled' ? 'failed' :
                            project.status as any
                  }}
                  onDelete={handleDeleteProject}
                  onPlay={handlePlayProject}
                  onSelect={selectProject}
                  viewMode="grid"
                  isSelected={selectedProjects.has(project.id)}
                  selectionMode={selectionMode}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="list" className="space-y-4">
          <div className="space-y-2">
            {Array.isArray(filteredProjects) && filteredProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={{
                  ...project,
                  name: project.name || '',
                  description: project.description || undefined,
                  type: project.type === 'video-clip' ? 'video-edit' : 
                        project.type === 'short-clip' ? 'custom' : 
                        project.type as any,
                  status: project.status === 'created' ? 'draft' : 
                          project.status === 'uploading' ? 'processing' :
                          project.status === 'analyzing' ? 'processing' :
                          project.status === 'queued' ? 'processing' :
                          project.status === 'cancelled' ? 'failed' :
                          project.status as any
                }}
                onDelete={handleDeleteProject}
                onPlay={handlePlayProject}
                onSelect={selectProject}
                viewMode="list"
                isSelected={selectedProjects.has(project.id)}
                selectionMode={selectionMode}
              />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
