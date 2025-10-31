// =========================
// WORKFLOW SYSTEM TYPES
// =========================

export interface WorkflowContext {
  projectId?: string | null;
  setProjectId?: (id: string) => void;
  messages: Message[];
  setMessages: (updater: (prev: Message[]) => Message[]) => void;
  addAssistantMessageWithDelay: (message: Omit<Message, 'id' | 'timestamp'>, delay?: number) => void;
  prompt: string;
  setPrompt: (prompt: string) => void;
  inputEnabled: boolean;
  setInputEnabled: (enabled: boolean) => void;
  fileInputEnabled: boolean;
  setFileInputEnabled: (enabled: boolean) => void;
  fileInputRef: React.RefObject<HTMLInputElement>;
  uploadedImages: File[];
  setUploadedImages: (updater: (prev: File[]) => File[]) => void;
  uploadedAudio: File[];
  setUploadedAudio: (updater: (prev: File[]) => File[]) => void;
  isGenerating: boolean;
  setIsGenerating: (generating: boolean) => void;
  toast: (options: ToastOptions) => void;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  files?: {
    images: (File | { name: string; size?: number; type?: string; fileId?: string; url?: string })[];
    audio: (File | { name: string; size?: number; type?: string; fileId?: string; url?: string })[];
  };
  actionButtons?: ActionButton[];
  enableFileInput?: boolean;
  enablePromptInput?: boolean;
}

export interface ActionButton {
  label?: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  className?: string;
  disabled?: boolean;
  onClick: () => void;
}

export interface ToastOptions {
  title: string;
  description?: string;
  variant?: 'default' | 'destructive';
  duration?: number;
}

export interface WorkflowStep {
  id: string;
  stepNumber: number;
  bricks: BrickConfig[];
  nextStep: string | ((data: any) => string);
  conditions?: Array<{
    condition: (data: any) => boolean;
    nextStep: string;
  }>;
  assistantMessage?: {
    content: string | ((data: any) => string);
    showDelay?: number;
    enableFileInput?: boolean;
    enablePromptInput?: boolean;
  };
  autoSave?: boolean;
}

export interface WorkflowConfig {
  id: string;
  name: string;
  description: string;
  initialStep: string;
  steps: Record<string, WorkflowStep>;
  globalSettings?: {
    autoSave: boolean;
    errorHandling: 'continue' | 'stop' | 'retry';
    timeout: number;
  };
}

export interface WorkflowHelpers {
  setData: (updater: (prev: any) => any) => void;
  setStep: (step: string) => void | Promise<void>;
  saveState: (projectId: string | null | undefined) => Promise<void>;
  toast: (options: ToastOptions) => void;
  projectId?: string | null;
}

// =========================
// BRICK CONFIGURATION TYPES
// =========================

export type BrickType = 'llm' | 'user_input' | 'api_call' | 'background' | 'json_display' | 'waiting_display' | 'media_display' | 'confirmation' | 'batch_media_display';

export interface BaseBrickConfig {
  id: string;
  type: BrickType;
  enabled?: boolean;
  validation?: {
    required?: boolean;
    custom?: (value: any) => boolean | string;
  };
}

export interface LLMBrickConfig extends BaseBrickConfig {
  type: 'llm';
  buttons: Array<{
    label: string;
    action: string;
    returnValue: any;
    variant?: 'default' | 'outline' | 'ghost';
    userMessage?: string;
  }>;
  activatePrompt: boolean;
  activateFileUpload: boolean;
  fileTypes?: string[];
  prompt: {
    placeholder: string;
    editable: boolean;
    confirmRequired: boolean;
  };
  assistantMessage?: {
    content: string;
    showDelay?: number;
    enableFileInput?: boolean;
    enablePromptInput?: boolean;
  };
}

export interface UserInputBrickConfig extends BaseBrickConfig {
  type: 'user_input';
  inputType: 'text' | 'file' | 'multiselect' | 'select' | 'checkbox' | 'radio';
  saveConfig: {
    key: string;
    type: 'string' | 'object' | 'array' | 'dict';
    backendKey: string;
    backendType: 'list' | 'dict';
    backendSubkey?: string;
  };
  validation?: {
    required: boolean;
    minLength?: number;
    maxLength?: number;
    pattern?: string;
    custom?: (value: any) => boolean | string;
  };
  options?: Array<{
    label: string;
    value: any;
    disabled?: boolean;
  }>;
  placeholder?: string;
  label?: string;
  accept?: string;
  multiple?: boolean;
  maxFiles?: number;
}

export interface APICallBrickConfig extends BaseBrickConfig {
  type: 'api_call';
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  payload: {
    source: 'workflow_data' | 'user_input' | 'static';
    mapping?: Record<string, string>;
    staticData?: any;
  };
  response?: {
    saveConfig?: {
      key: string;
      type: 'string' | 'object' | 'array' | 'dict';
      backendKey: string;
      backendType: 'list' | 'dict';
      backendSubkey?: string;
    };
    transform?: (response: any) => any;
  };
  headers?: Record<string, string>;
  timeout?: number;
  retries?: number;
}

export interface BackendCallBrickConfig extends BaseBrickConfig {
  type: 'api_call';
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  payload?: Record<string, any> | string; // Can use {{workflowData.field}} templates
  waitForResponse: boolean;
  timeout?: number;
  autoExecute?: boolean; // If false, wait for manual trigger (default: true)
  saveResponse?: {
    key: string;
    path?: string; // JSONPath to extract from response, e.g., "data.prompt"
    transform?: string; // Name of transform function
  };
  onSuccess?: {
    nextBrick?: string;
    nextStep?: string;
    message?: string;
  };
  onError?: {
    message?: string;
    retryable?: boolean;
    nextStep?: string;
  };
  headers?: Record<string, string>;
}

export interface BackgroundBrickConfig extends BaseBrickConfig {
  type: 'background';
  trigger: 'immediate' | 'on_step_enter' | 'on_condition';
  condition?: (data: any) => boolean;
  action: {
    id?: string;
    type: 'api_call' | 'file_processing' | 'ai_generation';
    endpoint?: string;
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    payload?: {
      source: 'workflow_data' | 'user_input' | 'static';
      mapping?: Record<string, string>;
      staticData?: any;
    };
    config?: any;
  };
  onComplete?: {
    nextStep?: string;
    message?: string;
    dataUpdate?: Record<string, any>;
  };
}

export interface FileProcessingConfig {
  type: 'file_processing';
  operation: 'upload' | 'download' | 'transform' | 'analyze';
  config: {
    s3Key?: string;
    backendKey: string;
    backendType: 'list' | 'dict';
    backendSubkey?: string;
    transform?: (file: File) => any;
  };
}

export interface AIGenerationConfig {
  type: 'ai_generation';
  model: string;
  parameters: Record<string, any>;
  inputMapping: Record<string, string>;
  outputMapping: {
    saveKey: string;
    saveType: 'string' | 'object' | 'array' | 'dict';
  };
}

export interface JSONDisplayBrickConfig extends BaseBrickConfig {
  type: 'json_display';
  dataSource: string; // Path to data in workflowData, e.g., "workflowData.musicPromptData"
  display: {
    userFields?: Array<{
      key: string;
      label: string;
      format?: 'text' | 'textarea';
    }>;
    assistantFields?: Array<{
      key: string;
      label: string;
      editable?: boolean;
      format?: 'text' | 'textarea';
    }>;
  };
  actions?: Array<{
    label: string;
    action: string;
    variant?: 'default' | 'outline' | 'ghost' | 'destructive';
    enableEdit?: boolean;
    saveEdits?: boolean;
    triggerBrick?: string;
    nextStep?: string;
    nextBrick?: string;
  }>;
}

export interface WaitingDisplayBrickConfig extends BaseBrickConfig {
  type: 'waiting_display';
  listenTo: string; // Brick ID to listen to
  loadingMessage?: string;
  estimatedTime?: number; // in seconds
  showProgress?: boolean;
  onResponse?: {
    success?: {
      displayAs?: 'text' | 'json';
      message?: string;
      nextBrick?: string;
      nextStep?: string;
    };
    error?: {
      message?: string;
      retryable?: boolean;
      nextStep?: string;
    };
  };
}

export interface MediaDisplayBrickConfig extends BaseBrickConfig {
  type: 'media_display';
  mediaType: 'audio' | 'video' | 'image';
  mediaUrl: string; // Path to URL in workflowData or direct URL
  metadata?: {
    title?: string;
    description?: string;
  };
  controls?: {
    play?: boolean;
    seek?: boolean;
    volume?: boolean;
    download?: boolean;
  };
  actions?: Array<{
    label: string;
    action: string;
    variant?: 'default' | 'outline' | 'ghost' | 'destructive';
    nextStep?: string;
    triggerBrick?: string;
  }>;
}

export interface ConfirmationBrickConfig extends BaseBrickConfig {
  type: 'confirmation';
  message: string;
  dataToDisplay?: {
    dataSource: string;
    fields: Array<{
      key: string;
      label: string;
      editable?: boolean;
      format?: 'text' | 'textarea';
    }>;
  };
  actions: Array<{
    label: string;
    action: string;
    variant?: 'default' | 'outline' | 'ghost' | 'destructive';
    nextStep?: string;
    nextBrick?: string;
  }>;
}

export interface BatchMediaDisplayBrickConfig extends BaseBrickConfig {
  type: 'batch_media_display';
  generations: Array<{
    mediaType: 'text' | 'image' | 'audio' | 'video';
    label?: string;
    endpoint: string;
    payload?: Record<string, any>;
    contentPath?: string;
    regenerationPrice?: string;
  }>;
  saveKey?: string;
  onComplete?: {
    nextStep?: string;
    message?: string;
  };
}

export type BrickConfig = 
  | LLMBrickConfig 
  | UserInputBrickConfig 
  | APICallBrickConfig 
  | BackendCallBrickConfig
  | BackgroundBrickConfig
  | JSONDisplayBrickConfig
  | WaitingDisplayBrickConfig
  | MediaDisplayBrickConfig
  | ConfirmationBrickConfig
  | BatchMediaDisplayBrickConfig;

// =========================
// BRICK CONTEXT TYPES
// =========================

export interface BrickContext {
  workflowData: Record<string, any>;
  setData: (updater: (prev: any) => any) => void;
  setStep: (stepId: string) => void;
  saveState: (projectId: string) => Promise<void>;
  toast: (options: ToastOptions) => void;
  projectId?: string;
}

export interface BrickProps<T = any> {
  config: BrickConfig;
  context: BrickContext;
  onComplete: (value: T) => void;
  onError: (error: Error) => void;
}

// =========================
// WORKFLOW EXECUTION TYPES
// =========================

export interface WorkflowExecutionState {
  currentStep: string;
  workflowData: Record<string, any>;
  isExecuting: boolean;
  error?: Error;
  completedSteps: string[];
}

export interface WorkflowExecutionResult {
  success: boolean;
  data?: any;
  error?: Error;
  nextStep?: string;
}
