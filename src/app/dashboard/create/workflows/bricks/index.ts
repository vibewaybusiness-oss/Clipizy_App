// =========================
// BRICK SYSTEM EXPORTS
// =========================

// Core brick system
export { BrickFactory, brickFactory } from './BrickFactory';
export { BrickRegistry, brickRegistry } from './BrickRegistry';
export { BrickUtils } from './BrickUtils';
export { BrickErrorHandler, brickErrorHandler } from './BrickError';
export { BrickEventEmitter, brickEventEmitter, ScopedBrickEventEmitter } from './BrickEventEmitter';
export { BrickValidator, brickValidator } from './BrickValidation';

// Brick implementations
export { LLMBrick, LLMBrickComponent } from './LLMBrick';
export { UserInputBrick, UserInputBrickComponent } from './UserInputBrick';
export { APICallBrick, APICallBrickComponent } from './APICallBrick';
export { BackgroundBrick, BackgroundBrickComponent } from './BackgroundBrick';

// Utility functions
export {
  createValidationError,
  createExecutionError,
  createGenericError,
  handleBrickError
} from './BrickError';

export {
  validateRequired,
  validateLength,
  validateRange,
  validateEmail,
  validateUrl,
  validateFileType,
  validateFileSize
} from './BrickValidation';

// Re-export types for convenience (only export types, not classes)
export type {
  BrickConfig,
  BrickContext,
  BrickInstance,
  BrickExecutionResult,
  BrickCreator,
  BrickValidationRule,
  BrickValidationResult,
  LLMBrickConfig,
  LLMBrickState,
  LLMBrickActions,
  UserInputBrickConfig,
  UserInputBrickState,
  UserInputBrickActions,
  APICallBrickConfig,
  APICallBrickState,
  APICallBrickActions,
  BackgroundBrickConfig,
  BackgroundBrickState,
  BackgroundBrickActions,
  BrickError,
  BrickValidationError,
  BrickExecutionError
} from '@/types/bricks';
export type { BrickRegistryEntry } from './BrickRegistry';
export type { BrickEventCallback, BrickEventSubscription } from './BrickEventEmitter';
