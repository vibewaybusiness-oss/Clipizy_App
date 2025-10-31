import { useState, useEffect, useCallback } from 'react';
import { projectsAPI, Project, CreateProjectRequest, UpdateProjectRequest } from '@/lib/api/projects';
import { useAuth } from '@/contexts/auth-context';

export function useProjects() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await projectsAPI.getProjects(user.id);
      console.log('Raw API response:', data, 'type:', typeof data, 'isArray:', Array.isArray(data));
      
      // Handle different response structures
      let projectsArray: Project[] = [];
      if (Array.isArray(data)) {
        projectsArray = data;
      } else if (data && typeof data === 'object' && 'projects' in data) {
        projectsArray = Array.isArray((data as any).projects) ? (data as any).projects : [];
      }
      
      console.log('Processed projects array:', projectsArray);
      setProjects(projectsArray);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch projects');
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const createProject = useCallback(async (projectData: CreateProjectRequest) => {
    try {
      setError(null);
      const newProject = await projectsAPI.createProject(projectData);
      setProjects(prev => [newProject, ...prev]);
      return newProject;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
      throw err;
    }
  }, []);

  const updateProject = useCallback(async (projectId: string, projectData: UpdateProjectRequest) => {
    try {
      setError(null);
      const updatedProject = await projectsAPI.updateProject(projectId, projectData);
      setProjects(prev =>
        prev.map(project =>
          project.id === projectId ? updatedProject : project
        )
      );
      return updatedProject;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update project');
      throw err;
    }
  }, []);

  const deleteProject = useCallback(async (projectId: string) => {
    try {
      setError(null);
      await projectsAPI.deleteProject(projectId);
      setProjects(prev => prev.filter(project => project.id !== projectId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete project');
      throw err;
    }
  }, []);

  const getProject = useCallback(async (projectId: string) => {
    try {
      setError(null);
      return await projectsAPI.getProject(projectId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch project');
      throw err;
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return {
    projects,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    getProject,
  };
}

export function useProject(projectId: string) {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProject = useCallback(async () => {
    if (!projectId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await projectsAPI.getProject(projectId);
      setProject(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch project');
      console.error('Error fetching project:', err);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  return {
    project,
    loading,
    error,
    refetch: fetchProject,
  };
}
