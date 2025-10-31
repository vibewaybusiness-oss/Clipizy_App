"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { BrickInstance, BrickExecutionResult } from '@/types/bricks';
import { BrickConfig, BrickContext, WaitingDisplayBrickConfig } from '@/types/workflow';
import { brickEventEmitter } from './BrickEventEmitter';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

export class WaitingDisplayBrick implements BrickInstance {
  public id: string;
  public type: string = 'waiting_display';
  public config: WaitingDisplayBrickConfig;
  public context: BrickContext;
  private responseData: any = null;
  private isWaiting: boolean = true;
  private error: Error | null = null;

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as WaitingDisplayBrickConfig;
    this.context = context;
  }

  public async execute(): Promise<BrickExecutionResult> {
    return new Promise((resolve) => {
      // Listen for completion from the target brick
      const subscriptionId = brickEventEmitter.on(`complete:${this.config.listenTo}`, (data: any) => {
        this.isWaiting = false;
        this.responseData = data;
        
        // Handle onSuccess
        if (this.config.onResponse.success?.nextStep) {
          setTimeout(() => {
            this.context.setStep(this.config.onResponse.success!.nextStep!);
          }, 500);
        }

        brickEventEmitter.offById(subscriptionId);
        brickEventEmitter.emitComplete(this.id, undefined, data);
        
        resolve({
          success: true,
          data
        });
      });

      // Listen for errors from the target brick
      const errorSubscriptionId = brickEventEmitter.on(`error:${this.config.listenTo}`, (error: Error) => {
        this.isWaiting = false;
        this.error = error;
        
        brickEventEmitter.offById(subscriptionId);
        brickEventEmitter.offById(errorSubscriptionId);
        
        resolve({
          success: false,
          error
        });
      });
    });
  }

  public validate(): boolean | string {
    if (!this.config.listenTo) {
      return 'listenTo brick ID is required';
    }
    return true;
  }

  public reset(): void {
    this.responseData = null;
    this.isWaiting = true;
    this.error = null;
  }

  public destroy(): void {
    this.responseData = null;
    this.isWaiting = false;
    this.error = null;
  }

  public getState(): any {
    return {
      responseData: this.responseData,
      isWaiting: this.isWaiting,
      error: this.error
    };
  }
}

export const WaitingDisplayBrickComponent: React.FC<{
  brick: WaitingDisplayBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [isWaiting, setIsWaiting] = useState(true);
  const [responseData, setResponseData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Start execution
    brick.execute().then(result => {
      setIsWaiting(false);
      if (result.success) {
        setResponseData(result.data);
        onComplete(result.data);
      } else {
        setError(result.error || new Error('Operation failed'));
        onError(result.error || new Error('Operation failed'));
      }
    });

    // Progress simulation if estimated time is provided
    const cfg = brick.config as WaitingDisplayBrickConfig;
    if (cfg.showProgress && cfg.estimatedTime) {
      const interval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev + (100 / (cfg.estimatedTime! * 10));
          return Math.min(newProgress, 95); // Cap at 95% until actual completion
        });
      }, 100);

      return () => clearInterval(interval);
    }
  }, [brick]);

  const handleAction = useCallback((action: any) => {
    if (action.nextStep) {
      brick.context.setStep(action.nextStep);
    }
    
    if (action.retryBrick) {
      // Reset and trigger retry
      brick.reset();
      setIsWaiting(true);
      setError(null);
      setProgress(0);
      brick.execute();
    }
  }, [brick]);

  const cfg = brick.config as WaitingDisplayBrickConfig;

  if (error) {
    return (
      <div className="flex flex-col gap-3 p-4 border border-destructive rounded-lg bg-destructive/10">
        <div className="flex items-center gap-2">
          <XCircle className="w-5 h-5 text-destructive" />
          <span className="text-sm text-destructive font-medium">
            {cfg.onResponse.error?.message || error.message}
          </span>
        </div>
        {cfg.onResponse.error?.retryable && (
          <Button variant="outline" size="sm" onClick={() => {
            brick.reset();
            setIsWaiting(true);
            setError(null);
            brick.execute();
          }}>
            Retry
          </Button>
        )}
      </div>
    );
  }

  if (isWaiting) {
    return (
      <div className="flex flex-col gap-3 p-6 border rounded-lg bg-card">
        <div className="flex items-center gap-3">
          <Loader2 className="w-5 h-5 animate-spin text-primary" />
          <span className="text-sm font-medium">{cfg.loadingMessage}</span>
        </div>
        
        {cfg.showProgress && cfg.estimatedTime && (
          <div className="space-y-2">
            <Progress value={progress} className="h-2" />
            <p className="text-xs text-muted-foreground text-center">
              Estimated time: ~{cfg.estimatedTime} seconds
            </p>
          </div>
        )}
      </div>
    );
  }

  if (responseData && cfg.onResponse.success) {
    const successConfig = cfg.onResponse.success;
    
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-green-600">
          <CheckCircle className="w-5 h-5" />
          <span className="text-sm font-medium">
            {successConfig.message || 'Operation completed successfully'}
          </span>
        </div>

        {successConfig.actions && successConfig.actions.length > 0 && (
          <div className="flex gap-2">
            {successConfig.actions.map((action, idx) => (
              <Button
                key={idx}
                variant={action.variant || 'default'}
                onClick={() => handleAction(action)}
              >
                {action.label}
              </Button>
            ))}
          </div>
        )}
      </div>
    );
  }

  return null;
};

