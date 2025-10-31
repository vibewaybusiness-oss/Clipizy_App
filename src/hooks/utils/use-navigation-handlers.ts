"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";

interface UseNavigationHandlersProps {
  projectState: any; // Generic project state (musicClipState, longFormState, etc.)
  projectManagement: any;
  projectData: any; // Generic project data (musicTracks, longFormData, etc.)
  resetProjectData?: () => void; // Optional custom reset function
  onStepChange?: (step: number) => void; // Optional step change handler
}

export function useNavigationHandlers({
  projectState,
  projectManagement,
  projectData,
  resetProjectData,
  onStepChange
}: UseNavigationHandlersProps) {
  const router = useRouter();

  const handleBack = useCallback(async (e?: React.MouseEvent) => {
    console.log('🔄 handleBack called:', { 
      e, 
      currentStep: projectState?.state?.currentStep,
      stack: new Error().stack 
    });
    
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    const currentStep = projectState?.state?.currentStep || 1;
    
    // Save data before navigating if we have a project ID and save function
    if (projectManagement?.state?.currentProjectId && projectState?.actions?.saveToUnifiedStorage) {
      try {
        console.log('💾 Saving data before back navigation...');
        await projectState.actions.saveToUnifiedStorage(projectManagement.state.currentProjectId, projectData);
        console.log('✅ Data saved successfully before back navigation');
      } catch (error) {
        console.error('❌ Failed to save data before back navigation:', error);
        // Continue with navigation even if save fails
      }
    }
    
    if (currentStep > 1) {
      // Navigate to previous step
      const previousStep = currentStep - 1;
      console.log('🔄 handleBack: Navigating to previous step', { from: currentStep, to: previousStep });
      
      if (onStepChange) {
        onStepChange(previousStep);
      } else if (projectState?.actions?.setCurrentStep) {
        projectState.actions.setCurrentStep(previousStep);
      }
    } else {
      // Navigate back to dashboard create page
      console.log('🔄 handleBack: Navigating back to dashboard create page');
      router.replace('/dashboard/create');
    }
  }, [router, projectState, projectManagement, projectData, onStepChange]);

  return {
    handleBack
  };
}
