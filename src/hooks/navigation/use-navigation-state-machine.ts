"use client";

import { useState, useCallback, useMemo, useRef } from 'react';
import { useLogger } from '../shared/logger';
import { NavigationStep, ProjectValidationContext } from './use-navigation-manager';

// =========================
// STATE MACHINE TYPES
// =========================

export type NavigationState = 
  | 'idle'
  | 'validating'
  | 'navigating'
  | 'blocked'
  | 'error'
  | 'redirecting';

export type NavigationEvent = 
  | 'navigate'
  | 'validate'
  | 'block'
  | 'allow'
  | 'error'
  | 'redirect'
  | 'reset'
  | 'complete';

export interface StateTransition {
  from: NavigationState;
  to: NavigationState;
  event: NavigationEvent;
  condition?: (context: any) => boolean;
  action?: (context: any) => void | Promise<void>;
}

export interface NavigationContext {
  currentStep: NavigationStep;
  targetStep: NavigationStep;
  projectContext: ProjectValidationContext;
  error?: string;
  redirectTo?: string;
  validationResult?: any;
}

// =========================
// STATE MACHINE CONFIGURATION
// =========================

const STATE_TRANSITIONS: StateTransition[] = [
  // From idle
  {
    from: 'idle',
    to: 'validating',
    event: 'navigate',
    action: (context) => {
      console.log('Starting navigation validation', context);
    }
  },
  {
    from: 'idle',
    to: 'error',
    event: 'error',
    action: (context) => {
      console.error('Navigation error from idle state', context);
    }
  },
  
  // From validating
  {
    from: 'validating',
    to: 'navigating',
    event: 'allow',
    action: (context) => {
      console.log('Navigation allowed, proceeding', context);
    }
  },
  {
    from: 'validating',
    to: 'blocked',
    event: 'block',
    action: (context) => {
      console.log('Navigation blocked', context);
    }
  },
  {
    from: 'validating',
    to: 'redirecting',
    event: 'redirect',
    action: (context) => {
      console.log('Redirecting navigation', context);
    }
  },
  {
    from: 'validating',
    to: 'error',
    event: 'error',
    action: (context) => {
      console.error('Validation error', context);
    }
  },
  
  // From navigating
  {
    from: 'navigating',
    to: 'idle',
    event: 'complete',
    action: (context) => {
      console.log('Navigation completed', context);
    }
  },
  {
    from: 'navigating',
    to: 'error',
    event: 'error',
    action: (context) => {
      console.error('Navigation failed', context);
    }
  },
  
  // From blocked
  {
    from: 'blocked',
    to: 'idle',
    event: 'reset',
    action: (context) => {
      console.log('Navigation reset from blocked state', context);
    }
  },
  
  // From redirecting
  {
    from: 'redirecting',
    to: 'idle',
    event: 'complete',
    action: (context) => {
      console.log('Redirect completed', context);
    }
  },
  
  // From error
  {
    from: 'error',
    to: 'idle',
    event: 'reset',
    action: (context) => {
      console.log('Navigation reset from error state', context);
    }
  },
  
  // Universal reset
  {
    from: 'validating',
    to: 'idle',
    event: 'reset'
  },
  {
    from: 'navigating',
    to: 'idle',
    event: 'reset'
  },
  {
    from: 'blocked',
    to: 'idle',
    event: 'reset'
  },
  {
    from: 'redirecting',
    to: 'idle',
    event: 'reset'
  }
];

// =========================
// STATE MACHINE HOOK
// =========================

export function useNavigationStateMachine() {
  const logger = useLogger({ source: 'useNavigationStateMachine' });
  
  const [currentState, setCurrentState] = useState<NavigationState>('idle');
  const [context, setContext] = useState<NavigationContext | null>(null);
  const [history, setHistory] = useState<{ state: NavigationState; timestamp: number; context?: NavigationContext }[]>([]);
  
  const stateRef = useRef<NavigationState>('idle');
  const contextRef = useRef<NavigationContext | null>(null);

  // =========================
  // STATE TRANSITION LOGIC
  // =========================

  const transition = useCallback(async (
    event: NavigationEvent,
    newContext?: Partial<NavigationContext>
  ): Promise<boolean> => {
    const currentStateValue = stateRef.current;
    const currentContextValue = contextRef.current;
    
    logger.debug('State machine transition', { 
      from: currentStateValue, 
      event, 
      newContext 
    });

    // Find valid transition
    const validTransition = STATE_TRANSITIONS.find(transition => 
      transition.from === currentStateValue && 
      transition.event === event &&
      (!transition.condition || transition.condition({ ...currentContextValue, ...newContext }))
    );

    if (!validTransition) {
      logger.warn('Invalid state transition', { 
        from: currentStateValue, 
        event, 
        availableTransitions: STATE_TRANSITIONS
          .filter(t => t.from === currentStateValue)
          .map(t => t.event)
      });
      return false;
    }

    // Update context
    const updatedContext = { ...currentContextValue, ...newContext };
    setContext(updatedContext);
    contextRef.current = updatedContext;

    // Execute transition action
    if (validTransition.action) {
      try {
        await validTransition.action(updatedContext);
      } catch (error) {
        logger.error('Transition action failed', { error, transition: validTransition });
        setCurrentState('error');
        stateRef.current = 'error';
        return false;
      }
    }

    // Update state
    setCurrentState(validTransition.to);
    stateRef.current = validTransition.to;

    // Update history
    setHistory(prev => [...prev, {
      state: validTransition.to,
      timestamp: Date.now(),
      context: updatedContext
    }]);

    logger.info('State transition completed', { 
      from: currentStateValue, 
      to: validTransition.to, 
      event 
    });

    return true;
  }, [logger]);

  // =========================
  // STATE QUERIES
  // =========================

  const canTransition = useCallback((event: NavigationEvent): boolean => {
    const currentStateValue = stateRef.current;
    return STATE_TRANSITIONS.some(transition => 
      transition.from === currentStateValue && 
      transition.event === event
    );
  }, []);

  const getAvailableEvents = useCallback((): NavigationEvent[] => {
    const currentStateValue = stateRef.current;
    return STATE_TRANSITIONS
      .filter(transition => transition.from === currentStateValue)
      .map(transition => transition.event);
  }, []);

  const isInState = useCallback((state: NavigationState): boolean => {
    return stateRef.current === state;
  }, []);

  // =========================
  // STATE ACTIONS
  // =========================

  const startNavigation = useCallback(async (
    targetStep: NavigationStep,
    projectContext: ProjectValidationContext
  ): Promise<boolean> => {
    logger.info('Starting navigation', { targetStep, projectContext });
    
    const success = await transition('navigate', {
      currentStep: projectContext.currentStep || 1,
      targetStep,
      projectContext
    });
    
    return success;
  }, [transition, logger]);

  const allowNavigation = useCallback(async (): Promise<boolean> => {
    logger.info('Allowing navigation');
    return await transition('allow');
  }, [transition, logger]);

  const blockNavigation = useCallback(async (reason?: string): Promise<boolean> => {
    logger.info('Blocking navigation', { reason });
    return await transition('block', { error: reason });
  }, [transition, logger]);

  const redirectNavigation = useCallback(async (redirectTo: string): Promise<boolean> => {
    logger.info('Redirecting navigation', { redirectTo });
    return await transition('redirect', { redirectTo });
  }, [transition, logger]);

  const completeNavigation = useCallback(async (): Promise<boolean> => {
    logger.info('Completing navigation');
    return await transition('complete');
  }, [transition, logger]);

  const errorNavigation = useCallback(async (error: string): Promise<boolean> => {
    logger.error('Navigation error', { error });
    return await transition('error', { error });
  }, [transition, logger]);

  const resetNavigation = useCallback(async (): Promise<boolean> => {
    logger.info('Resetting navigation');
    setContext(null);
    contextRef.current = null;
    setHistory([]);
    return await transition('reset');
  }, [transition, logger]);

  // =========================
  // STATE INFORMATION
  // =========================

  const stateInfo = useMemo(() => ({
    currentState,
    context,
    history: history.slice(-10), // Last 10 transitions
    canTransition,
    getAvailableEvents,
    isInState,
    
    // State flags
    isIdle: currentState === 'idle',
    isValidating: currentState === 'validating',
    isNavigating: currentState === 'navigating',
    isBlocked: currentState === 'blocked',
    isError: currentState === 'error',
    isRedirecting: currentState === 'redirecting',
    
    // Context information
    currentStep: context?.currentStep,
    targetStep: context?.targetStep,
    error: context?.error,
    redirectTo: context?.redirectTo,
    validationResult: context?.validationResult
  }), [
    currentState,
    context,
    history,
    canTransition,
    getAvailableEvents,
    isInState
  ]);

  // =========================
  // RETURN INTERFACE
  // =========================

  return {
    // State
    ...stateInfo,
    
    // Actions
    transition,
    startNavigation,
    allowNavigation,
    blockNavigation,
    redirectNavigation,
    completeNavigation,
    errorNavigation,
    resetNavigation,
    
    // Utilities
    getStateHistory: () => history,
    getLastTransition: () => history[history.length - 1],
    getTransitionCount: () => history.length
  };
}
