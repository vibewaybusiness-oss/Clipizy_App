"use client";

import { useEffect, useCallback, useRef } from "react";
import { autoSaveService } from "@/lib/auto-save-service";
import { ProjectType, ProjectData } from "@/types/projects";

interface UseGenericDataPersistenceOptions {
  projectId: string | null;
  userId: string | null;
  projectType: ProjectType;
  projectData: ProjectData;
  isEnabled?: boolean;
}

interface UseGenericDataPersistenceReturn {
  saveDataToBackend: () => Promise<void>;
  saveDataToBackendImmediate: () => Promise<void>;
  flushPendingSaves: () => void;
  pushDataOnRefresh: () => Promise<void>;
  loadProjectData: (projectId: string) => Promise<ProjectData | null>;
}

export function useGenericDataPersistence({
  projectId,
  userId,
  projectType,
  projectData,
  isEnabled = true
}: UseGenericDataPersistenceOptions): UseGenericDataPersistenceReturn {
  
  const lastSaveTimeRef = useRef<number>(0);
  const SAVE_DEBOUNCE_MS = 5000; // 5 seconds debounce to reduce rate limiting
  
  const pushDataToBackend = useCallback(async (
    projectId: string, 
    userId: string, 
    projectType: ProjectType,
    projectData: ProjectData
  ) => {
    const now = Date.now();
    
    if (now - lastSaveTimeRef.current < SAVE_DEBOUNCE_MS) {
      console.log('Skipping save - too soon since last save:', now - lastSaveTimeRef.current, 'ms');
      return;
    }
    
    lastSaveTimeRef.current = now;
    
    try {
      console.log(`Pushing ${projectType} data to backend for project:`, projectId, 'user:', userId);

      // Prepare data for backend with project type information
      const backendData = {
        projectId,
        projectType,
        userId,
        data: projectData,
        timestamp: now
      };

      // For immediate saves (like on page unload), flush all pending saves
      // This will save any queued data including the current data if it's already queued
      autoSaveService.flushAllSaves();
      
      console.log(`Successfully pushed ${projectType} data to backend`);
    } catch (error) {
      console.error(`Failed to push ${projectType} data to backend:`, error);
      // Don't throw error to avoid blocking page navigation
    }
  }, []);

  const saveDataToBackend = useCallback(async () => {
    console.log('saveDataToBackend called with:', { projectId, userId, projectType, isEnabled });
    
    if (!projectId || !userId || !isEnabled) {
      console.log('Skipping save - missing requirements:', { 
        hasProjectId: !!projectId, 
        hasUserId: !!userId, 
        isEnabled 
      });
      return;
    }
    
    try {
      console.log(`Starting ${projectType} data save to backend...`);
      
      // Use the auto-save service for consistent debounced saving
      const autoSaveData = {
        projectId,
        projectType,
        projectData,
        timestamp: Date.now()
      };
      
      console.log('Triggering autosave with data:', autoSaveData);
      autoSaveService.scheduleSave(projectId, autoSaveData);
      
      console.log(`${projectType} data save scheduled successfully`);
    } catch (error) {
      console.error(`Failed to save ${projectType} data to backend:`, error);
    }
  }, [projectId, userId, projectType, projectData, pushDataToBackend, isEnabled]);

  const saveDataToBackendImmediate = useCallback(async () => {
    console.log('saveDataToBackendImmediate called with:', { projectId, userId, projectType, isEnabled });
    
    if (!projectId || !userId || !isEnabled) {
      console.log('Skipping immediate save - missing requirements:', { 
        hasProjectId: !!projectId, 
        hasUserId: !!userId, 
        isEnabled 
      });
      return;
    }
    
    try {
      console.log(`Starting immediate ${projectType} data save to backend...`);
      
      // Prepare data for backend with project type information
      const backendData = {
        projectId,
        projectType,
        userId,
        data: projectData,
        timestamp: Date.now()
      };

      // Save immediately without debounce
      await autoSaveService.pushDataOnRefresh(projectId, backendData);
      
      console.log(`${projectType} data saved immediately to backend`);
    } catch (error) {
      console.error(`Failed to save ${projectType} data immediately to backend:`, error);
    }
  }, [projectId, userId, projectType, projectData, isEnabled]);

  const flushPendingSaves = useCallback(() => {
    if (!isEnabled) return;
    
    try {
      // Flush all pending auto-saves immediately
      autoSaveService.flushAllSaves();
    } catch (error) {
      console.error('Failed to flush pending saves:', error);
    }
  }, [isEnabled]);

  const pushDataOnRefresh = useCallback(async () => {
    if (projectId && userId) {
      console.log(`Pushing ${projectType} data on refresh...`);
      const autoSaveData = {
        projectId,
        projectType,
        projectData,
        timestamp: Date.now()
      };
      await autoSaveService.pushDataOnRefresh(projectId, autoSaveData);
    }
  }, [projectId, userId, projectType, projectData]);

  const loadProjectData = useCallback(async (projectId: string): Promise<ProjectData | null> => {
    try {
      console.log(`Loading ${projectType} project data...`);
      const data = await autoSaveService.loadProjectData(projectId);
      return data;
    } catch (error) {
      console.error(`Failed to load ${projectType} project data:`, error);
      return null;
    }
  }, [projectType]);

  // Data persistence is now handled by the backend storage hook
  // No need for duplicate beforeunload handlers here

  return {
    saveDataToBackend,
    saveDataToBackendImmediate,
    flushPendingSaves,
    pushDataOnRefresh,
    loadProjectData
  };
}
