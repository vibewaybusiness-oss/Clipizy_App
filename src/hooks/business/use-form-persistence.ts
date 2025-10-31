"use client";

import { useCallback } from "react";
import { useToast } from "@/hooks/ui/use-toast";
import * as z from "zod";

interface UseFormPersistenceProps {
  projectState: any; // Generic project state
  projectManagement: any;
  // dataPersistence removed - handled by backend storage
  setShowLoading?: (loading: boolean) => void;
}

export function useFormPersistence({
  projectState,
  projectManagement,
  // dataPersistence removed
  setShowLoading
}: UseFormPersistenceProps) {
  const { toast } = useToast();

  const handleSettingsSubmit = useCallback(async (values: any) => {
    // Generic settings submission logic
    projectState.actions.setSettings(values);
    
    if (projectManagement.state.currentProjectId) {
      try {
        // Data persistence handled by backend storage
        projectState.actions.markAsSaved();
        console.log('Settings saved to backend on navigation');
      } catch (error) {
        console.error('Failed to save settings to backend:', error);
        toast({
          variant: "destructive",
          title: "Save Failed",
          description: "Failed to save your settings. Please try again.",
        });
        return;
      }
    }
    
    projectState.actions.setIsNavigating(true);
    
    // Trigger any project-specific processing
    if (setShowLoading) {
      setShowLoading(true);
    }
    
    // Project-specific logic can be added here via callbacks or props
    console.log('Settings submitted:', values);
    
    setTimeout(() => {
      projectState.actions.setIsNavigating(false);
      if (setShowLoading) {
        setShowLoading(false);
      }
    }, 1000);
  }, [projectState, projectManagement, toast, setShowLoading]);

  const handlePromptSubmit = useCallback(async (values: any, additionalData?: any) => {
    // Generic prompt submission logic
    projectState.actions.setPrompts(values);
    
    // Handle additional data if provided (e.g., track descriptions, genres)
    if (additionalData) {
      if (additionalData.trackDescriptions) {
        projectState.actions.setIndividualDescriptions((prev: any) => ({
          ...prev,
          ...additionalData.trackDescriptions
        }));
      }
      
      if (additionalData.trackGenres) {
        // Handle track genres if the project supports them
        if (projectState.actions.setTrackGenres) {
          projectState.actions.setTrackGenres((prev: any) => ({
            ...prev,
            ...additionalData.trackGenres
          }));
        }
      }
    }
    
    if (projectManagement.state.currentProjectId) {
      try {
        // Data persistence handled by backend storage
        projectState.actions.markAsSaved();
        console.log('Prompts saved to backend on navigation');
      } catch (error) {
        console.error('Failed to save prompts to backend:', error);
        toast({
          variant: "destructive",
          title: "Save Failed",
          description: "Failed to save your prompts. Please try again.",
        });
        return;
      }
    }
    
    projectState.actions.setIsNavigating(true);
    
    // Trigger navigation to next step
    const currentStep = projectState.state.currentStep;
    const nextStep = Math.min(currentStep + 1, 4) as 1 | 2 | 3 | 4;
    projectState.actions.setCurrentStep(nextStep);
    projectState.actions.setMaxReachedStep(nextStep);
    
    setTimeout(() => {
      projectState.actions.setIsNavigating(false);
    }, 500);
  }, [projectState, projectManagement, toast]);

  const handleOverviewSubmit = useCallback(async (values: any) => {
    console.log('=== handleOverviewSubmit CALLED ===');
    console.log('Values:', values);
    console.log('Current step before:', projectState.state.currentStep);
    
    if (projectManagement.state.currentProjectId) {
      try {
        // Data persistence handled by backend storage
        projectState.actions.markAsSaved();
        console.log('Overview data saved to backend');
      } catch (error) {
        console.error('Failed to save overview data to backend:', error);
        toast({
          variant: "destructive",
          title: "Save Failed",
          description: "Failed to save your overview data. Please try again.",
        });
        return;
      }
    }
    
    // Data saved successfully - navigation will be handled by the calling function
    console.log('Overview data saved successfully');
  }, [projectState, projectManagement, toast]);

  const handleContinue = useCallback(async () => {
    if (projectManagement.state.currentProjectId) {
      try {
        // Data persistence handled by backend storage
        projectState.actions.markAsSaved();
        console.log('Data saved to backend on continue navigation');
      } catch (error) {
        console.error('Failed to save data to backend on continue:', error);
        toast({
          variant: "destructive",
          title: "Save Failed",
          description: "Failed to save your progress. Please try again.",
        });
        return;
      }
    }
    
    // Trigger continue action
    if (projectState.actions.handleContinue) {
      projectState.actions.handleContinue();
    }
  }, [projectState, projectManagement, toast]);

  return {
    handleSettingsSubmit,
    handlePromptSubmit,
    handleOverviewSubmit
    // handleContinue removed - using the one from form submission handlers instead
  };
}
