"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { 
  BrickInstance, 
  BrickExecutionResult,
  APICallBrickState,
  APICallBrickActions
} from '@/types/bricks';
import { 
  BrickConfig, 
  BrickContext,
  APICallBrickConfig
} from '@/types/workflow';
import { brickEventEmitter } from './BrickEventEmitter';
import { brickErrorHandler } from './BrickError';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle, XCircle, RefreshCw } from 'lucide-react';

export class APICallBrick implements BrickInstance {
  public id: string;
  public type: string = 'api_call';
  public config: APICallBrickConfig;
  public context: BrickContext;
  private state: APICallBrickState;
  private actions: APICallBrickActions;
  private static pendingCalls: Map<string, Promise<any>> = new Map();

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as APICallBrickConfig;
    this.context = context;
    this.state = {
      loading: false,
      error: undefined,
      data: undefined,
      retryCount: 0,
      lastCall: undefined
    };
    this.actions = this.createActions();
  }

  private createActions(): APICallBrickActions {
    return {
      execute: async () => {
        await this.performAPICall();
      },
      retry: async () => {
        this.state.retryCount++;
        await this.performAPICall();
      },
      reset: () => {
        this.state = {
          loading: false,
          error: undefined,
          data: undefined,
          retryCount: 0,
          lastCall: undefined
        };
        this.emitStateChange();
      },
      setLoading: (loading: boolean) => {
        this.state.loading = loading;
        this.emitStateChange();
      },
      setError: (error: Error) => {
        this.state.error = error;
        this.emitStateChange();
      },
      setData: (data: any) => {
        this.state.data = data;
        this.emitStateChange();
      }
    };
  }

  private emitStateChange(): void {
    brickEventEmitter.emitData(this.id, undefined, {
      type: 'state_change',
      state: this.state
    });
  }

  private async performAPICall(): Promise<void> {
    try {
      // Check for duplicate calls (especially for signal-pod endpoints)
      const callKey = this.getCallKey();
      if (callKey && APICallBrick.pendingCalls.has(callKey)) {
        console.log(`⏭️ Skipping duplicate API call: ${this.config.endpoint}`, callKey);
        const existingCall = await APICallBrick.pendingCalls.get(callKey);
        this.actions.setData(existingCall);
        brickEventEmitter.emitComplete(this.id, undefined, existingCall);
        return;
      }

      this.actions.setLoading(true);
      this.state.error = undefined;
      this.state.lastCall = new Date();

      // Build payload based on configuration
      const payload = this.buildPayload();
      
      // Create call promise and track it if it's a signal-pod call
      const callPromise = this.makeAPICall(payload).then(async (response) => {
        const processedData = this.processResponse(response);
        
        // Save to workflow data
        this.saveToWorkflowData(processedData);
        
        return processedData;
      });

      // Track signal-pod calls to prevent duplicates
      if (callKey) {
        APICallBrick.pendingCalls.set(callKey, callPromise);
        callPromise.finally(() => {
          // Remove from pending after 5 seconds to allow retries
          setTimeout(() => {
            APICallBrick.pendingCalls.delete(callKey);
          }, 5000);
        });
      }
      
      // Make API call
      const processedData = await callPromise;
      
      this.actions.setData(processedData);
      brickEventEmitter.emitComplete(this.id, undefined, processedData);

    } catch (error) {
      const brickError = brickErrorHandler.handleError(
        error as Error,
        this.id,
        this.type,
        { config: this.config, retryCount: this.state.retryCount }
      );
      
      this.actions.setError(brickError);
      brickEventEmitter.emitError(this.id, undefined, brickError);
      
      // Remove from pending on error
      const callKey = this.getCallKey();
      if (callKey) {
        APICallBrick.pendingCalls.delete(callKey);
      }
    } finally {
      this.actions.setLoading(false);
    }
  }

  private getCallKey(): string | null {
    // Only deduplicate signal-pod calls
    if (this.config.endpoint.includes('signal-pod')) {
      const payload = this.buildPayload();
      return `${this.config.endpoint}:${JSON.stringify(payload)}`;
    }
    return null;
  }

  private buildPayload(): any {
    const { payload } = this.config;
    
    switch (payload.source) {
      case 'workflow_data':
        return this.buildPayloadFromWorkflowData();
      case 'user_input':
        return this.buildPayloadFromUserInput();
      case 'static':
        return payload.staticData || {};
      default:
        return {};
    }
  }

  private buildPayloadFromWorkflowData(): any {
    const { mapping, staticData } = this.config.payload;
    const payload: any = {};
    
    if (mapping) {
      Object.entries(mapping).forEach(([key, path]: [string, string]) => {
        const value = this.getNestedValue(this.context.workflowData, path);
        if (value !== undefined) {
          payload[key] = value;
        }
      });
    }
    
    if (staticData) {
      Object.assign(payload, staticData);
    }
    
    return payload;
  }

  private buildPayloadFromUserInput(): any {
    const { staticData } = this.config.payload;
    if (staticData) {
      return staticData;
    }
    // Use workflow data as fallback
    return this.buildPayloadFromWorkflowData();
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
  }

  private async makeAPICall(payload: any): Promise<Response> {
    const { endpoint, method, headers, timeout } = this.config;
    
    const controller = new AbortController();
    const timeoutId = timeout ? setTimeout(() => controller.abort(), timeout) : undefined;
    
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const authHeader = token ? { Authorization: `Bearer ${token}` } : {};
      let url = endpoint;
      if (!endpoint.startsWith('http')) {
        // Route through Next proxy for app API paths
        if (endpoint.startsWith('/api/')) {
          url = endpoint; // use browser origin
        } else {
          const envBase = (typeof process !== 'undefined' && (process as any).env && (process as any).env.NEXT_PUBLIC_API_URL) || '';
          const defaultBackend = 'http://localhost:8000';
          const base = envBase || defaultBackend;
          url = `${base}${endpoint}`;
        }
      }
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers,
          ...authHeader
        },
        body: method !== 'GET' ? JSON.stringify(payload) : undefined,
        signal: controller.signal
      });
      
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return response;
    } catch (error) {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      throw error;
    }
  }

  private async processResponse(response: Response): Promise<any> {
    const responseText = await response.text();
    let data;
    
    try {
      data = JSON.parse(responseText);
    } catch {
      data = responseText;
    }
    
    if (this.config.response?.transform) {
      return this.config.response.transform(data);
    }
    
    return data;
  }

  private saveToWorkflowData(data: any): void {
    if (!this.config.response?.saveConfig) {
      return;
    }

    const { key, type, backendKey, backendType, backendSubkey } = this.config.response.saveConfig;
    
    this.context.setData((prev: any) => {
      const updated = { ...prev };
      
      switch (type) {
        case 'string':
          updated[key] = String(data);
          break;
        case 'object':
          updated[key] = data;
          break;
        case 'array':
          if (backendType === 'list') {
            updated[backendKey] = Array.isArray(data) ? data : [data];
          } else {
            updated[key] = Array.isArray(data) ? data : [data];
          }
          break;
        case 'dict':
          if (backendType === 'dict' && backendSubkey) {
            updated[backendKey] = {
              ...updated[backendKey],
              [backendSubkey]: data
            };
          } else {
            updated[key] = { ...updated[key], ...data };
          }
          break;
      }
      
      return updated;
    });
  }

  public async execute(): Promise<BrickExecutionResult> {
    try {
      await this.performAPICall();
      
      return {
        success: true,
        data: this.state.data
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
    if (!this.config.endpoint) {
      return 'API endpoint is required';
    }
    
    if (!this.config.method) {
      return 'HTTP method is required';
    }
    
    return true;
  }

  public reset(): void {
    this.actions.reset();
  }

  public destroy(): void {
    this.state = {
      loading: false,
      error: undefined,
      data: undefined,
      retryCount: 0,
      lastCall: undefined
    };
  }

  public getState(): APICallBrickState {
    return { ...this.state };
  }

  public getActions(): APICallBrickActions {
    return this.actions;
  }
}

export const APICallBrickComponent: React.FC<{
  brick: APICallBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context?: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [state, setState] = useState<APICallBrickState>(brick.getState());

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

  const handleExecute = useCallback(async () => {
    try {
      const result = await brick.execute();
      if (result.success) {
        onComplete(result.data);
      } else {
        onError(result.error || new Error('API call failed'));
      }
    } catch (error) {
      onError(error as Error);
    }
  }, [brick, onComplete, onError]);

  const handleRetry = useCallback(async () => {
    try {
      await brick.getActions().retry();
    } catch (error) {
      onError(error as Error);
    }
  }, [brick, onError]);

  const getStatusIcon = () => {
    if (state.loading) {
      return <Loader2 className="w-4 h-4 animate-spin" />;
    }
    
    if (state.error) {
      return <XCircle className="w-4 h-4 text-destructive" />;
    }
    
    if (state.data) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    
    return null;
  };

  const getStatusText = () => {
    if (state.loading) {
      return 'Calling API...';
    }
    
    if (state.error) {
      return `Error: ${state.error.message}`;
    }
    
    if (state.data) {
      return 'API call successful';
    }
    
    return 'Ready to call API';
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-card">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium">API Call</h3>
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="text-sm text-muted-foreground">
              {getStatusText()}
            </span>
          </div>
        </div>
        
        <div className="text-xs text-muted-foreground">
          <div><strong>Endpoint:</strong> {brick.config.method} {brick.config.endpoint}</div>
          {state.lastCall && (
            <div><strong>Last Call:</strong> {state.lastCall.toLocaleTimeString()}</div>
          )}
          {state.retryCount > 0 && (
            <div><strong>Retries:</strong> {state.retryCount}</div>
          )}
        </div>
        
        {state.error && (
          <div className="p-2 bg-destructive/10 border border-destructive/20 rounded text-sm text-destructive">
            {state.error.message}
          </div>
        )}
        
        {state.data && (
          <div className="p-2 bg-green-50 border border-green-200 rounded text-sm">
            <strong>Response:</strong> {JSON.stringify(state.data, null, 2)}
          </div>
        )}
        
        <div className="flex gap-2">
          <Button
            onClick={handleExecute}
            disabled={state.loading}
            className="flex-1"
          >
            {state.loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Calling API...
              </>
            ) : (
              'Call API'
            )}
          </Button>
          
          {state.error && (
            <Button
              onClick={handleRetry}
              disabled={state.loading}
              variant="outline"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
