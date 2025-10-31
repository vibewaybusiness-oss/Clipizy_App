"use client";

import { useState, useCallback, useMemo, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useLogger } from '../shared/logger';

// =========================
// NAVIGATION TYPES
// =========================

export type ProjectState = 'draft' | 'processing' | 'completed' | 'failed' | 'archived';
export type NavigationStep = 1 | 2 | 3 | 4;
export type NavigationDirection = 'forward' | 'backward' | 'jump';

export interface NavigationState {
  currentStep: NavigationStep;
  maxReachedStep: NavigationStep;
  isNavigating: boolean;
  canNavigateForward: boolean;
  canNavigateBackward: boolean;
  availableSteps: NavigationStep[];
}

export interface NavigationActions {
  navigateToStep: (step: NavigationStep, direction?: NavigationDirection) => Promise<boolean>;
  navigateForward: () => Promise<boolean>;
  navigateBackward: () => Promise<boolean>;
  navigateToDashboard: () => Promise<boolean>;
  canNavigateToStep: (step: NavigationStep) => boolean;
  resetNavigation: () => void;
  setMaxReachedStep: (step: NavigationStep) => void;
}

export interface ProjectValidationContext {
  projectId: string | null;
  projectState: ProjectState | null;
  hasTracks: boolean;
  hasAnalysis: boolean;
  hasValidForm: boolean;
  isGenerating: boolean;
  userAuthenticated: boolean;
}

export interface NavigationConfig {
  step: NavigationStep;
  title: string;
  description: string;
  isOptional: boolean;
  canSkip: boolean;
  validation: (context: ProjectValidationContext) => {
    canAccess: boolean;
    canProceed: boolean;
    reason?: string;
  };
  onEnter?: (context: ProjectValidationContext) => void | Promise<void>;
  onExit?: (context: ProjectValidationContext) => void | Promise<void>;
  onValidate?: (context: ProjectValidationContext) => Promise<boolean>;
}

// =========================
// NAVIGATION CONFIGURATION
// =========================

export const NAVIGATION_CONFIG: Record<NavigationStep, NavigationConfig> = {
  1: {
    step: 1,
    title: 'Upload Music',
    description: 'Upload your music tracks or generate new ones',
    isOptional: false,
    canSkip: false,
    validation: (context) => {
      if (!context.userAuthenticated) {
        return { canAccess: false, canProceed: false, reason: 'User must be authenticated' };
      }
      if (context.projectState === 'processing') {
        return { canAccess: false, canProceed: false, reason: 'Project is currently processing' };
      }
      return { canAccess: true, canProceed: true };
    },
    onEnter: (context) => {
      console.log('Entering step 1: Upload Music');
    }
  },
  2: {
    step: 2,
    title: 'AI Blueprint',
    description: 'Review AI analysis and musical characteristics',
    isOptional: false,
    canSkip: false,
    validation: (context) => {
      if (!context.userAuthenticated) {
        return { canAccess: false, canProceed: false, reason: 'User must be authenticated' };
      }
      if (!context.hasTracks) {
        return { canAccess: false, canProceed: false, reason: 'No tracks available' };
      }
      if (context.projectState === 'processing') {
        return { canAccess: false, canProceed: false, reason: 'Project is currently processing' };
      }
      // Allow access to step 2 - analysis will be handled internally
      return { canAccess: true, canProceed: true };
    },
    onEnter: (context) => {
      console.log('Entering step 2: AI Blueprint - analysis will be triggered internally');
    }
  },
  3: {
    step: 3,
    title: 'Visual Story',
    description: 'Define your video concept and add reference images',
    isOptional: false,
    canSkip: false,
    validation: (context) => {
      if (!context.userAuthenticated) {
        return { canAccess: false, canProceed: false, reason: 'User must be authenticated' };
      }
      if (!context.hasTracks) {
        return { canAccess: false, canProceed: false, reason: 'No tracks available' };
      }
      if (!context.hasAnalysis) {
        return { canAccess: false, canProceed: false, reason: 'No analysis data available' };
      }
      if (context.projectState === 'processing') {
        return { canAccess: false, canProceed: false, reason: 'Project is currently processing' };
      }
      return { canAccess: true, canProceed: context.hasValidForm };
    },
    onEnter: (context) => {
      console.log('Entering step 3: Visual Story');
    }
  },
  4: {
    step: 4,
    title: 'Generate Video',
    description: 'Review settings and generate your music video',
    isOptional: false,
    canSkip: false,
    validation: (context) => {
      if (!context.userAuthenticated) {
        return { canAccess: false, canProceed: false, reason: 'User must be authenticated' };
      }
      if (!context.hasTracks) {
        return { canAccess: false, canProceed: false, reason: 'No tracks available' };
      }
      if (!context.hasAnalysis) {
        return { canAccess: false, canProceed: false, reason: 'No analysis data available' };
      }
      if (!context.hasValidForm) {
        return { canAccess: false, canProceed: false, reason: 'Form validation required' };
      }
      if (context.projectState === 'processing') {
        return { canAccess: true, canProceed: false, reason: 'Project is currently processing' };
      }
      if (context.isGenerating) {
        return { canAccess: true, canProceed: false, reason: 'Generation in progress' };
      }
      return { canAccess: true, canProceed: true };
    },
    onEnter: (context) => {
      console.log('Entering step 4: Generate Video');
    }
  }
};

// =========================
// NAVIGATION MANAGER HOOK
// =========================

export function useNavigationManager(
  initialStep: NavigationStep = 1,
  validationContext: ProjectValidationContext
) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const logger = useLogger({ 
    projectId: validationContext.projectId || 'unknown', 
    source: 'useNavigationManager' 
  });

  // =========================
  // STATE MANAGEMENT
  // =========================

  const [currentStep, setCurrentStep] = useState<NavigationStep>(initialStep);
  const [maxReachedStep, setMaxReachedStep] = useState<NavigationStep>(initialStep);
  const [isNavigating, setIsNavigating] = useState(false);
  const [navigationHistory, setNavigationHistory] = useState<NavigationStep[]>([initialStep]);

  // =========================
  // VALIDATION LOGIC
  // =========================

  const validateStep = useCallback((step: NavigationStep): { canAccess: boolean; canProceed: boolean; reason?: string } => {
    const config = NAVIGATION_CONFIG[step];
    if (!config) {
      return { canAccess: false, canProceed: false, reason: 'Invalid step' };
    }

    const validation = config.validation(validationContext);
    logger.debug('Step validation', { step, validation, context: validationContext });
    
    return validation;
  }, [validationContext, logger]);

  const canNavigateToStep = useCallback((step: NavigationStep): boolean => {
    const validation = validateStep(step);
    return validation.canAccess;
  }, [validateStep]);

  const canProceedFromStep = useCallback((step: NavigationStep): boolean => {
    const validation = validateStep(step);
    return validation.canProceed;
  }, [validateStep]);

  // =========================
  // NAVIGATION LOGIC
  // =========================

  const navigateToStep = useCallback(async (
    targetStep: NavigationStep, 
    direction: NavigationDirection = 'jump'
  ): Promise<boolean> => {
    logger.info('Navigation requested', { 
      from: currentStep, 
      to: targetStep, 
      direction 
    });

    // Prevent navigation if already navigating
    if (isNavigating) {
      logger.warn('Navigation blocked - already navigating');
      return false;
    }

    // Validate target step
    const validation = validateStep(targetStep);
    if (!validation.canAccess) {
      logger.warn('Navigation blocked - validation failed', { 
        step: targetStep, 
        reason: validation.reason 
      });
      return false;
    }

    // Check if navigation is allowed based on direction
    if (direction === 'forward' && targetStep > maxReachedStep) {
      logger.warn('Navigation blocked - cannot skip ahead', { 
        targetStep, 
        maxReachedStep 
      });
      return false;
    }

    setIsNavigating(true);

    try {
      // Execute step exit logic
      const currentConfig = NAVIGATION_CONFIG[currentStep];
      if (currentConfig?.onExit) {
        await currentConfig.onExit(validationContext);
      }

      // Execute step enter logic
      const targetConfig = NAVIGATION_CONFIG[targetStep];
      if (targetConfig?.onEnter) {
        await targetConfig.onEnter(validationContext);
      }

      // Update navigation state
      setCurrentStep(targetStep);
      
      if (targetStep > maxReachedStep) {
        setMaxReachedStep(targetStep);
      }

      // Update navigation history
      setNavigationHistory(prev => [...prev, targetStep]);

      // Update URL
      const params = new URLSearchParams(searchParams);
      params.set('step', targetStep.toString());
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      router.replace(newUrl, { scroll: false });

      logger.info('Navigation completed', { 
        from: currentStep, 
        to: targetStep, 
        direction 
      });

      return true;
    } catch (error) {
      logger.error('Navigation failed', { error, targetStep });
      return false;
    } finally {
      setIsNavigating(false);
    }
  }, [
    currentStep, 
    maxReachedStep, 
    isNavigating, 
    validateStep, 
    validationContext, 
    searchParams, 
    router, 
    logger
  ]);

  const navigateForward = useCallback(async (): Promise<boolean> => {
    const nextStep = Math.min(currentStep + 1, 4) as NavigationStep;
    return navigateToStep(nextStep, 'forward');
  }, [currentStep, navigateToStep]);

  const navigateBackward = useCallback(async (): Promise<boolean> => {
    const prevStep = Math.max(currentStep - 1, 1) as NavigationStep;
    return navigateToStep(prevStep, 'backward');
  }, [currentStep, navigateToStep]);

  const navigateToDashboard = useCallback(async (): Promise<boolean> => {
    logger.info('Navigating to dashboard create page');
    
    try {
      // Navigate to dashboard create page
      router.push('/dashboard/create');
      return true;
    } catch (error) {
      logger.error('Failed to navigate to dashboard', { error });
      return false;
    }
  }, [router, logger]);

  const resetNavigation = useCallback(() => {
    setCurrentStep(1);
    setMaxReachedStep(1);
    setIsNavigating(false);
    setNavigationHistory([1]);
    logger.info('Navigation reset');
  }, [logger]);

  // =========================
  // COMPUTED VALUES
  // =========================

  const navigationState: NavigationState = useMemo(() => {
    const availableSteps = (Object.keys(NAVIGATION_CONFIG) as NavigationStep[])
      .filter(step => canNavigateToStep(step));

    return {
      currentStep,
      maxReachedStep,
      isNavigating,
      canNavigateForward: canProceedFromStep(currentStep) && currentStep < 4,
      canNavigateBackward: currentStep > 1,
      availableSteps
    };
  }, [currentStep, maxReachedStep, isNavigating, canNavigateToStep, canProceedFromStep]);

  const navigationActions: NavigationActions = useMemo(() => ({
    navigateToStep,
    navigateForward,
    navigateBackward,
    navigateToDashboard,
    canNavigateToStep,
    resetNavigation,
    setMaxReachedStep
  }), [
    navigateToStep,
    navigateForward,
    navigateBackward,
    navigateToDashboard,
    canNavigateToStep,
    resetNavigation,
    setMaxReachedStep
  ]);

  // =========================
  // URL SYNCHRONIZATION
  // =========================

  useEffect(() => {
    const handlePopState = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const stepParam = urlParams.get('step');
      if (stepParam) {
        const step = parseInt(stepParam, 10) as NavigationStep;
        if (step !== currentStep && canNavigateToStep(step)) {
          logger.info('Browser navigation detected', { step });
          navigateToStep(step, 'jump');
        }
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [currentStep, canNavigateToStep, navigateToStep, logger]);

  // =========================
  // RETURN INTERFACE
  // =========================

  return {
    // State
    ...navigationState,
    
    // Actions
    ...navigationActions,
    
    // Validation
    validateStep,
    canProceedFromStep,
    
    // Configuration
    config: NAVIGATION_CONFIG,
    
    // History
    navigationHistory
  };
}
