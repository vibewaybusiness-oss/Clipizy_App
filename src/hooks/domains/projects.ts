// PROJECT DOMAIN HOOKS
import { useState, useCallback, useEffect } from 'react';
import { projectsService } from '@/lib/api/services';
import type { CreateProjectRequest, UpdateProjectRequest, Project } from '@/types/domains';

export function useProjectsDomain() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [current, setCurrent] = useState<Project | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectsService.getProjects();
      setProjects(data.map(project => ({
        ...project,
        name: project.name || 'Untitled Project',
        description: project.description || undefined,
        status: project.status === 'processing' ? 'active' : 
                project.status === 'uploading' ? 'active' :
                project.status === 'analyzing' ? 'active' :
                project.status === 'queued' ? 'active' :
                project.status === 'failed' ? 'archived' :
                project.status === 'cancelled' ? 'archived' :
                project.status === 'created' ? 'draft' :
                project.status as 'draft' | 'active' | 'completed' | 'archived'
      })));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch projects';
      setError(errorMessage);
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const createProject = useCallback(async (data: CreateProjectRequest) => {
    try {
      setError(null);
      const newProject = await projectsService.createProject({
        ...data,
        type: 'music-clip' as const
      });
      const mappedProject = {
        ...newProject,
        name: newProject.name || 'Untitled Project',
        description: newProject.description || undefined,
        status: newProject.status === 'processing' ? 'active' : 
                newProject.status === 'uploading' ? 'active' :
                newProject.status === 'analyzing' ? 'active' :
                newProject.status === 'queued' ? 'active' :
                newProject.status === 'failed' ? 'archived' :
                newProject.status === 'cancelled' ? 'archived' :
                newProject.status === 'created' ? 'draft' :
                newProject.status as 'draft' | 'active' | 'completed' | 'archived'
      };
      setProjects(prev => [mappedProject, ...prev]);
      return mappedProject;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create project';
      setError(errorMessage);
      throw error;
    }
  }, []);

  const updateProject = useCallback(async (id: string, data: UpdateProjectRequest) => {
    try {
      setError(null);
      const updatedProject = await projectsService.updateProject(id, data);
      const mappedProject = {
        ...updatedProject,
        name: updatedProject.name || 'Untitled Project',
        description: updatedProject.description || undefined,
        status: updatedProject.status === 'processing' ? 'active' : 
                updatedProject.status === 'uploading' ? 'active' :
                updatedProject.status === 'analyzing' ? 'active' :
                updatedProject.status === 'queued' ? 'active' :
                updatedProject.status === 'failed' ? 'archived' :
                updatedProject.status === 'cancelled' ? 'archived' :
                updatedProject.status === 'created' ? 'draft' :
                updatedProject.status as 'draft' | 'active' | 'completed' | 'archived'
      };
      setProjects(prev => prev.map(p => p.id === id ? mappedProject : p));
      return mappedProject;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update project';
      setError(errorMessage);
      throw error;
    }
  }, []);

  const deleteProject = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null);
      await projectsService.deleteProject(id);
      setProjects(prev => prev.filter(p => p.id !== id));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete project';
      setError(errorMessage);
      throw error;
    }
  }, []);

  // Auto-fetch projects on mount
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return {
    items: projects,
    current,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
  };
}
