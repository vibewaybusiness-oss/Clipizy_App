"use client";

import { useCallback, useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useLogger } from '../shared/logger';
import { NavigationStep } from './use-navigation-manager';

// =========================
// URL SYNCHRONIZATION TYPES
// =========================

export interface UrlSyncOptions {
  basePath: string;
  stepParam: string;
  projectParam: string;
  preserveOtherParams: boolean;
  scrollBehavior: 'smooth' | 'instant' | 'auto';
}

export interface UrlSyncState {
  currentStep: NavigationStep;
  currentProjectId: string | null;
  isUrlSyncing: boolean;
  lastSyncedStep: NavigationStep | null;
}

export interface UrlSyncActions {
  syncStepToUrl: (step: NavigationStep, projectId?: string | null) => Promise<void>;
  syncUrlToStep: () => NavigationStep | null;
  updateUrl: (updates: Record<string, string | null>) => void;
  getUrlParams: () => Record<string, string>;
  clearUrlParams: () => void;
}

// =========================
// DEFAULT OPTIONS
// =========================

const DEFAULT_OPTIONS: UrlSyncOptions = {
  basePath: '/dashboard/create/music-clip',
  stepParam: 'step',
  projectParam: 'projectId',
  preserveOtherParams: true,
  scrollBehavior: 'auto'
};

// =========================
// URL SYNCHRONIZATION HOOK
// =========================

export function useUrlSync(options: Partial<UrlSyncOptions> = {}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const logger = useLogger({ source: 'useUrlSync' });
  
  const config = { ...DEFAULT_OPTIONS, ...options };
  const isUrlSyncingRef = useRef(false);
  const lastSyncedStepRef = useRef<NavigationStep | null>(null);

  // =========================
  // URL PARSING
  // =========================

  const parseUrlParams = useCallback(() => {
    const params: Record<string, string> = {};
    
    for (const [key, value] of searchParams.entries()) {
      params[key] = value;
    }
    
    return params;
  }, [searchParams]);

  const getStepFromUrl = useCallback((): NavigationStep | null => {
    const stepParam = searchParams.get(config.stepParam);
    if (stepParam) {
      const step = parseInt(stepParam, 10);
      if (step >= 1 && step <= 4) {
        return step as NavigationStep;
      }
    }
    return null;
  }, [searchParams, config.stepParam]);

  const getProjectIdFromUrl = useCallback((): string | null => {
    return searchParams.get(config.projectParam);
  }, [searchParams, config.projectParam]);

  // =========================
  // URL UPDATING
  // =========================

  const updateUrl = useCallback((updates: Record<string, string | null>) => {
    if (isUrlSyncingRef.current) {
      logger.debug('URL update blocked - already syncing');
      return;
    }

    isUrlSyncingRef.current = true;
    
    try {
      const currentParams = parseUrlParams();
      const newParams = new URLSearchParams();
      
      // Preserve existing params if configured
      if (config.preserveOtherParams) {
        for (const [key, value] of Object.entries(currentParams)) {
          if (!updates.hasOwnProperty(key)) {
            newParams.set(key, value);
          }
        }
      }
      
      // Apply updates
      for (const [key, value] of Object.entries(updates)) {
        if (value !== null && value !== undefined) {
          newParams.set(key, value);
        } else {
          newParams.delete(key);
        }
      }
      
      const newUrl = `${config.basePath}?${newParams.toString()}`;
      
      logger.debug('Updating URL', { 
        updates, 
        newUrl, 
        preserveOtherParams: config.preserveOtherParams 
      });
      
      router.replace(newUrl, { scroll: false });
      
    } catch (error) {
      logger.error('URL update failed', { error, updates });
    } finally {
      isUrlSyncingRef.current = false;
    }
  }, [config, parseUrlParams, router, logger]);

  const syncStepToUrl = useCallback(async (
    step: NavigationStep, 
    projectId?: string | null
  ): Promise<void> => {
    logger.info('Syncing step to URL', { step, projectId });
    
    const updates: Record<string, string | null> = {
      [config.stepParam]: step.toString()
    };
    
    if (projectId !== undefined) {
      updates[config.projectParam] = projectId;
    }
    
    updateUrl(updates);
    lastSyncedStepRef.current = step;
  }, [config, updateUrl, logger]);

  const syncUrlToStep = useCallback((): NavigationStep | null => {
    const step = getStepFromUrl();
    logger.debug('Syncing URL to step', { step });
    return step;
  }, [getStepFromUrl, logger]);

  const getUrlParams = useCallback(() => {
    return parseUrlParams();
  }, [parseUrlParams]);

  const clearUrlParams = useCallback(() => {
    logger.info('Clearing URL parameters');
    router.replace(config.basePath, { scroll: false });
  }, [config.basePath, router, logger]);

  // =========================
  // BROWSER NAVIGATION HANDLING
  // =========================

  useEffect(() => {
    const handlePopState = () => {
      logger.debug('Browser navigation detected');
      
      // Small delay to allow URL to update
      setTimeout(() => {
        const step = getStepFromUrl();
        if (step && step !== lastSyncedStepRef.current) {
          logger.info('URL changed via browser navigation', { 
            from: lastSyncedStepRef.current, 
            to: step 
          });
          lastSyncedStepRef.current = step;
        }
      }, 10);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [getStepFromUrl, logger]);

  // =========================
  // URL VALIDATION
  // =========================

  const validateUrl = useCallback(() => {
    const step = getStepFromUrl();
    const projectId = getProjectIdFromUrl();
    
    const validation = {
      isValid: true,
      errors: [] as string[],
      warnings: [] as string[]
    };
    
    // Validate step
    if (step === null) {
      validation.warnings.push('No step parameter in URL');
    } else if (step < 1 || step > 4) {
      validation.isValid = false;
      validation.errors.push(`Invalid step parameter: ${step}`);
    }
    
    // Validate project ID format if present
    if (projectId && !/^[a-zA-Z0-9-_]+$/.test(projectId)) {
      validation.warnings.push('Project ID contains invalid characters');
    }
    
    if (validation.errors.length > 0 || validation.warnings.length > 0) {
      logger.debug('URL validation result', validation);
    }
    
    return validation;
  }, [getStepFromUrl, getProjectIdFromUrl, logger]);

  // =========================
  // URL STATE
  // =========================

  const urlSyncState: UrlSyncState = {
    currentStep: getStepFromUrl() || 1,
    currentProjectId: getProjectIdFromUrl(),
    isUrlSyncing: isUrlSyncingRef.current,
    lastSyncedStep: lastSyncedStepRef.current
  };

  const urlSyncActions: UrlSyncActions = {
    syncStepToUrl,
    syncUrlToStep,
    updateUrl,
    getUrlParams,
    clearUrlParams
  };

  // =========================
  // RETURN INTERFACE
  // =========================

  return {
    // State
    ...urlSyncState,
    
    // Actions
    ...urlSyncActions,
    
    // Utilities
    validateUrl,
    getStepFromUrl,
    getProjectIdFromUrl,
    
    // Configuration
    config
  };
}
