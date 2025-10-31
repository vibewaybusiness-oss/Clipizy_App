"use client";

import { useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/hooks/ui/use-toast';
import { useLogger } from '../shared/logger';
import { 
  ProjectState, 
  NavigationStep, 
  ProjectValidationContext,
  NAVIGATION_CONFIG 
} from './use-navigation-manager';

// =========================
// NAVIGATION GUARD TYPES
// =========================

export interface NavigationGuard {
  id: string;
  name: string;
  description: string;
  priority: number;
  condition: (context: ProjectValidationContext) => boolean;
  action: (context: ProjectValidationContext) => Promise<boolean>;
  message?: string;
  redirectTo?: string;
}

export interface GuardResult {
  canProceed: boolean;
  blockedBy: string[];
  redirectTo?: string;
  message?: string;
}

// =========================
// PROJECT STATE GUARDS
// =========================

export const PROJECT_STATE_GUARDS: NavigationGuard[] = [
  {
    id: 'auth-required',
    name: 'Authentication Required',
    description: 'User must be authenticated to access navigation',
    priority: 1,
    condition: (context) => !context.userAuthenticated,
    action: async (context) => {
      // Redirect to login
      return false;
    },
    message: 'You must be logged in to access this page.',
    redirectTo: '/auth/login'
  },
  {
    id: 'project-processing',
    name: 'Project Processing',
    description: 'Block navigation when project is processing',
    priority: 2,
    condition: (context) => context.projectState === 'processing',
    action: async (context) => {
      // Allow access to current step but prevent navigation
      return false;
    },
    message: 'Your project is currently being processed. Please wait for completion.',
    redirectTo: '/dashboard/create/generation-overview'
  },
  {
    id: 'project-completed',
    name: 'Project Completed',
    description: 'Redirect completed projects to overview',
    priority: 3,
    condition: (context) => context.projectState === 'completed',
    action: async (context) => {
      // Redirect to project overview
      return false;
    },
    message: 'Your project has been completed.',
    redirectTo: '/dashboard/create/generation-overview'
  },
  {
    id: 'project-failed',
    name: 'Project Failed',
    description: 'Handle failed projects',
    priority: 4,
    condition: (context) => context.projectState === 'failed',
    action: async (context) => {
      // Allow access to retry or start over
      return true;
    },
    message: 'Your project failed to process. You can retry or start over.'
  },
  {
    id: 'project-archived',
    name: 'Project Archived',
    description: 'Block access to archived projects',
    priority: 5,
    condition: (context) => context.projectState === 'archived',
    action: async (context) => {
      // Redirect to projects list
      return false;
    },
    message: 'This project has been archived and is no longer accessible.',
    redirectTo: '/dashboard/projects'
  }
];

// =========================
// STEP-SPECIFIC GUARDS
// =========================

export const STEP_SPECIFIC_GUARDS: Record<NavigationStep, NavigationGuard[]> = {
  1: [
    {
      id: 'step1-tracks-required',
      name: 'Tracks Required',
      description: 'Step 1 requires tracks to be uploaded or generated',
      priority: 1,
      condition: (context) => !context.hasTracks,
      action: async (context) => {
        // Allow access to step 1 to upload tracks
        return true;
      }
    }
  ],
  2: [
    {
      id: 'step2-tracks-required',
      name: 'Tracks Required for Analysis',
      description: 'Step 2 requires tracks to be available',
      priority: 1,
      condition: (context) => !context.hasTracks,
      action: async (context) => {
        // Redirect to step 1
        return false;
      },
      message: 'Please upload or generate music tracks first.',
      redirectTo: '?step=1'
    }
    // Analysis validation removed - step 2 will handle analysis internally
  ],
  3: [
    {
      id: 'step3-analysis-required',
      name: 'Analysis Required for Visual Story',
      description: 'Step 3 requires completed music analysis',
      priority: 1,
      condition: (context) => !context.hasAnalysis,
      action: async (context) => {
        // Redirect to step 2
        return false;
      },
      message: 'Please complete the music analysis first.',
      redirectTo: '?step=2'
    },
    {
      id: 'step3-form-validation',
      name: 'Form Validation Required',
      description: 'Step 3 requires valid form data',
      priority: 2,
      condition: (context) => !context.hasValidForm,
      action: async (context) => {
        // Allow access to fill out form
        return true;
      },
      message: 'Please complete the form before proceeding.'
    }
  ],
  4: [
    {
      id: 'step4-all-requirements',
      name: 'All Requirements Met',
      description: 'Step 4 requires all previous steps to be completed',
      priority: 1,
      condition: (context) => !context.hasTracks || !context.hasAnalysis || !context.hasValidForm,
      action: async (context) => {
        // Redirect to appropriate step
        if (!context.hasTracks) return false;
        if (!context.hasAnalysis) return false;
        if (!context.hasValidForm) return false;
        return true;
      },
      message: 'Please complete all previous steps before generating the video.',
      redirectTo: '?step=1'
    },
    {
      id: 'step4-generation-in-progress',
      name: 'Generation In Progress',
      description: 'Block navigation when generation is in progress',
      priority: 2,
      condition: (context) => context.isGenerating,
      action: async (context) => {
        // Allow access to step 4 but prevent new generation
        return true;
      },
      message: 'Video generation is already in progress.'
    }
  ]
};

// =========================
// NAVIGATION GUARDS HOOK
// =========================

export function useNavigationGuards(
  validationContext: ProjectValidationContext,
  currentStep: NavigationStep
) {
  const router = useRouter();
  const { toast } = useToast();
  const logger = useLogger({ 
    projectId: validationContext.projectId || 'unknown', 
    source: 'useNavigationGuards' 
  });

  // =========================
  // GUARD EVALUATION
  // =========================

  const evaluateGuards = useCallback(async (step: NavigationStep): Promise<GuardResult> => {
    logger.debug('Evaluating guards for step', { step, context: validationContext });

    const allGuards = [
      ...PROJECT_STATE_GUARDS,
      ...STEP_SPECIFIC_GUARDS[step]
    ].sort((a, b) => a.priority - b.priority);

    const blockedBy: string[] = [];
    let redirectTo: string | undefined;
    let message: string | undefined;

    for (const guard of allGuards) {
      if (guard.condition(validationContext)) {
        logger.debug('Guard triggered', { guard: guard.id, step });
        
        const canProceed = await guard.action(validationContext);
        
        if (!canProceed) {
          blockedBy.push(guard.id);
          
          if (guard.message) {
            message = guard.message;
          }
          
          if (guard.redirectTo) {
            redirectTo = guard.redirectTo;
          }
          
          // Stop evaluation on first blocking guard
          break;
        }
      }
    }

    const result: GuardResult = {
      canProceed: blockedBy.length === 0,
      blockedBy,
      redirectTo,
      message
    };

    logger.debug('Guard evaluation result', { step, result });
    return result;
  }, [validationContext, logger]);

  // =========================
  // NAVIGATION VALIDATION
  // =========================

  const validateNavigation = useCallback(async (targetStep: NavigationStep): Promise<boolean> => {
    logger.info('Validating navigation', { from: currentStep, to: targetStep });

    // Check if target step is accessible
    const stepConfig = NAVIGATION_CONFIG[targetStep];
    if (!stepConfig) {
      logger.warn('Invalid step configuration', { targetStep });
      toast({
        variant: "destructive",
        title: "Invalid Step",
        description: "The requested step is not valid.",
      });
      return false;
    }

    // Evaluate guards
    const guardResult = await evaluateGuards(targetStep);
    
    if (!guardResult.canProceed) {
      logger.warn('Navigation blocked by guards', { 
        targetStep, 
        blockedBy: guardResult.blockedBy 
      });

      // Show appropriate message
      if (guardResult.message) {
        toast({
          variant: "destructive",
          title: "Navigation Blocked",
          description: guardResult.message,
        });
      }

      // Handle redirect
      if (guardResult.redirectTo) {
        if (guardResult.redirectTo.startsWith('http') || guardResult.redirectTo.startsWith('/')) {
          router.push(guardResult.redirectTo);
        } else {
          // Relative redirect within current page
          const currentUrl = new URL(window.location.href);
          currentUrl.search = guardResult.redirectTo;
          router.replace(currentUrl.pathname + currentUrl.search);
        }
      }

      return false;
    }

    logger.info('Navigation validation passed', { targetStep });
    return true;
  }, [currentStep, evaluateGuards, toast, router, logger]);

  // =========================
  // GUARD STATUS
  // =========================

  const getGuardStatus = useCallback(async (step: NavigationStep) => {
    const guardResult = await evaluateGuards(step);
    return {
      step,
      canAccess: guardResult.canProceed,
      blockedBy: guardResult.blockedBy,
      message: guardResult.message,
      redirectTo: guardResult.redirectTo
    };
  }, [evaluateGuards]);

  // =========================
  // COMPUTED VALUES
  // =========================

  const guardStatus = useMemo(() => {
    return {
      currentStep: {
        canAccess: true, // Current step is always accessible
        blockedBy: [],
        message: undefined,
        redirectTo: undefined
      },
      nextStep: currentStep < 4 ? {
        step: (currentStep + 1) as NavigationStep,
        canAccess: false, // Will be evaluated when needed
        blockedBy: [],
        message: undefined,
        redirectTo: undefined
      } : null,
      previousStep: currentStep > 1 ? {
        step: (currentStep - 1) as NavigationStep,
        canAccess: true, // Previous steps are always accessible
        blockedBy: [],
        message: undefined,
        redirectTo: undefined
      } : null
    };
  }, [currentStep]);

  // =========================
  // RETURN INTERFACE
  // =========================

  return {
    // Validation
    validateNavigation,
    evaluateGuards,
    getGuardStatus,
    
    // Status
    guardStatus,
    
    // Guards
    projectStateGuards: PROJECT_STATE_GUARDS,
    stepSpecificGuards: STEP_SPECIFIC_GUARDS,
    
    // Utilities
    isStepAccessible: (step: NavigationStep) => {
      const guards = [...PROJECT_STATE_GUARDS, ...STEP_SPECIFIC_GUARDS[step]];
      return guards.every(guard => !guard.condition(validationContext));
    }
  };
}
