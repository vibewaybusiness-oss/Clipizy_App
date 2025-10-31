// =========================
// BRICK SYSTEM TYPES
// =========================

import { BrickConfig, BrickContext, BrickProps } from './workflow';

// Re-export core types for convenience
export type { BrickConfig, BrickContext, BrickProps } from './workflow';
export type { 
  LLMBrickConfig, 
  UserInputBrickConfig, 
  APICallBrickConfig, 
  BackgroundBrickConfig 
} from './workflow';
export type {
  LLMBrickState,
  LLMBrickActions,
  UserInputBrickState,
  UserInputBrickActions,
  APICallBrickState,
  APICallBrickActions,
  BackgroundBrickState,
  BackgroundBrickActions
} from './workflow';

// =========================
// BRICK FACTORY TYPES
// =========================

export interface BrickFactory {
  createBrick: (config: BrickConfig, context: BrickContext) => BrickInstance;
  getSupportedTypes: () => string[];
  registerBrickType: (type: string, creator: BrickCreator) => void;
}

export interface BrickCreator {
  (config: BrickConfig, context: BrickContext): BrickInstance;
}

export interface BrickInstance {
  id: string;
  type: string;
  config: BrickConfig;
  context: BrickContext;
  execute: () => Promise<BrickExecutionResult>;
  validate: () => boolean | string;
  reset: () => void;
  destroy: () => void;
}

export interface BrickExecutionResult {
  success: boolean;
  data?: any;
  error?: Error;
  nextStep?: string;
  message?: string;
}

// =========================
// BRICK COMPONENT TYPES
// =========================

export interface BrickComponentProps<T = any> extends BrickProps<T> {
  className?: string;
  style?: React.CSSProperties;
  disabled?: boolean;
  loading?: boolean;
}

export interface BrickComponent<T = any> extends React.Component<BrickComponentProps<T>> {
  focus: () => void;
  blur: () => void;
  getValue: () => T;
  setValue: (value: T) => void;
  validate: () => boolean | string;
  reset: () => void;
}

// =========================
// LLM BRICK TYPES
// =========================

export interface LLMBrickState {
  prompt: string;
  isEditing: boolean;
  selectedButton?: string;
  files: File[];
}

export interface LLMBrickActions {
  setPrompt: (prompt: string) => void;
  startEditing: () => void;
  stopEditing: () => void;
  confirmEdit: () => void;
  cancelEdit: () => void;
  selectButton: (buttonId: string) => void;
  addFiles: (files: File[]) => void;
  removeFile: (index: number) => void;
  clearFiles: () => void;
}

// =========================
// USER INPUT BRICK TYPES
// =========================

export interface UserInputBrickState<T = any> {
  value: T;
  error?: string;
  touched: boolean;
  dirty: boolean;
  valid: boolean;
  loading: boolean;
}

export interface UserInputBrickActions<T = any> {
  setValue: (value: T) => void;
  setError: (error: string) => void;
  setTouched: (touched: boolean) => void;
  setDirty: (dirty: boolean) => void;
  setLoading: (loading: boolean) => void;
  validate: () => boolean | string;
  reset: () => void;
}

// =========================
// API CALL BRICK TYPES
// =========================

export interface APICallBrickState {
  loading: boolean;
  error?: Error;
  data?: any;
  retryCount: number;
  lastCall?: Date;
}

export interface APICallBrickActions {
  execute: () => Promise<void>;
  retry: () => Promise<void>;
  reset: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: Error) => void;
  setData: (data: any) => void;
}

// =========================
// BACKGROUND BRICK TYPES
// =========================

export interface BackgroundBrickState {
  isRunning: boolean;
  progress?: number;
  status?: string;
  error?: Error;
  result?: any;
}

export interface BackgroundBrickActions {
  start: () => Promise<void>;
  stop: () => void;
  reset: () => void;
  setProgress: (progress: number) => void;
  setStatus: (status: string) => void;
  setError: (error: Error) => void;
  setResult: (result: any) => void;
}

// =========================
// BRICK VALIDATION TYPES
// =========================

export interface BrickValidationRule<T = any> {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  min?: number;
  max?: number;
  custom?: (value: T) => boolean | string;
  message?: string;
}

export interface BrickValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

// =========================
// BRICK COMMUNICATION TYPES
// =========================

export interface BrickMessage {
  type: 'data' | 'error' | 'complete' | 'progress' | 'status';
  source: string;
  target?: string;
  payload: any;
  timestamp: Date;
}

export interface BrickEventEmitter {
  on: (event: string, callback: (data: any) => void) => void;
  off: (event: string, callback: (data: any) => void) => void;
  emit: (event: string, data: any) => void;
  once: (event: string, callback: (data: any) => void) => void;
}

// =========================
// BRICK REGISTRY TYPES
// =========================

export interface BrickRegistry {
  register: (type: string, brick: BrickCreator) => void;
  unregister: (type: string) => void;
  get: (type: string) => BrickCreator | undefined;
  list: () => string[];
  clear: () => void;
}

// =========================
// BRICK UTILITY TYPES
// =========================

export interface BrickUtils {
  generateId: () => string;
  validateConfig: (config: BrickConfig) => boolean | string;
  transformData: (data: any, transform: (data: any) => any) => any;
  mergeData: (target: any, source: any, type: 'string' | 'object' | 'array' | 'dict') => any;
  saveToBackend: (data: any, config: {
    backendKey: string;
    backendType: 'list' | 'dict';
    backendSubkey?: string;
  }) => Promise<any>;
}

// =========================
// BRICK ERROR TYPES
// =========================

export class BrickError extends Error {
  constructor(
    message: string,
    public brickId: string,
    public brickType: string,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'BrickError';
  }
}

export class BrickValidationError extends BrickError {
  constructor(
    message: string,
    brickId: string,
    brickType: string,
    public validationErrors: string[]
  ) {
    super(message, brickId, brickType, 'VALIDATION_ERROR');
    this.name = 'BrickValidationError';
  }
}

export class BrickExecutionError extends BrickError {
  constructor(
    message: string,
    brickId: string,
    brickType: string,
    public originalError?: Error
  ) {
    super(message, brickId, brickType, 'EXECUTION_ERROR');
    this.name = 'BrickExecutionError';
  }
}
