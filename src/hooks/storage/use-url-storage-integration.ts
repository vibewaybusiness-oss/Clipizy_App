"use client";

import { useCallback, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useUrlManagement } from "../use-url-management";
import { useGenericProjectManagement } from "./use-project-management";
import { useGenericDataPersistence } from "./use-data-persistence";
import { ProjectType, ProjectData } from "@/types/projects";

interface UseGenericUrlStorageIntegrationOptions {
  currentStep: number;
  maxReachedStep: number;
  onStepChange: (step: number) => void;
  projectType: ProjectType;
  basePath?: string;
  projectData?: ProjectData;
  userId?: string | null;
  authLoading?: boolean;
  user?: any;
  isNewProject?: boolean;
  setShowLoading?: (loading: boolean) => void;
  enableProjectEffects?: boolean;
}

interface UseGenericUrlStorageIntegrationReturn {
  // URL Management
  urlProjectId: string | null;
  isNewProject: boolean;
  updateStepInUrl: (step: number) => void;
  updateProjectIdInUrl: (projectId: string) => void;
  preventRedirects: boolean;
  syncWithStorage: () => void;
  isStorageSynced: boolean;
  
  // Project Management
  currentProjectId: string | null;
  isProjectCreated: boolean;
  isLoadingProject: boolean;
  existingProjects: any[];
  createProject: () => Promise<string | null>;
  loadExistingProjects: () => Promise<void>;
  loadExistingProject: (projectId: string) => Promise<ProjectData | null>;
  updateProject: (projectId: string, data: any) => Promise<void>;
  setCurrentProjectId: (projectId: string | null) => void;
  clearProjectData: () => void;
  clearAllProjectData: () => void;
  
  // Data Persistence
  saveDataToBackend: () => Promise<void>;
  saveDataToBackendImmediate: () => Promise<void>;
  flushPendingSaves: () => void;
  pushDataOnRefresh: () => Promise<void>;
  loadProjectData: (projectId: string) => Promise<ProjectData | null>;
  
  // Project Effects
  handleNewProject: () => Promise<void>;
  handleProjectSwitch: (projectId: string) => Promise<void>;
  handleAuthenticationCheck: () => void;
  
  // Unified state
  unifiedProjectId: string | null;
  isUnifiedStateReady: boolean;
  isProjectEffectsEnabled: boolean;
}

export function useGenericUrlStorageIntegration({
  currentStep,
  maxReachedStep,
  onStepChange,
  projectType,
  basePath = `/dashboard/create/${projectType}`,
  projectData,
  userId,
  authLoading = false,
  user,
  isNewProject = false,
  setShowLoading,
  enableProjectEffects = true
}: UseGenericUrlStorageIntegrationOptions): UseGenericUrlStorageIntegrationReturn {
  
  const projectManagement = useGenericProjectManagement({
    projectType,
    storagePrefix: projectType
  });
  const router = useRouter();
  
  // Initialize URL management with storage sync enabled
  const urlManagement = useUrlManagement({
    projectId: projectManagement.state.currentProjectId,
    currentStep,
    maxReachedStep,
    onStepChange,
    onProjectIdChange: (newProjectId) => {
      if (newProjectId && newProjectId !== projectManagement.state.currentProjectId) {
        projectManagement.actions.setCurrentProjectId(newProjectId);
      }
    },
    projectType,
    basePath,
    enableStorageSync: true
  });

  // Initialize data persistence
  const dataPersistence = useGenericDataPersistence({
    projectId: urlManagement.urlProjectId || projectManagement.state.currentProjectId,
    userId: userId || null,
    projectType,
    projectData: projectData || {
      settings: {},
      tracks: [],
      analysis: null,
      media: [],
      metadata: {}
    },
    isEnabled: !!(urlManagement.urlProjectId || projectManagement.state.currentProjectId) && !!userId
  });

  // Unified state management
  const unifiedProjectId = urlManagement.urlProjectId || projectManagement.state.currentProjectId;
  const isUnifiedStateReady = !!(unifiedProjectId && projectManagement.state.isProjectCreated);
  
  const syncTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isSyncingRef = useRef(false);
  const lastSyncedProjectIdRef = useRef<string | null>(null);

  const enhancedSyncWithStorage = useCallback(() => {
    if (isSyncingRef.current) return;
    
    if (syncTimeoutRef.current) {
      clearTimeout(syncTimeoutRef.current);
    }

    syncTimeoutRef.current = setTimeout(() => {
      if (isSyncingRef.current) return;
      isSyncingRef.current = true;
      
      if (urlManagement.urlProjectId && urlManagement.urlProjectId !== projectManagement.state.currentProjectId && urlManagement.urlProjectId !== lastSyncedProjectIdRef.current) {
        lastSyncedProjectIdRef.current = urlManagement.urlProjectId;
        projectManagement.actions.setCurrentProjectId(urlManagement.urlProjectId);
      }
      
      isSyncingRef.current = false;
    }, 100);
  }, [urlManagement.urlProjectId, projectManagement.state.currentProjectId, projectManagement.actions]);

  const enhancedCreateProject = useCallback(async (): Promise<string | null> => {
    try {
      const projectId = await projectManagement.actions.createProject();
      
      if (projectId) {
        urlManagement.updateProjectIdInUrl(projectId);
      }
      
      return projectId;
    } catch (error) {
      console.error(`Failed to create ${projectType} project:`, error);
      throw error;
    }
  }, [projectManagement, urlManagement, projectType]);

  const enhancedLoadExistingProject = useCallback(async (projectId: string): Promise<ProjectData | null> => {
    try {
      const projectData = await projectManagement.actions.loadExistingProject(projectId);
      
      urlManagement.updateProjectIdInUrl(projectId);
      
      return projectData;
    } catch (error) {
      console.error(`Failed to load ${projectType} project:`, error);
      throw error;
    }
  }, [projectManagement, urlManagement, projectType]);

  const enhancedSetCurrentProjectId = useCallback((projectId: string | null) => {
    projectManagement.actions.setCurrentProjectId(projectId);
    
    if (projectId && projectId !== urlManagement.urlProjectId) {
      urlManagement.updateProjectIdInUrl(projectId);
    }
  }, [projectManagement, urlManagement, projectType]);

  const enhancedClearProjectData = useCallback(() => {
    projectManagement.actions.clearProjectData();
    urlManagement.updateProjectIdInUrl('');
  }, [projectManagement, urlManagement, projectType]);

  const enhancedClearAllProjectData = useCallback(() => {
    projectManagement.actions.clearAllProjectData();
    urlManagement.updateProjectIdInUrl('');
  }, [projectManagement, urlManagement, projectType]);

  const handleNewProject = useCallback(async () => {
    if (!enableProjectEffects) return;
    
    try {
      await enhancedCreateProject();
    } catch (error) {
      console.error(`Failed to handle new ${projectType} project:`, error);
    }
  }, [enhancedCreateProject, enableProjectEffects, projectType]);

  const handleProjectSwitch = useCallback(async (projectId: string) => {
    if (!enableProjectEffects) return;
    
    try {
      await enhancedLoadExistingProject(projectId);
    } catch (error) {
      console.error(`Failed to switch to ${projectType} project:`, error);
    }
  }, [enhancedLoadExistingProject, enableProjectEffects, projectType]);

  const handleAuthenticationCheck = useCallback(() => {
    if (!enableProjectEffects) return;
    
    if (!user && !authLoading) {
      router.push('/auth/login');
    }
  }, [user, authLoading, router, enableProjectEffects]);

  useEffect(() => {
    if (urlManagement.urlProjectId && urlManagement.urlProjectId !== projectManagement.state.currentProjectId) {
      enhancedSyncWithStorage();
    }
  }, [urlManagement.urlProjectId]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current);
      }
    };
  }, []);

  return {
    // URL Management
    urlProjectId: urlManagement.urlProjectId,
    isNewProject: urlManagement.isNewProject,
    updateStepInUrl: urlManagement.updateStepInUrl,
    updateProjectIdInUrl: urlManagement.updateProjectIdInUrl,
    preventRedirects: urlManagement.preventRedirects,
    syncWithStorage: enhancedSyncWithStorage,
    isStorageSynced: urlManagement.isStorageSynced,
    
    // Project Management
    currentProjectId: projectManagement.state.currentProjectId,
    isProjectCreated: projectManagement.state.isProjectCreated,
    isLoadingProject: projectManagement.state.isLoadingProject,
    existingProjects: projectManagement.state.existingProjects,
    createProject: enhancedCreateProject,
    loadExistingProjects: projectManagement.actions.loadExistingProjects,
    loadExistingProject: enhancedLoadExistingProject,
    updateProject: projectManagement.actions.updateProject,
    setCurrentProjectId: enhancedSetCurrentProjectId,
    clearProjectData: enhancedClearProjectData,
    clearAllProjectData: enhancedClearAllProjectData,
    
    // Data Persistence
    saveDataToBackend: dataPersistence.saveDataToBackend,
    saveDataToBackendImmediate: dataPersistence.saveDataToBackendImmediate,
    flushPendingSaves: dataPersistence.flushPendingSaves,
    pushDataOnRefresh: dataPersistence.pushDataOnRefresh,
    loadProjectData: dataPersistence.loadProjectData,
    
    // Project Effects
    handleNewProject,
    handleProjectSwitch,
    handleAuthenticationCheck,
    
    // Unified state
    unifiedProjectId,
    isUnifiedStateReady,
    isProjectEffectsEnabled: enableProjectEffects
  };
}
