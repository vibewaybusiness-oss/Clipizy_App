"use client";

import { WorkflowConfig, WorkflowStep } from '@/types/workflow';
import { BrickConfig, LLMBrickConfig, UserInputBrickConfig, APICallBrickConfig, BackgroundBrickConfig } from '@/types/workflow';

export interface LegacyWorkflowStep {
  id: string;
  stepNumber: number;
  inputs?: Array<{
    type: 'text' | 'audio' | 'image';
    required?: boolean;
    saveKey: string;
    saveType: 'string' | 'object' | 'array' | 'dict';
    accept?: string;
    multiple?: boolean;
    maxFiles?: number;
    placeholder?: string;
    label?: string;
    transform?: (file: File | string, data: any) => any;
  }>;
  backendSignals?: Array<{
    workflow: string;
    inputs?: Record<string, any>;
  }>;
  paymentConfirmation?: {
    generationType: 'music' | 'video' | 'image' | 'audio';
    displayPrice: boolean;
    generationData: (data: any) => Record<string, any>;
  };
  nextStep?: string | ((data: any) => string);
  assistantMessage?: {
    content: string | ((data: any) => string);
    showDelay?: number;
  };
  actionButtons?: Array<{
    label: string;
    variant?: "default" | "outline" | "ghost";
    action: string;
    icon?: string;
    modal?: string;
  }> | ((data: any) => Array<{
    label: string;
    variant?: "default" | "outline" | "ghost";
    action: string;
    icon?: string;
    modal?: string;
  }>);
  autoSave?: boolean;
  onEnter?: (data: any, helpers: any) => void | Promise<void>;
}

export interface LegacyWorkflowConfig {
  projectType: string;
  projectName: string;
  projectDescription: string;
  initialStep: string;
  steps: Record<string, LegacyWorkflowStep>;
  actions: Record<string, (data: any, helpers: any) => Promise<void>>;
}

export class WorkflowMigrator {
  public static migrateLegacyWorkflow(legacyConfig: LegacyWorkflowConfig): WorkflowConfig {
    const steps: Record<string, WorkflowStep> = {};

    for (const [stepId, legacyStep] of Object.entries(legacyConfig.steps)) {
      steps[stepId] = this.migrateLegacyStep(stepId, legacyStep);
    }

    return {
      id: legacyConfig.projectType,
      name: legacyConfig.projectName,
      description: legacyConfig.projectDescription,
      initialStep: legacyConfig.initialStep,
      steps,
      globalSettings: {
        autoSave: true,
        errorHandling: 'stop',
        timeout: 30000
      }
    };
  }

  private static migrateLegacyStep(stepId: string, legacyStep: LegacyWorkflowStep): WorkflowStep {
    const bricks: BrickConfig[] = [];

    // Migrate inputs to UserInputBrick
    if (legacyStep.inputs) {
      for (const input of legacyStep.inputs) {
        const userInputBrick: UserInputBrickConfig = {
          id: `${stepId}-${input.saveKey}-input`,
          type: 'user_input',
          inputType: this.mapInputType(input.type),
          saveConfig: {
            key: input.saveKey,
            type: input.saveType,
            backendKey: this.getBackendKey(input.saveKey),
            backendType: this.getBackendType(input.saveType)
          },
          label: input.label,
          placeholder: input.placeholder,
          multiple: input.multiple,
          accept: input.accept,
          maxFiles: input.maxFiles,
          validation: {
            required: input.required || false
          }
        };
        bricks.push(userInputBrick);
      }
    }

    // Migrate backend signals to BackgroundBrick
    if (legacyStep.backendSignals) {
      for (const signal of legacyStep.backendSignals) {
        const apiCallAction: APICallBrickConfig = {
          id: `${stepId}-${signal.workflow}-api`,
          type: 'api_call',
          endpoint: this.getSignalEndpoint(signal.workflow),
          method: 'POST',
          payload: {
            source: 'static',
            staticData: {
              workflow: signal.workflow,
              inputs: signal.inputs || {}
            }
          }
        };

        const backgroundBrick: BackgroundBrickConfig = {
          id: `${stepId}-${signal.workflow}-background`,
          type: 'background',
          trigger: 'on_step_enter',
          action: apiCallAction
        };
        bricks.push(backgroundBrick);
      }
    }

    // Migrate payment confirmation to APICallBrick
    if (legacyStep.paymentConfirmation) {
      const paymentApiCall: APICallBrickConfig = {
        id: `${stepId}-payment-confirm`,
        type: 'api_call',
        endpoint: '/api/credits/confirm-generation',
        method: 'POST',
        payload: {
          source: 'workflow_data',
          mapping: {
            generation_type: 'generationType',
            project_id: 'projectId',
            generation_data: 'generationData',
            pricing: 'pricing'
          }
        },
        response: {
          saveConfig: {
            key: 'paymentConfirmation',
            type: 'object'
          }
        }
      };
      bricks.push(paymentApiCall);
    }

    // Migrate action buttons to LLMBrick
    if (legacyStep.actionButtons) {
      const buttons = typeof legacyStep.actionButtons === 'function' 
        ? legacyStep.actionButtons({}) // We can't call the function without data, so use empty object
        : legacyStep.actionButtons;

      if (buttons.length > 0) {
        const llmBrick: LLMBrickConfig = {
          id: `${stepId}-actions`,
          type: 'llm',
          buttons: buttons.map(btn => ({
            label: btn.label,
            action: btn.action,
            returnValue: btn.label,
            variant: btn.variant || 'default',
            modal: btn.modal
          })),
          activatePrompt: false,
          activateFileUpload: false
        };
        bricks.push(llmBrick);
      }
    }

    // If no action buttons but has assistant message, create a simple LLM brick
    if (!legacyStep.actionButtons && legacyStep.assistantMessage) {
      const llmBrick: LLMBrickConfig = {
        id: `${stepId}-message`,
        type: 'llm',
        activatePrompt: false,
        activateFileUpload: false,
        assistantMessage: legacyStep.assistantMessage
      };
      bricks.push(llmBrick);
    }

    return {
      id: stepId,
      stepNumber: legacyStep.stepNumber,
      bricks,
      nextStep: legacyStep.nextStep,
      assistantMessage: legacyStep.assistantMessage,
      autoSave: legacyStep.autoSave,
      onEnter: legacyStep.onEnter
    };
  }

  private static mapInputType(legacyType: 'text' | 'audio' | 'image'): 'text' | 'file' {
    switch (legacyType) {
      case 'text':
        return 'text';
      case 'audio':
      case 'image':
        return 'file';
      default:
        return 'text';
    }
  }

  private static getBackendKey(saveKey: string): string {
    // Map common save keys to backend keys
    const keyMapping: Record<string, string> = {
      'uploadedAudio': 'tracks',
      'uploadedImages': 'images',
      'musicDescription': 'settings',
      'videoDescription': 'settings',
      'selectedStyles': 'settings',
      'referenceImages': 'referenceImages',
      'lyrics': 'tracks',
      'genre': 'tracks',
      'isInstrumental': 'tracks'
    };
    return keyMapping[saveKey] || 'settings';
  }

  private static getBackendType(saveType: 'string' | 'object' | 'array' | 'dict'): 'list' | 'dict' {
    switch (saveType) {
      case 'array':
        return 'list';
      case 'dict':
      case 'object':
        return 'dict';
      case 'string':
      default:
        return 'dict';
    }
  }

  private static getSignalEndpoint(workflow: string): string {
    const endpointMapping: Record<string, string> = {
      'ollama': '/api/ai/runpod/signal-pod',
      'comfyui': '/api/ai/runpod/signal-pod',
      'music': '/api/ai/generate-music',
      'video': '/api/ai/generate-video'
    };
    return endpointMapping[workflow] || '/api/ai/runpod/signal-pod';
  }

  public static validateMigratedWorkflow(config: WorkflowConfig): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.id) {
      errors.push('Workflow ID is required');
    }

    if (!config.name) {
      errors.push('Workflow name is required');
    }

    if (!config.initialStep) {
      errors.push('Initial step is required');
    }

    if (!config.steps || Object.keys(config.steps).length === 0) {
      errors.push('At least one step is required');
    }

    if (config.initialStep && !config.steps[config.initialStep]) {
      errors.push(`Initial step '${config.initialStep}' not found in steps`);
    }

    // Validate each step
    for (const [stepId, step] of Object.entries(config.steps)) {
      if (!step.id) {
        errors.push(`Step ${stepId} is missing an ID`);
      }

      if (!step.bricks || step.bricks.length === 0) {
        errors.push(`Step ${stepId} has no bricks`);
      }

      // Validate each brick
      for (const brick of step.bricks) {
        if (!brick.id) {
          errors.push(`Brick in step ${stepId} is missing an ID`);
        }

        if (!brick.type) {
          errors.push(`Brick ${brick.id} is missing a type`);
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  public static createMigrationReport(legacyConfig: LegacyWorkflowConfig, migratedConfig: WorkflowConfig): string {
    const report = [];
    
    report.push('# Workflow Migration Report');
    report.push('');
    report.push(`**Source:** ${legacyConfig.projectName}`);
    report.push(`**Target:** ${migratedConfig.name}`);
    report.push(`**Steps:** ${Object.keys(legacyConfig.steps).length} → ${Object.keys(migratedConfig.steps).length}`);
    report.push('');

    report.push('## Migration Summary');
    report.push('');
    
    for (const [stepId, step] of Object.entries(migratedConfig.steps)) {
      report.push(`### Step: ${stepId}`);
      report.push(`- Bricks: ${step.bricks.length}`);
      report.push(`- Auto-save: ${step.autoSave ? 'Yes' : 'No'}`);
      report.push('');
    }

    report.push('## Brick Types');
    const brickTypes = new Set<string>();
    for (const step of Object.values(migratedConfig.steps)) {
      for (const brick of step.bricks) {
        brickTypes.add(brick.type);
      }
    }
    
    for (const type of Array.from(brickTypes).sort()) {
      report.push(`- ${type}`);
    }

    return report.join('\n');
  }
}

export const workflowMigrator = new WorkflowMigrator();
