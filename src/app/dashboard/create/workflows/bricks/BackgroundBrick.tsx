"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { 
  BrickConfig, 
  BrickContext, 
  BrickInstance, 
  BrickExecutionResult,
  BackgroundBrickConfig,
  BackgroundBrickState,
  BackgroundBrickActions
} from '@/types/bricks';
import { brickEventEmitter } from './BrickEventEmitter';
import { brickErrorHandler } from './BrickError';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Play, Pause, Square, CheckCircle, XCircle, Loader2 } from 'lucide-react';

export class BackgroundBrick implements BrickInstance {
  public id: string;
  public type: string = 'background';
  public config: BackgroundBrickConfig;
  public context: BrickContext;
  private state: BackgroundBrickState;
  private actions: BackgroundBrickActions;
  private intervalId: NodeJS.Timeout | null = null;
  private isDestroyed = false;

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as BackgroundBrickConfig;
    this.context = context;
    this.state = {
      isRunning: false,
      progress: undefined,
      status: undefined,
      error: undefined,
      result: undefined
    };
    this.actions = this.createActions();
  }

  private createActions(): BackgroundBrickActions {
    return {
      start: async () => {
        await this.startBackgroundProcess();
      },
      stop: () => {
        this.stopBackgroundProcess();
      },
      reset: () => {
        this.state = {
          isRunning: false,
          progress: undefined,
          status: undefined,
          error: undefined,
          result: undefined
        };
        this.emitStateChange();
      },
      setProgress: (progress: number) => {
        this.state.progress = progress;
        this.emitStateChange();
        brickEventEmitter.emitProgress(this.id, undefined, progress);
      },
      setStatus: (status: string) => {
        this.state.status = status;
        this.emitStateChange();
        brickEventEmitter.emitStatus(this.id, undefined, status);
      },
      setError: (error: Error) => {
        this.state.error = error;
        this.state.isRunning = false;
        this.emitStateChange();
        brickEventEmitter.emitError(this.id, undefined, error);
      },
      setResult: (result: any) => {
        this.state.result = result;
        this.state.isRunning = false;
        this.emitStateChange();
        brickEventEmitter.emitComplete(this.id, undefined, result);
      }
    };
  }

  private emitStateChange(): void {
    if (this.isDestroyed) return;
    
    brickEventEmitter.emitData(this.id, undefined, {
      type: 'state_change',
      state: this.state
    });
  }

  private async startBackgroundProcess(): Promise<void> {
    try {
      this.state.isRunning = true;
      this.state.error = undefined;
      this.state.result = undefined;
      this.emitStateChange();

      // Check trigger conditions
      if (this.config.trigger === 'on_condition' && this.config.condition) {
        if (!this.config.condition(this.context.workflowData)) {
          this.actions.setStatus('Condition not met, skipping');
          return;
        }
      }

      this.actions.setStatus('Starting background process...');

      // Execute the background action
      await this.executeBackgroundAction();

    } catch (error) {
      const brickError = brickErrorHandler.handleError(
        error as Error,
        this.id,
        this.type,
        { config: this.config, state: this.state }
      );
      
      this.actions.setError(brickError);
    }
  }

  private async executeBackgroundAction(): Promise<void> {
    const { action } = this.config;
    
    console.log('🔄 Background action details:', action);
    
    switch (action.type) {
      case 'api_call':
        await this.executeAPICall(action);
        break;
      case 'file_processing':
        await this.executeFileProcessing(action);
        break;
      case 'ai_generation':
        await this.executeAIGeneration(action);
        break;
      default:
        throw new Error(`Unknown action type: ${action.type}`);
    }
  }

  private async executeAPICall(config: any): Promise<void> {
    this.actions.setStatus('Making API call...');
    
    try {
      const { endpoint, method = 'POST', payload } = config;
      
      if (!endpoint) {
        throw new Error('API endpoint is required');
      }

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || '';
      const fullUrl = endpoint.startsWith('http') ? endpoint : `${backendUrl}${endpoint}`;
      
      this.actions.setStatus(`Calling ${method} ${fullUrl}...`);
      
      const token = localStorage.getItem('access_token');
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      console.log('🔄 Making API call to:', fullUrl, 'with headers:', headers);
      
      const response = await fetch(fullUrl, {
        method,
        headers,
        body: payload ? JSON.stringify(payload) : undefined,
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      this.actions.setStatus('API call completed successfully');
      this.actions.setProgress(100);
      this.state.result = result;
      this.emitStateChange();
      
      // Emit completion event
      brickEventEmitter.emitComplete(this.id, undefined, result);
      
    } catch (error) {
      console.error('API call failed:', error);
      this.actions.setError(error as Error);
      throw error;
    }
  }

  private async executeFileProcessing(config: any): Promise<void> {
    this.actions.setStatus('Processing files...');
    
    // Simulate file processing with progress updates
    for (let i = 0; i <= 100; i += 5) {
      if (this.isDestroyed) return;
      
      this.actions.setProgress(i);
      this.actions.setStatus(`Processing files: ${i}%`);
      
      // Simulate file processing delay
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    // Simulate file processing result
    const mockResult = {
      success: true,
      processedFiles: 5,
      totalSize: 1024000,
      timestamp: new Date().toISOString()
    };
    
    this.actions.setResult(mockResult);
    this.handleCompletion(mockResult);
  }

  private async executeAIGeneration(config: any): Promise<void> {
    this.actions.setStatus('Generating with AI...');
    
    // Simulate AI generation with progress updates
    const steps = [
      'Initializing AI model...',
      'Processing input data...',
      'Generating content...',
      'Post-processing...',
      'Finalizing output...'
    ];
    
    for (let i = 0; i < steps.length; i++) {
      if (this.isDestroyed) return;
      
      const progress = Math.round((i / steps.length) * 100);
      this.actions.setProgress(progress);
      this.actions.setStatus(steps[i]);
      
      // Simulate AI generation delay
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Simulate AI generation result
    const mockResult = {
      success: true,
      generatedContent: 'AI-generated content',
      confidence: 0.95,
      timestamp: new Date().toISOString()
    };
    
    this.actions.setResult(mockResult);
    this.handleCompletion(mockResult);
  }

  private handleCompletion(result: any): void {
    const { onComplete } = this.config;
    
    if (onComplete) {
      // Update workflow data if specified
      if (onComplete.dataUpdate) {
        this.context.setData(prev => ({
          ...prev,
          ...onComplete.dataUpdate
        }));
      }
      
      // Navigate to next step if specified
      if (onComplete.nextStep) {
        this.context.setStep(onComplete.nextStep);
      }
      
      // Show message if specified
      if (onComplete.message) {
        this.context.toast({
          title: 'Background Process Complete',
          description: onComplete.message
        });
      }
    }
  }

  private stopBackgroundProcess(): void {
    this.state.isRunning = false;
    this.state.status = 'Stopped';
    this.emitStateChange();
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  public async execute(): Promise<BrickExecutionResult> {
    try {
      // Check if we should start immediately
      if (this.config.trigger === 'immediate' || this.config.trigger === 'on_step_enter') {
        await this.startBackgroundProcess();
      } else if (this.config.trigger === 'on_condition') {
        // Check condition and start if met
        if (this.config.condition && this.config.condition(this.context.workflowData)) {
          await this.startBackgroundProcess();
        } else {
          return {
            success: true,
            data: { status: 'condition_not_met' }
          };
        }
      }
      
      return {
        success: true,
        data: {
          isRunning: this.state.isRunning,
          progress: this.state.progress,
          status: this.state.status,
          result: this.state.result
        }
      };
    } catch (error) {
      const brickError = brickErrorHandler.handleError(
        error as Error,
        this.id,
        this.type,
        { config: this.config }
      );
      
      return {
        success: false,
        error: brickError
      };
    }
  }

  public validate(): boolean | string {
    if (!this.config.action) {
      return 'Action configuration is required';
    }
    
    if (!this.config.action.type) {
      return 'Action type is required';
    }
    
    return true;
  }

  public reset(): void {
    this.actions.reset();
  }

  public destroy(): void {
    this.isDestroyed = true;
    this.stopBackgroundProcess();
    this.state = {
      isRunning: false,
      progress: undefined,
      status: undefined,
      error: undefined,
      result: undefined
    };
  }

  public getState(): BackgroundBrickState {
    return { ...this.state };
  }

  public getActions(): BackgroundBrickActions {
    return this.actions;
  }
}

export const BackgroundBrickComponent: React.FC<{
  brick: BackgroundBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context?: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [state, setState] = useState<BackgroundBrickState>(brick.getState());

  useEffect(() => {
    const handleStateChange = (data: any) => {
      if (data.type === 'state_change') {
        setState(data.state);
      }
    };

    const handleComplete = (data: any) => {
      onComplete(data);
    };

    const handleError = (error: Error) => {
      onError(error);
    };

    const subscriptionId = brickEventEmitter.on(`data:${brick.id}`, handleStateChange);
    const completeId = brickEventEmitter.once(`complete:${brick.id}`, handleComplete);
    const errorId = brickEventEmitter.once(`error:${brick.id}`, handleError);
    
    return () => {
      brickEventEmitter.offById(subscriptionId);
      brickEventEmitter.offById(completeId);
      brickEventEmitter.offById(errorId);
    };
  }, [brick.id, onComplete, onError]);

  const handleStart = useCallback(async () => {
    try {
      await brick.getActions().start();
    } catch (error) {
      onError(error as Error);
    }
  }, [brick, onError]);

  const handleStop = useCallback(() => {
    brick.getActions().stop();
  }, [brick]);

  const handleReset = useCallback(() => {
    brick.getActions().reset();
  }, [brick]);

  const getStatusIcon = () => {
    if (state.isRunning) {
      return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
    }
    
    if (state.error) {
      return <XCircle className="w-4 h-4 text-destructive" />;
    }
    
    if (state.result) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    
    return <Play className="w-4 h-4" />;
  };

  const getStatusText = () => {
    if (state.isRunning) {
      return state.status || 'Running...';
    }
    
    if (state.error) {
      return `Error: ${state.error.message}`;
    }
    
    if (state.result) {
      return 'Completed';
    }
    
    return 'Ready';
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-card">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium">Background Process</h3>
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="text-sm text-muted-foreground">
              {getStatusText()}
            </span>
          </div>
        </div>
        
        {state.progress !== undefined && (
          <div className="space-y-2">
            <Progress value={state.progress} className="w-full" />
            <div className="text-xs text-muted-foreground text-center">
              {state.progress}%
            </div>
          </div>
        )}
        
        {state.status && (
          <div className="text-sm text-muted-foreground">
            {state.status}
          </div>
        )}
        
        {state.error && (
          <div className="p-2 bg-destructive/10 border border-destructive/20 rounded text-sm text-destructive">
            {state.error.message}
          </div>
        )}
        
        {state.result && (
          <div className="p-2 bg-green-50 border border-green-200 rounded text-sm">
            <strong>Result:</strong> {JSON.stringify(state.result, null, 2)}
          </div>
        )}
        
        <div className="flex gap-2">
          {!state.isRunning ? (
            <Button
              onClick={handleStart}
              disabled={state.result !== undefined}
              className="flex-1"
            >
              <Play className="w-4 h-4 mr-2" />
              Start
            </Button>
          ) : (
            <Button
              onClick={handleStop}
              variant="outline"
              className="flex-1"
            >
              <Pause className="w-4 h-4 mr-2" />
              Stop
            </Button>
          )}
          
          <Button
            onClick={handleReset}
            variant="outline"
            size="sm"
          >
            <Square className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};
