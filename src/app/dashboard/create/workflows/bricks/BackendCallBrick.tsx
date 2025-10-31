"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { BrickInstance, BrickExecutionResult } from '@/types/bricks';
import { BrickConfig, BrickContext } from '@/types/workflow';
import type { BackendCallBrickConfig } from '@/types/workflow';
import { brickEventEmitter } from './BrickEventEmitter';
import { Loader2 } from 'lucide-react';

export class BackendCallBrick implements BrickInstance {
  public id: string;
  public type: string = 'api_call';
  public config: BackendCallBrickConfig;
  public context: BrickContext;
  private responseData: any = null;
  private hasExecuted: boolean = false;

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as BackendCallBrickConfig;
    this.context = context;
  }

  public trigger(): void {
    // Allow manual triggering
    if (!this.hasExecuted) {
      this.execute();
    }
  }

  private interpolateTemplate(template: string): string {
    return template.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
      const cleanPath = path.trim().replace(/^workflowData\./, '');
      const keys = cleanPath.split('.');
      let value = this.context.workflowData;
      
      for (const key of keys) {
        if (value && typeof value === 'object' && key in value) {
          value = value[key];
        } else {
          return match;
        }
      }
      
      return String(value);
    });
  }

  private buildPayload(): any {
    if (!this.config.payload) return null;

    if (typeof this.config.payload === 'string') {
      return JSON.parse(this.interpolateTemplate(this.config.payload));
    }

    // Handle legacy APICallBrick payload format (source/staticData structure)
    if (this.config.payload && typeof this.config.payload === 'object' && 'source' in this.config.payload) {
      const legacyPayload = this.config.payload as any;
      if (legacyPayload.source === 'static' && legacyPayload.staticData) {
        return legacyPayload.staticData;
      }
      if (legacyPayload.source === 'workflow_data' && legacyPayload.mapping) {
        const result: any = {};
        for (const [key, path] of Object.entries(legacyPayload.mapping)) {
          const cleanPath = String(path).replace(/^workflowData\./, '');
          const keys = cleanPath.split('.');
          let value = this.context.workflowData;
          
          for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
              value = value[k];
            } else {
              value = undefined;
              break;
            }
          }
          
          result[key] = value;
        }
        return result;
      }
    }

    // Handle standard BackendCallBrick payload format
    const result: any = {};
    for (const [key, value] of Object.entries(this.config.payload)) {
      if (typeof value === 'string' && value.includes('{{')) {
        result[key] = this.interpolateTemplate(value);
      } else {
        result[key] = value;
      }
    }
    return result;
  }

  private extractResponseData(response: any): any {
    if (!this.config.saveResponse?.path) {
      return response;
    }

    const path = this.config.saveResponse.path;
    const keys = path.split('.');
    let value = response;
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return response;
      }
    }
    
    return value;
  }

  public async execute(): Promise<BrickExecutionResult> {
    // Don't auto-execute if autoExecute is false
    if (this.config.autoExecute === false && !this.hasExecuted) {
      return { success: true, data: { waiting: true } };
    }

    this.hasExecuted = true;

    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const payload = this.buildPayload();

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...this.config.headers
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const controller = new AbortController();
      const timeout = this.config.timeout || 300000; // 5 minutes default
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        // Construct full URL if endpoint is relative
        let fullUrl = this.config.endpoint;
        if (fullUrl.startsWith('/') && !fullUrl.startsWith('//')) {
          // Use Next.js API routes (proxy to backend) or construct backend URL
          const apiBase = process.env.NEXT_PUBLIC_API_URL || '';
          if (fullUrl.startsWith('/api/')) {
            // Next.js API route (proxies to backend)
            fullUrl = fullUrl;
          } else {
            // Direct backend call
            fullUrl = `${apiBase}${fullUrl}`;
          }
        }

        const response = await fetch(fullUrl, {
          method: this.config.method,
          headers,
          body: this.config.method !== 'GET' ? JSON.stringify(payload) : undefined,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const responseData = await response.json();
        const extractedData = this.extractResponseData(responseData);
        this.responseData = extractedData;

        // Save response to workflow data
        if (this.config.saveResponse) {
          this.context.setData(prev => ({
            ...prev,
            [this.config.saveResponse!.key]: extractedData
          }));
        }

        // Emit completion event
        brickEventEmitter.emitComplete(this.id, undefined, {
          response: responseData,
          extractedData
        });

        // Handle onSuccess
        if (this.config.onSuccess?.nextStep) {
          setTimeout(() => {
            this.context.setStep(this.config.onSuccess!.nextStep!);
          }, 100);
        }

        return {
          success: true,
          data: extractedData
        };
      } catch (error) {
        clearTimeout(timeoutId);
        throw error;
      }
    } catch (error) {
      console.error(`Backend call brick ${this.id} failed:`, error);
      
      const errorMessage = this.config.onError?.message || 
        (error instanceof Error ? error.message : 'Backend call failed');

      brickEventEmitter.emitError(this.id, new Error(errorMessage));

      return {
        success: false,
        error: new Error(errorMessage)
      };
    }
  }

  public validate(): boolean | string {
    if (!this.config.endpoint) {
      return 'Endpoint is required';
    }
    if (!this.config.method) {
      return 'HTTP method is required';
    }
    return true;
  }

  public reset(): void {
    this.responseData = null;
  }

  public destroy(): void {
    this.responseData = null;
  }

  public getState(): any {
    return {
      responseData: this.responseData
    };
  }

  public async trigger(): Promise<void> {
    this.hasExecuted = false;
    await this.execute();
  }
}

export const BackendCallBrickComponent: React.FC<{
  brick: BackendCallBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const executeCall = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await brick.execute();
        if (result.success) {
          if (result.data?.waiting) {
            return;
          }
          onComplete(result.data);
        } else {
          setError(result.error?.message || 'Backend call failed');
          onError(result.error || new Error('Backend call failed'));
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
        setError(errorMsg);
        onError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    if (brick.config.waitForResponse && (brick.config.autoExecute !== false)) {
      executeCall();
    }
  }, [brick]);

  if (!brick.config.waitForResponse) {
    return null; // Silent execution, no UI
  }

  if (error) {
    return (
      <div className="p-4 border border-destructive rounded-lg bg-destructive/10">
        <p className="text-destructive text-sm">{error}</p>
        {brick.config.onError?.retryable && (
          <button 
            onClick={() => brick.execute()}
            className="mt-2 text-sm underline"
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 p-4 border rounded-lg bg-muted/30">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="text-sm">Processing request...</span>
      </div>
    );
  }

  return null;
};

