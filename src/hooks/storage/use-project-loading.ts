"use client";

import { useCallback, useState } from "react";
import { useToast } from "@/hooks/ui/use-toast";
import { projectsAPI } from "@/lib/api/projects";
import { isValidUUID } from "@/utils/music-clip-utils";

interface UseProjectLoadingProps {
  projectState: any; // Generic project state
  projectManagement: any;
  projectData: any; // Generic project data
  loadProjectSpecificData?: (projectData: any) => Promise<void>; // Project-specific loading logic
}

export function useProjectLoading({
  projectState,
  projectManagement,
  projectData,
  loadProjectSpecificData
}: UseProjectLoadingProps) {
  const { toast } = useToast();
  const [isLoadingProjectData, setIsLoadingProjectData] = useState(false);

  const loadExistingProject = useCallback(async (projectId: string) => {
    try {
      if (projectState.actions.setIsLoadingExistingProject) {
        projectState.actions.setIsLoadingExistingProject(true);
      }
      console.log('📥 Loading existing project from backend:', projectId);
      const projectData = await projectManagement.actions.loadExistingProject(projectId);
      
      console.log('Project data structure:', projectData);
      
      // Load backend data into project state
      const backendData: any = {};
      
      // Generic settings loading
      if (projectData?.script?.steps?.music?.settings) {
        const settings = projectData.script.steps.music.settings;
        console.log('Loading settings:', settings);
        
        // Apply project-specific settings fixes
        const fixedSettings = {
          ...settings,
          // Add project-specific fixes here
        };
        
        console.log('Fixed settings:', fixedSettings);
        backendData.settings = fixedSettings;
        projectState.actions.setSettings(fixedSettings);
        
        // Reset form if available
        if (projectState.forms?.settingsForm) {
          projectState.forms.settingsForm.reset(fixedSettings);
        }
      } else {
        console.log('No settings found in project data - preserving existing form values');
        if (projectState.forms?.settingsForm) {
          const currentFormValues = projectState.forms.settingsForm.getValues();
          // Set default values if needed
        }
      }
      
      // Call loadFromBackend to ensure backend data takes precedence
      if (projectState.actions.loadFromBackend) {
        projectState.actions.loadFromBackend(backendData);
      }
      
      // Load project-specific data (tracks, analysis, etc.)
      if (loadProjectSpecificData) {
        await loadProjectSpecificData(projectData);
      }
      
      // Generic project data loading
      if (projectData?.analysis) {
        console.log('Loading analysis data from project:', projectData.analysis);
        if (projectData.updateAnalysisData) {
          projectData.updateAnalysisData(projectData.analysis);
        }
      }
      
    } catch (error) {
      console.error('Failed to load existing project:', error);
      
      if (error instanceof Error && error.message.includes('Project not found')) {
        toast({
          variant: "destructive",
          title: "Project Not Found",
          description: "The selected project could not be found. Using local data instead.",
        });
      } else {
        toast({
          variant: "destructive",
          title: "Loading Error",
          description: "Failed to load the existing project from server. Using local data instead.",
        });
      }
    } finally {
      if (projectState.actions.setIsLoadingExistingProject) {
        projectState.actions.setIsLoadingExistingProject(false);
      }
    }
  }, [projectState, projectManagement, projectData, loadProjectSpecificData, toast]);

  const loadAnalysisData = useCallback(async (projectId: string) => {
    try {
      console.log('Loading analysis data for project:', projectId);
      
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      if (!token) {
        console.log('User not authenticated, skipping analysis data load');
        return;
      }
      
      // Validate token
      try {
        if (token && typeof window !== 'undefined') {
          const tokenData = JSON.parse(atob(token.split('.')[1]));
          const currentTime = Math.floor(Date.now() / 1000);
          if (tokenData.exp && tokenData.exp < currentTime) {
            console.log('Token expired, skipping analysis data load');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            return;
          }
        }
      } catch (error) {
        console.log('Invalid token format, skipping analysis data load');
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        return;
      }
      
      if (!isValidUUID(projectId)) {
        console.error('Invalid project ID format:', projectId);
        toast({
          variant: "destructive",
          title: "Invalid Project ID",
          description: "The project ID format is invalid. Please create a new project.",
        });
        return;
      }
      
      setIsLoadingProjectData(true);
      
      // This would need to be project-specific
      // For now, we'll just log that analysis data loading is needed
      console.log('Analysis data loading would be implemented here for project type');
      
    } catch (error: any) {
      console.error('Error loading analysis data:', error);
      
      if (error.status === 401 || error.status === 403) {
        console.log('Authentication error, user needs to log in');
        return;
      } else if (error.status === 404) {
        toast({
          variant: "destructive",
          title: "Project Not Found",
          description: "The project was not found. Please create a new project.",
        });
      } else if (error.status === 500) {
        toast({
          variant: "destructive",
          title: "Server Error",
          description: "There was an error loading the project data. Please try again.",
        });
      } else {
        toast({
          variant: "destructive",
          title: "Error Loading Data",
          description: `Failed to load analysis data: ${error.message || 'Unknown error'}`,
        });
      }
    } finally {
      setIsLoadingProjectData(false);
    }
  }, [toast]);

  return {
    isLoadingProjectData,
    isLoadingAnalysisData: isLoadingProjectData, // Alias for compatibility
    loadAnalysisData,
    loadExistingProject
  };
}
