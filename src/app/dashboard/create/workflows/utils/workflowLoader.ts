import { WorkflowConfig, WorkflowStep } from '@/types/workflow';
import { brickValidator } from '../bricks/BrickValidation';

export class WorkflowLoader {
  private static instance: WorkflowLoader;
  private loadedWorkflows: Map<string, WorkflowConfig> = new Map();
  private loadingPromises: Map<string, Promise<WorkflowConfig>> = new Map();

  private constructor() {}

  public static getInstance(): WorkflowLoader {
    if (!WorkflowLoader.instance) {
      WorkflowLoader.instance = new WorkflowLoader();
    }
    return WorkflowLoader.instance;
  }

  public async loadFromJSON(jsonPath: string): Promise<WorkflowConfig> {
    try {
      // Remove .json extension if present
      const cleanPath = jsonPath.replace(/\.json$/, '');

      // Check cache first
      if (this.loadedWorkflows.has(cleanPath)) {
        return this.loadedWorkflows.get(cleanPath)!;
      }

      // Check if already loading
      if (this.loadingPromises.has(cleanPath)) {
        return await this.loadingPromises.get(cleanPath)!;
      }

      // Start loading
      const loadPromise = this.fetchWorkflowConfig(cleanPath);
      this.loadingPromises.set(cleanPath, loadPromise);

      try {
        const config = await loadPromise;
        this.loadedWorkflows.set(cleanPath, config);
        return config;
      } finally {
        this.loadingPromises.delete(cleanPath);
      }
    } catch (error) {
      console.error('❌ Failed to load workflow:', error);
      throw new Error(`Failed to load workflow from ${jsonPath}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async fetchWorkflowConfig(cleanPath: string): Promise<WorkflowConfig> {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const backendUrl = `${apiBase}/api/chatbot/workflows/${cleanPath}`;

    console.log('🔄 Loading workflow from backend:', backendUrl);

    const response = await fetch(backendUrl, {
      headers: {
        'Content-Type': 'application/json'
      },
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => response.statusText);
      throw new Error(`Failed to fetch workflow config: ${response.status} ${response.statusText}. ${errorText}`);
    }

    const config = await response.json();
    console.log('✅ Workflow config fetched successfully:', config);
    return this.validate(config);
  }

  public async loadFromFile(file: File): Promise<WorkflowConfig> {
    try {
      const text = await file.text();
      const config = JSON.parse(text);
      return this.validate(config);
    } catch (error) {
      throw new Error(`Failed to load workflow from file: ${error instanceof Error ? error.message : 'Invalid JSON'}`);
    }
  }

  public saveToFile(config: WorkflowConfig, filename?: string): void {
    const jsonString = JSON.stringify(config, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `${config.id}-workflow.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  public loadFromObject(config: any): WorkflowConfig {
    return this.validate(config);
  }

  public validate(config: any): WorkflowConfig {
    const errors: string[] = [];

    // Validate basic structure
    if (!config.id || typeof config.id !== 'string') {
      errors.push('Workflow ID is required and must be a string');
    }

    if (!config.name || typeof config.name !== 'string') {
      errors.push('Workflow name is required and must be a string');
    }

    if (!config.description || typeof config.description !== 'string') {
      errors.push('Workflow description is required and must be a string');
    }

    if (!config.initialStep || typeof config.initialStep !== 'string') {
      errors.push('Initial step is required and must be a string');
    }

    if (!config.steps || typeof config.steps !== 'object') {
      errors.push('Steps configuration is required and must be an object');
    }

    // Validate steps
    if (config.steps) {
      const stepIds = Object.keys(config.steps);
      
      if (stepIds.length === 0) {
        errors.push('At least one step is required');
      }

      // Check if initial step exists
      if (!stepIds.includes(config.initialStep)) {
        errors.push(`Initial step '${config.initialStep}' not found in steps`);
      }

      // Validate each step
      stepIds.forEach(stepId => {
        const stepErrors = this.validateStep(stepId, config.steps[stepId]);
        errors.push(...stepErrors);
      });
    }

    // Validate global settings if present
    if (config.globalSettings) {
      const settingsErrors = this.validateGlobalSettings(config.globalSettings);
      errors.push(...settingsErrors);
    }

    if (errors.length > 0) {
      throw new Error(`Workflow validation failed:\n${errors.join('\n')}`);
    }

    // Cache the validated workflow
    this.loadedWorkflows.set(config.id, config as WorkflowConfig);
    
    return config as WorkflowConfig;
  }

  private validateStep(stepId: string, step: any): string[] {
    const errors: string[] = [];

    if (!step.id || step.id !== stepId) {
      errors.push(`Step ${stepId}: ID must match step key`);
    }

    if (!step.stepNumber || typeof step.stepNumber !== 'number') {
      errors.push(`Step ${stepId}: Step number is required and must be a number`);
    }

    if (!step.bricks || !Array.isArray(step.bricks)) {
      errors.push(`Step ${stepId}: Bricks array is required`);
    }

    // Validate bricks
    if (step.bricks && Array.isArray(step.bricks)) {
      step.bricks.forEach((brick: any, index: number) => {
        const brickErrors = this.validateBrick(stepId, index, brick);
        errors.push(...brickErrors);
      });
    }

    // Validate nextStep
    if (step.nextStep) {
      if (typeof step.nextStep !== 'string' && typeof step.nextStep !== 'function') {
        errors.push(`Step ${stepId}: nextStep must be a string or function`);
      }
    }

    // Validate conditions
    if (step.conditions && Array.isArray(step.conditions)) {
      step.conditions.forEach((condition: any, index: number) => {
        if (!condition.condition || typeof condition.condition !== 'function') {
          errors.push(`Step ${stepId}: Condition ${index} must have a function`);
        }
        if (!condition.nextStep || typeof condition.nextStep !== 'string') {
          errors.push(`Step ${stepId}: Condition ${index} must have a nextStep string`);
        }
      });
    }

    // Validate assistantMessage
    if (step.assistantMessage) {
      if (typeof step.assistantMessage.content !== 'string' && typeof step.assistantMessage.content !== 'function') {
        errors.push(`Step ${stepId}: Assistant message content must be a string or function`);
      }
      if (step.assistantMessage.showDelay !== undefined && typeof step.assistantMessage.showDelay !== 'number') {
        errors.push(`Step ${stepId}: Assistant message showDelay must be a number`);
      }
    }

    // Validate autoSave
    if (step.autoSave !== undefined && typeof step.autoSave !== 'boolean') {
      errors.push(`Step ${stepId}: autoSave must be a boolean`);
    }

    return errors;
  }

  private validateBrick(stepId: string, brickIndex: number, brick: any): string[] {
    const errors: string[] = [];

    if (!brick.id || typeof brick.id !== 'string') {
      errors.push(`Step ${stepId}, Brick ${brickIndex}: ID is required and must be a string`);
    }

    if (!brick.type || typeof brick.type !== 'string') {
      errors.push(`Step ${stepId}, Brick ${brickIndex}: Type is required and must be a string`);
    }

    // Validate brick configuration based on type
    const brickValidation = brickValidator.validate(brick, {
      required: true,
      message: 'Brick configuration is required'
    });
    if (!brickValidation.valid) {
      errors.push(...brickValidation.errors.map(error => 
        `Step ${stepId}, Brick ${brickIndex}: ${error}`
      ));
    }

    return errors;
  }

  private validateGlobalSettings(settings: any): string[] {
    const errors: string[] = [];

    if (settings.autoSave !== undefined && typeof settings.autoSave !== 'boolean') {
      errors.push('Global autoSave must be a boolean');
    }

    if (settings.errorHandling && !['continue', 'stop', 'retry'].includes(settings.errorHandling)) {
      errors.push('Global errorHandling must be one of: continue, stop, retry');
    }

    if (settings.timeout !== undefined && (typeof settings.timeout !== 'number' || settings.timeout <= 0)) {
      errors.push('Global timeout must be a positive number');
    }

    return errors;
  }

  public getLoadedWorkflow(id: string): WorkflowConfig | undefined {
    return this.loadedWorkflows.get(id);
  }

  public getAllLoadedWorkflows(): WorkflowConfig[] {
    return Array.from(this.loadedWorkflows.values());
  }

  public clearCache(): void {
    this.loadedWorkflows.clear();
  }

  public removeWorkflow(id: string): boolean {
    return this.loadedWorkflows.delete(id);
  }

  public hasWorkflow(id: string): boolean {
    return this.loadedWorkflows.has(id);
  }

  public exportWorkflow(id: string): string {
    const workflow = this.loadedWorkflows.get(id);
    if (!workflow) {
      throw new Error(`Workflow '${id}' not found`);
    }
    
    return JSON.stringify(workflow, null, 2);
  }

  public importWorkflow(jsonString: string): WorkflowConfig {
    try {
      const config = JSON.parse(jsonString);
      return this.validate(config);
    } catch (error) {
      throw new Error(`Failed to import workflow: ${error instanceof Error ? error.message : 'Invalid JSON'}`);
    }
  }

  public getWorkflowSummary(id: string): {
    id: string;
    name: string;
    description: string;
    stepCount: number;
    brickCount: number;
    hasErrors: boolean;
  } | null {
    const workflow = this.loadedWorkflows.get(id);
    if (!workflow) {
      return null;
    }

    const stepCount = Object.keys(workflow.steps).length;
    const brickCount = Object.values(workflow.steps).reduce((total, step) => {
      return total + (step.bricks ? step.bricks.length : 0);
    }, 0);

    return {
      id: workflow.id,
      name: workflow.name,
      description: workflow.description,
      stepCount,
      brickCount,
      hasErrors: false // This would be determined by validation
    };
  }
}

export const workflowLoader = WorkflowLoader.getInstance();
