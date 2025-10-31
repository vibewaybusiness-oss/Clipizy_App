"use client";

import { useCallback, useMemo } from 'react';
import { useUnifiedNavigation, UnifiedNavigationOptions } from './use-unified-navigation';
import { useLogger } from '../shared/logger';
import { NavigationStep } from './use-navigation-manager';

// =========================
// PROJECT NAVIGATION TYPES
// =========================

export interface ProjectNavigationOptions extends UnifiedNavigationOptions {
  dashboardPath?: string;
  onBackToDashboard?: () => void;
}

export interface ProjectNavigationActions {
  // Standard navigation
  navigateToStep: (step: NavigationStep) => Promise<boolean>;
  navigateForward: () => Promise<boolean>;
  navigateBackward: () => Promise<boolean>;
  resetNavigation: () => Promise<boolean>;
  
  // Project-specific navigation
  handleBackNavigation: () => Promise<boolean>;
  navigateToDashboard: () => Promise<boolean>;
  
  // URL actions
  syncStepToUrl: (step: NavigationStep, projectId?: string | null) => Promise<void>;
  updateUrl: (updates: Record<string, string | null>) => void;
}

// =========================
// PROJECT NAVIGATION HOOK
// =========================

export function useProjectNavigation(options: ProjectNavigationOptions) {
  const logger = useLogger({ 
    projectId: options.validationContext.projectId || 'unknown', 
    source: 'useProjectNavigation' 
  });

  const { dashboardPath = '/dashboard/create', onBackToDashboard } = options;

  // =========================
  // UNIFIED NAVIGATION
  // =========================

  const navigation = useUnifiedNavigation(options);

  // =========================
  // PROJECT-SPECIFIC NAVIGATION LOGIC
  // =========================

  const handleBackNavigation = useCallback(async (): Promise<boolean> => {
    logger.info('Handling back navigation', { 
      currentStep: navigation.currentStep,
      hasTracks: options.validationContext.hasTracks 
    });

    // If on step 1, navigate to dashboard
    if (navigation.currentStep === 1) {
      logger.info('On step 1, navigating to dashboard');
      return await navigateToDashboard();
    }

    // If on any other step, navigate to previous step
    logger.info('Not on step 1, navigating to previous step');
    return await navigation.navigateBackward();
  }, [navigation, options.validationContext.hasTracks, logger]);

  const navigateToDashboard = useCallback(async (): Promise<boolean> => {
    logger.info('Navigating to dashboard', { dashboardPath });
    
    try {
      // Call custom handler if provided
      if (onBackToDashboard) {
        onBackToDashboard();
        return true;
      }
      
      // Use unified navigation dashboard method
      return await navigation.navigateToDashboard();
    } catch (error) {
      logger.error('Failed to navigate to dashboard', { error });
      return false;
    }
  }, [dashboardPath, onBackToDashboard, navigation, logger]);

  // =========================
  // NAVIGATION STATE
  // =========================

  const navigationState = useMemo(() => ({
    // Current navigation state
    currentStep: navigation.currentStep,
    maxReachedStep: navigation.maxReachedStep,
    isNavigating: navigation.isNavigating,
    
    // Back navigation logic
    shouldGoToDashboard: navigation.currentStep === 1,
    shouldGoToPreviousStep: navigation.currentStep > 1,
    
    // Navigation capabilities
    canNavigateForward: navigation.canNavigateForward,
    canNavigateBackward: navigation.canNavigateBackward,
    availableSteps: navigation.availableSteps,
    
    // Error state
    error: navigation.error,
    redirectTo: navigation.redirectTo
  }), [navigation]);

  // =========================
  // PROJECT NAVIGATION ACTIONS
  // =========================

  const projectNavigationActions: ProjectNavigationActions = useMemo(() => ({
    // Standard navigation
    navigateToStep: navigation.navigateToStep,
    navigateForward: navigation.navigateForward,
    navigateBackward: navigation.navigateBackward,
    resetNavigation: navigation.resetNavigation,
    
    // Project-specific navigation
    handleBackNavigation,
    navigateToDashboard,
    
    // URL actions
    syncStepToUrl: navigation.syncStepToUrl,
    updateUrl: navigation.updateUrl
  }), [
    navigation,
    handleBackNavigation,
    navigateToDashboard
  ]);

  // =========================
  // RETURN INTERFACE
  // =========================

  return {
    // State
    ...navigationState,
    
    // Actions
    ...projectNavigationActions,
    
    // Component access (for advanced usage)
    navigation,
    
    // Utilities
    validateStep: navigation.validateStep,
    canNavigateToStep: navigation.canNavigateToStep,
    getGuardStatus: navigation.getGuardStatus,
    getUrlParams: navigation.getUrlParams,
    getStateHistory: navigation.getStateHistory,
    
    // Configuration
    config: navigation.config,
    guardStatus: navigation.guardStatus,
    urlConfig: navigation.urlConfig
  };
}
