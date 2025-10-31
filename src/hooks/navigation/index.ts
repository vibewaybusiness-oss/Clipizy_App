// =========================
// NAVIGATION SYSTEM EXPORTS
// =========================

// Core navigation components
export { useNavigationManager } from './use-navigation-manager';
export { useNavigationGuards } from './use-navigation-guards';
export { useUrlSync } from './use-url-sync';
export { useNavigationStateMachine } from './use-navigation-state-machine';
export { useUnifiedNavigation } from './use-unified-navigation';
export { useProjectNavigation } from './use-project-navigation';

// Types
export type {
  NavigationStep,
  ProjectState,
  NavigationDirection,
  NavigationState as NavigationStateType,
  NavigationActions,
  ProjectValidationContext,
  NavigationConfig
} from './use-navigation-manager';

export type {
  NavigationGuard,
  GuardResult
} from './use-navigation-guards';

export type {
  UrlSyncOptions,
  UrlSyncState,
  UrlSyncActions
} from './use-url-sync';

export type {
  NavigationState,
  NavigationEvent,
  StateTransition,
  NavigationContext
} from './use-navigation-state-machine';

export type {
  UnifiedNavigationState,
  UnifiedNavigationActions,
  UnifiedNavigationOptions
} from './use-unified-navigation';

export type {
  ProjectNavigationOptions,
  ProjectNavigationActions
} from './use-project-navigation';

// Configuration
export { NAVIGATION_CONFIG } from './use-navigation-manager';
export { PROJECT_STATE_GUARDS, STEP_SPECIFIC_GUARDS } from './use-navigation-guards';
