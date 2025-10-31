"use client";

import { useState, useCallback, useEffect, useRef } from 'react';
import { useToast } from '../ui/use-toast';
import { useAuth } from '@/contexts/auth-context';
import { 
  BaseProject, 
  ProjectType, 
  CreateProjectRequest, 
  UpdateProjectRequest, 
  ProjectData,
  PROJECT_CONFIGS 
} from '@/types/projects';
import { projectsAPI } from '@/lib/api/projects';

interface UseGenericProjectManagementOptions {
  projectType: ProjectType;
  storagePrefix?: string;
}

interface ProjectManagementState {
  currentProjectId: string | null;
  isProjectCreated: boolean;
  isLoadingProject: boolean;
  existingProjects: BaseProject[];
  currentProject: BaseProject | null;
}

interface ProjectManagementActions {
  createProject: (data?: Partial<CreateProjectRequest>) => Promise<string | null>;
  loadExistingProjects: () => Promise<void>;
  loadExistingProject: (projectId: string) => Promise<ProjectData | null>;
  updateProject: (projectId: string, data: UpdateProjectRequest) => Promise<void>;
  deleteProject: (projectId: string) => Promise<void>;
  setCurrentProjectId: (projectId: string | null) => void;
  clearProjectData: () => void;
  clearAllProjectData: () => void;
  saveProjectData: (projectId: string, data: ProjectData) => Promise<void>;
  loadProjectData: (projectId: string) => Promise<ProjectData | null>;
}

export function useGenericProjectManagement({
  projectType,
  storagePrefix
}: UseGenericProjectManagementOptions): {
  state: ProjectManagementState;
  actions: ProjectManagementActions;
} {
  const { toast } = useToast();
  const { user } = useAuth();
  const isLoadingProjectsRef = useRef(false);
  const isLoadingProjectRef = useRef(false);

  // Use project type specific storage prefix
  const prefix = storagePrefix || PROJECT_CONFIGS[projectType].storagePrefix;
  const projectKey = `${prefix}_currentProjectId`;
  const createdKey = `${prefix}_isProjectCreated`;

  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);
  const [isProjectCreated, setIsProjectCreated] = useState<boolean>(false);

  const [isLoadingProject, setIsLoadingProject] = useState(false);
  const [existingProjects, setExistingProjects] = useState<BaseProject[]>([]);
  const [currentProject, setCurrentProject] = useState<BaseProject | null>(null);

  // localStorage persistence removed - use backend storage

  const createProject = useCallback(async (data?: Partial<CreateProjectRequest>): Promise<string | null> => {
    if (!user?.id) {
      toast({
        variant: "destructive",
        title: "Authentication Required",
        description: "Please log in to create a project.",
      });
      return null;
    }

    if (isProjectCreated && currentProjectId) {
      // Verify the project still exists on the backend
      try {
        console.log('Verifying existing project:', currentProjectId);
        // Verify project exists on backend
        await projectsAPI.getProject(currentProjectId);
        console.log('Project verified successfully:', currentProjectId);
        return currentProjectId;
      } catch (error: any) {
        console.log('Project not found on backend, creating new one:', error);
        // Project doesn't exist, reset state and create new one
        setCurrentProjectId(null);
        setIsProjectCreated(false);
      }
    }

    const checkPendingProject = (): string | null => {
      if (typeof window === 'undefined') return null;
      
      const urlParams = new URLSearchParams(window.location.search);
      const newParam = urlParams.get('new');
      
      if (!newParam) return null;
      
      const projectKey = `pending_project_${newParam}`;
      const pendingData = sessionStorage.getItem(projectKey);
      
      if (pendingData) {
        try {
          const parsed = JSON.parse(pendingData);
          if (parsed.completed && parsed.projectId && parsed.type === projectType) {
            console.log('Found pending project in sessionStorage:', parsed.projectId);
            sessionStorage.removeItem(projectKey);
            return parsed.projectId;
          }
          
          if (parsed.error) {
            console.log('Pending project creation failed, creating new project');
            sessionStorage.removeItem(projectKey);
            return null;
          }
          
          if (!parsed.completed) {
            console.log('Project creation in progress, waiting...');
            return null;
          }
        } catch (error) {
          console.error('Error parsing pending project data:', error);
          sessionStorage.removeItem(projectKey);
        }
      }
      
      return null;
    };

    const pendingProjectId = checkPendingProject();
    if (pendingProjectId) {
      console.log('Using pending project:', pendingProjectId);
      const project = await projectsAPI.getProject(pendingProjectId);
      setCurrentProjectId(project.id);
      setIsProjectCreated(true);
      setCurrentProject(project);
      return project.id;
    }

    const waitForPendingProject = async (timestamp: string): Promise<string | null> => {
      const projectKey = `pending_project_${timestamp}`;
      const maxWaitTime = 10000;
      const checkInterval = 100;
      const startTime = Date.now();
      
      while (Date.now() - startTime < maxWaitTime) {
        const pendingData = sessionStorage.getItem(projectKey);
        if (pendingData) {
          try {
            const parsed = JSON.parse(pendingData);
            if (parsed.completed && parsed.projectId && parsed.type === projectType) {
              console.log('Pending project creation completed:', parsed.projectId);
              sessionStorage.removeItem(projectKey);
              const project = await projectsAPI.getProject(parsed.projectId);
              setCurrentProjectId(project.id);
              setIsProjectCreated(true);
              setCurrentProject(project);
              return project.id;
            }
            
            if (parsed.error) {
              console.log('Pending project creation failed, creating new project');
              sessionStorage.removeItem(projectKey);
              break;
            }
          } catch (error) {
            console.error('Error parsing pending project data:', error);
            sessionStorage.removeItem(projectKey);
            break;
          }
        }
        
        await new Promise(resolve => setTimeout(resolve, checkInterval));
      }
      
      sessionStorage.removeItem(projectKey);
      return null;
    };

    const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
    const newParam = urlParams?.get('new');
    
    if (newParam) {
      const waitedProjectId = await waitForPendingProject(newParam);
      if (waitedProjectId) {
        console.log('Project created in background, using it:', waitedProjectId);
        return waitedProjectId;
      }
    }

    try {
      console.log(`Creating new ${projectType} project...`);
      
      const projectData: CreateProjectRequest = {
        name: data?.name || `${projectType.charAt(0).toUpperCase() + projectType.slice(1)} Project ${new Date().toLocaleDateString()}`,
        description: data?.description || `AI-generated ${projectType} project`,
        type: projectType,
        settings: data?.settings,
        metadata: data?.metadata
      };

      // Create project via API
      const project = await projectsAPI.createProject(projectData);

      console.log('Project created successfully:', project.id);

      setCurrentProjectId(project.id);
      setIsProjectCreated(true);
      setCurrentProject(project);

      toast({
        title: "Project Created",
        description: `Your ${projectType} project has been created successfully.`,
      });

      return project.id;
    } catch (error: any) {
      console.error('Failed to create project:', error);
      
      toast({
        variant: "destructive",
        title: "Project Creation Failed",
        description: "Failed to create project. Please try again.",
      });
      throw error;
    }
  }, [isProjectCreated, currentProjectId, toast, user?.id, projectType]);

  const loadExistingProjects = useCallback(async () => {
    if (!user?.id) return;

    // Prevent duplicate calls using ref
    if (isLoadingProjectsRef.current) {
      console.log('Already loading projects, skipping...');
      return;
    }
    
    try {
      console.log(`Loading existing ${projectType} projects...`);
      isLoadingProjectsRef.current = true;
      setIsLoadingProject(true);
      
      // Load projects from backend
      const projects = await projectsAPI.getProjects(user.id, projectType);
      const response = { projects };
      
      setExistingProjects(response.projects);
      console.log('Loaded projects:', response.projects);
    } catch (error: any) {
      console.error('Failed to load existing projects:', error);
      
      toast({
        variant: "destructive",
        title: "Failed to Load Projects",
        description: "Could not load existing projects. Please try again.",
      });
    } finally {
      isLoadingProjectsRef.current = false;
      setIsLoadingProject(false);
    }
  }, [toast, user?.id, projectType]);

  const loadExistingProject = useCallback(async (projectId: string): Promise<ProjectData | null> => {
    if (isLoadingProjectRef.current) {
      console.log('Project already loading, skipping...');
      return null;
    }

    try {
      console.log('Loading existing project:', projectId);
      isLoadingProjectRef.current = true;
      setIsLoadingProject(true);

      // Set the project ID
      console.log('🔧 Setting currentProjectId to:', projectId);
      setCurrentProjectId(projectId);
      setIsProjectCreated(true);
      console.log('🔧 Project state updated - currentProjectId:', projectId, 'isProjectCreated: true');

      // Load project and project data from backend
      const project = await projectsAPI.getProject(projectId);
      
      // Check if project is in processing state and redirect if needed
      if (project?.status === 'processing') {
        console.log('🔄 Project is in processing state, redirecting to overview...');
        // Use window.location to ensure a full page redirect
        window.location.href = `/dashboard/create/generation-overview?projectId=${projectId}`;
        return null;
      }
      
      const projectData = await projectsAPI.loadProjectData(projectId);

      console.log('Project data loaded:', projectData);

      return projectData;
    } catch (error: any) {
      console.error('Failed to load existing project:', error);
      
      toast({
        variant: "destructive",
        title: "Project Load Failed",
        description: "Failed to load existing project. Using local data instead.",
      });

      // Don't reset the project state on error - keep the projectId
      console.log('Keeping project ID despite backend error:', projectId);
      
      return {
        settings: {},
        tracks: [],
        analysis: null,
        media: [],
        metadata: {}
      };
    } finally {
      isLoadingProjectRef.current = false;
      setIsLoadingProject(false);
    }
  }, [toast]);

  const updateProject = useCallback(async (projectId: string, data: UpdateProjectRequest) => {
    try {
      console.log(`Updating ${projectType} project:`, projectId, data);
      
      // Update project via API
      const updatedProject = await projectsAPI.updateProject(projectId, data);
      
      // Update local state
      setExistingProjects(prev =>
        prev.map(project =>
          project.id === projectId ? { ...project, ...data, updated_at: new Date().toISOString() } : project
        )
      );

      if (currentProject?.id === projectId) {
        setCurrentProject(prev => prev ? { ...prev, ...data, updated_at: new Date().toISOString() } : null);
      }

      console.log('Project updated successfully');
    } catch (error: any) {
      console.error('Failed to update project:', error);
      
      toast({
        variant: "destructive",
        title: "Update Failed",
        description: "Failed to update project. Please try again.",
      });
      throw error;
    }
  }, [toast, projectType, currentProject]);

  const deleteProject = useCallback(async (projectId: string) => {
    try {
      console.log(`Deleting ${projectType} project:`, projectId);
      
      // Delete project via API
      await projectsAPI.deleteProject(projectId);
      
      // Update local state
      setExistingProjects(prev => prev.filter(project => project.id !== projectId));
      
      if (currentProjectId === projectId) {
        setCurrentProjectId(null);
        setIsProjectCreated(false);
        setCurrentProject(null);
      }

      toast({
        title: "Project Deleted",
        description: "Project has been deleted successfully.",
      });
    } catch (error: any) {
      console.error('Failed to delete project:', error);
      
      toast({
        variant: "destructive",
        title: "Delete Failed",
        description: "Failed to delete project. Please try again.",
      });
      throw error;
    }
  }, [toast, projectType, currentProjectId]);

  const saveProjectData = useCallback(async (projectId: string, data: ProjectData) => {
    try {
      console.log(`Saving ${projectType} project data:`, projectId, data);
      
      // Save project data via API
      await projectsAPI.saveProjectData(projectId, data);
      
      console.log('Project data saved successfully');
    } catch (error: any) {
      console.error('Failed to save project data:', error);
      
      toast({
        variant: "destructive",
        title: "Save Failed",
        description: "Failed to save project data. Please try again.",
      });
      throw error;
    }
  }, [toast, projectType]);

  const loadProjectData = useCallback(async (projectId: string): Promise<ProjectData | null> => {
    try {
      console.log(`Loading ${projectType} project data:`, projectId);
      
      // Load project data via API
      const data = await projectsAPI.loadProjectData(projectId);
      
      console.log('Project data loaded successfully');
      return data;
    } catch (error: any) {
      console.error('Failed to load project data:', error);
      
      toast({
        variant: "destructive",
        title: "Load Failed",
        description: "Failed to load project data. Please try again.",
      });
      return null;
    }
  }, [toast, projectType]);

  const clearProjectData = useCallback(() => {
    setCurrentProjectId(null);
    setIsProjectCreated(false);
    setCurrentProject(null);
    setExistingProjects([]);
    
    // Clear localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem(projectKey);
      localStorage.removeItem(createdKey);
      console.log(`🔧 ${projectType} Project data cleared from localStorage`);
    }
  }, [projectKey, createdKey, projectType]);

  const setCurrentProjectIdAction = useCallback((projectId: string | null) => {
    console.log(`🔧 Setting current ${projectType} project ID:`, projectId);
    setCurrentProjectId(projectId);
    if (projectId) {
      setIsProjectCreated(true);
    }
  }, [projectType]);

  const clearAllProjectData = useCallback(() => {
    setCurrentProjectId(null);
    setIsProjectCreated(false);
    setCurrentProject(null);
    setExistingProjects([]);
    
    // Clear all localStorage data related to this project type
    if (typeof window !== 'undefined') {
      // Clear project management data
      localStorage.removeItem(projectKey);
      localStorage.removeItem(createdKey);
      
      // Clear all project-specific data
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(`${prefix}_`) && key.includes('_')) {
          localStorage.removeItem(key);
        }
      });
      
      console.log(`🔧 All ${projectType} project data cleared from localStorage`);
    }
  }, [projectKey, createdKey, prefix, projectType]);

  const state: ProjectManagementState = {
    currentProjectId,
    isProjectCreated,
    isLoadingProject,
    existingProjects,
    currentProject,
  };

  const actions: ProjectManagementActions = {
    createProject,
    loadExistingProjects,
    loadExistingProject,
    updateProject,
    deleteProject,
    setCurrentProjectId: setCurrentProjectIdAction,
    clearProjectData,
    clearAllProjectData,
    saveProjectData,
    loadProjectData,
  };

  return {
    state,
    actions,
  };
}
