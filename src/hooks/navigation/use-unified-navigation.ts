"use client";

import { useCallback, useMemo, useEffect } from 'react';
import { useLogger } from '../shared/logger';
import { 
  useNavigationManager, 
  NavigationStep, 
  ProjectValidationContext 
} from './use-navigation-manager';
import { useNavigationGuards } from './use-navigation-guards';
import { useUrlSync } from './use-url-sync';
import { useNavigationStateMachine } from './use-navigation-state-machine';

// =========================
// UNIFIED NAVIGATION TYPES
// =========================

export interface UnifiedNavigationState {
  // Navigation state
  currentStep: NavigationStep;
  maxReachedStep: NavigationStep;
  isNavigating: boolean;
  
  // URL state
  currentProjectId: string | null;
  isUrlSyncing: boolean;
  
  // State machine state
  navigationState: 'idle' | 'validating' | 'navigating' | 'blocked' | 'error' | 'redirecting';
  
  // Validation state
  canNavigateForward: boolean;
  canNavigateBackward: boolean;
  availableSteps: NavigationStep[];
  
  // Error state
  error?: string;
  redirectTo?: string;
}

export interface UnifiedNavigationActions {
  // Navigation actions
  navigateToStep: (step: NavigationStep) => Promise<boolean>;
  navigateForward: () => Promise<boolean>;
  navigateBackward: () => Promise<boolean>;
  navigateToDashboard: () => Promise<boolean>;
  resetNavigation: () => Promise<boolean>;
  
  // URL actions
  syncStepToUrl: (step: NavigationStep, projectId?: string | null) => Promise<void>;
  updateUrl: (updates: Record<string, string | null>) => void;
  
  // State machine actions
  startNavigation: (targetStep: NavigationStep) => Promise<boolean>;
  allowNavigation: () => Promise<boolean>;
  blockNavigation: (reason?: string) => Promise<boolean>;
  redirectNavigation: (redirectTo: string) => Promise<boolean>;
  completeNavigation: () => Promise<boolean>;
  errorNavigation: (error: string) => Promise<boolean>;
}

export interface UnifiedNavigationOptions {
  initialStep?: NavigationStep;
  validationContext: ProjectValidationContext;
  urlSyncOptions?: {
    basePath?: string;
    stepParam?: string;
    projectParam?: string;
    preserveOtherParams?: boolean;
  };
}

// =========================
// UNIFIED NAVIGATION HOOK
// =========================

export function useUnifiedNavigation(options: UnifiedNavigationOptions) {
  const logger = useLogger({ 
    projectId: options.validationContext.projectId || 'unknown', 
    source: 'useUnifiedNavigation' 
  });

  const { initialStep = 1, validationContext, urlSyncOptions = {} } = options;

  // =========================
  // COMPONENT HOOKS
  // =========================

  const navigationManager = useNavigationManager(initialStep, validationContext);
  const navigationGuards = useNavigationGuards(validationContext, navigationManager.currentStep);
  const urlSync = useUrlSync(urlSyncOptions);
  const stateMachine = useNavigationStateMachine();

  // =========================
  // UNIFIED NAVIGATION LOGIC
  // =========================

  const navigateToStep = useCallback(async (step: NavigationStep): Promise<boolean> => {
    logger.info('Unified navigation to step', { 
      from: navigationManager.currentStep, 
      to: step 
    });

    try {
      // Start state machine
      const started = await stateMachine.startNavigation(step, validationContext);
      if (!started) {
        logger.warn('Failed to start navigation state machine');
        return false;
      }

      // Validate navigation with guards
      const canNavigate = await navigationGuards.validateNavigation(step);
      if (!canNavigate) {
        await stateMachine.blockNavigation('Navigation blocked by guards');
        return false;
      }

      // Allow navigation in state machine
      const allowed = await stateMachine.allowNavigation();
      if (!allowed) {
        logger.warn('State machine blocked navigation');
        return false;
      }

      // Perform navigation
      const navigationSuccess = await navigationManager.navigateToStep(step);
      if (!navigationSuccess) {
        await stateMachine.errorNavigation('Navigation manager failed');
        return false;
      }

      // Sync URL
      await urlSync.syncStepToUrl(step, validationContext.projectId);

      // Complete navigation
      const completed = await stateMachine.completeNavigation();
      if (!completed) {
        logger.warn('Failed to complete navigation in state machine');
      }

      logger.info('Unified navigation completed', { step });
      return true;

    } catch (error) {
      logger.error('Unified navigation failed', { error, step });
      await stateMachine.errorNavigation(error instanceof Error ? error.message : 'Unknown error');
      return false;
    }
  }, [
    navigationManager,
    navigationGuards,
    urlSync,
    stateMachine,
    validationContext,
    logger
  ]);

  const navigateForward = useCallback(async (): Promise<boolean> => {
    const nextStep = Math.min(navigationManager.currentStep + 1, 4) as NavigationStep;
    return navigateToStep(nextStep);
  }, [navigateToStep, navigationManager.currentStep]);

  const navigateBackward = useCallback(async (): Promise<boolean> => {
    const prevStep = Math.max(navigationManager.currentStep - 1, 1) as NavigationStep;
    return navigateToStep(prevStep);
  }, [navigateToStep, navigationManager.currentStep]);

  const resetNavigation = useCallback(async (): Promise<boolean> => {
    logger.info('Resetting unified navigation');
    
    try {
      // Reset all components
      navigationManager.resetNavigation();
      await stateMachine.resetNavigation();
      urlSync.clearUrlParams();
      
      logger.info('Unified navigation reset completed');
      return true;
    } catch (error) {
      logger.error('Failed to reset unified navigation', { error });
      return false;
    }
  }, [navigationManager, stateMachine, urlSync, logger]);

  // =========================
  // UNIFIED STATE
  // =========================

  const unifiedState: UnifiedNavigationState = useMemo(() => ({
    // Navigation state
    currentStep: navigationManager.currentStep,
    maxReachedStep: navigationManager.maxReachedStep,
    isNavigating: navigationManager.isNavigating,
    
    // URL state
    currentProjectId: urlSync.currentProjectId,
    isUrlSyncing: urlSync.isUrlSyncing,
    
    // State machine state
    navigationState: stateMachine.currentState,
    
    // Validation state
    canNavigateForward: navigationManager.canNavigateForward,
    canNavigateBackward: navigationManager.canNavigateBackward,
    availableSteps: navigationManager.availableSteps,
    
    // Error state
    error: stateMachine.error,
    redirectTo: stateMachine.redirectTo
  }), [
    navigationManager,
    urlSync,
    stateMachine
  ]);

  const unifiedActions: UnifiedNavigationActions = useMemo(() => ({
    // Navigation actions
    navigateToStep,
    navigateForward,
    navigateBackward,
    navigateToDashboard: navigationManager.navigateToDashboard,
    resetNavigation,
    
    // URL actions
    syncStepToUrl: urlSync.syncStepToUrl,
    updateUrl: urlSync.updateUrl,
    
    // State machine actions
    startNavigation: stateMachine.startNavigation,
    allowNavigation: stateMachine.allowNavigation,
    blockNavigation: stateMachine.blockNavigation,
    redirectNavigation: stateMachine.redirectNavigation,
    completeNavigation: stateMachine.completeNavigation,
    errorNavigation: stateMachine.errorNavigation
  }), [
    navigateToStep,
    navigateForward,
    navigateBackward,
    navigationManager,
    resetNavigation,
    urlSync,
    stateMachine
  ]);

  // =========================
  // URL SYNCHRONIZATION
  // =========================

  useEffect(() => {
    const urlStep = urlSync.getStepFromUrl();
    if (urlStep && urlStep !== navigationManager.currentStep) {
      logger.info('URL step differs from navigation state, syncing', {
        urlStep,
        currentStep: navigationManager.currentStep
      });
      
      // Navigate to URL step if valid
      if (navigationManager.canNavigateToStep(urlStep)) {
        navigateToStep(urlStep);
      }
    }
  }, [urlSync, navigationManager, navigateToStep, logger]);

  // =========================
  // VALIDATION EFFECTS
  // =========================

  useEffect(() => {
    // Update navigation state when validation context changes
    const currentStep = navigationManager.currentStep;
    const canProceed = navigationManager.canProceedFromStep(currentStep);
    
    if (!canProceed && navigationManager.isNavigating) {
      logger.warn('Current step validation failed, blocking navigation', {
        currentStep,
        context: validationContext
      });
      
      stateMachine.blockNavigation('Current step validation failed');
    }
  }, [validationContext, navigationManager, stateMachine, logger]);

  // =========================
  // RETURN INTERFACE
  // =========================

  return {
    // Unified state
    ...unifiedState,
    
    // Unified actions
    ...unifiedActions,
    
    // Component access (for advanced usage)
    navigationManager,
    navigationGuards,
    urlSync,
    stateMachine,
    
    // Utilities
    validateStep: navigationManager.validateStep,
    canNavigateToStep: navigationManager.canNavigateToStep,
    getGuardStatus: navigationGuards.getGuardStatus,
    getUrlParams: urlSync.getUrlParams,
    getStateHistory: stateMachine.getStateHistory,
    
    // Configuration
    config: navigationManager.config,
    guardStatus: navigationGuards.guardStatus,
    urlConfig: urlSync.config
  };
}
