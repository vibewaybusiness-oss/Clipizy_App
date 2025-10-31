// =========================
// WORKFLOW SYSTEM EXPORTS
// =========================

// Workflow engine
export { useWorkflowEngine } from './WorkflowEngine';
export { useWorkflowHandlers, createWorkflowHandler } from './handlers';

// Types - export from local types first, then workflow types
export type { ProjectType, Message, WorkflowContext } from './types';
export type { 
  WorkflowConfig, 
  WorkflowStep, 
  WorkflowHelpers,
  ToastOptions,
  ActionButton
} from '@/types/workflow';

// Brick types - only export what's needed
export type {
  BrickInstance,
  BrickExecutionResult,
  BrickValidationRule,
  BrickValidationResult
} from '@/types/bricks';

// Re-export brick config types from workflow (where they're actually defined)
export type {
  BrickConfig,
  BrickContext,
  LLMBrickConfig,
  UserInputBrickConfig,
  APICallBrickConfig,
  BackgroundBrickConfig
} from '@/types/workflow';

// Workflow loader and utilities
export { workflowLoader } from './utils/workflowLoader';
export { brickFactoryUtils } from './utils/brickFactory';
export { workflowMigrator } from './utils/WorkflowMigrator';

// Brick system - specific exports to avoid conflicts
export { 
  brickFactory, 
  brickRegistry, 
  brickValidator, 
  brickErrorHandler,
  brickEventEmitter 
} from './bricks';

// UI Components
export { WorkflowUI } from './WorkflowUI';