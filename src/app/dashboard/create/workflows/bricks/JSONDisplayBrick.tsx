"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { BrickInstance, BrickExecutionResult } from '@/types/bricks';
import { BrickConfig, BrickContext, JSONDisplayBrickConfig } from '@/types/workflow';
import { brickEventEmitter } from './BrickEventEmitter';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Edit2, Save, Loader2 } from 'lucide-react';

export class JSONDisplayBrick implements BrickInstance {
  public id: string;
  public type: string = 'json_display';
  public config: JSONDisplayBrickConfig;
  public context: BrickContext;
  private editableData: Record<string, any> = {};
  private isEditing: boolean = false;

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as JSONDisplayBrickConfig;
    this.context = context;
  }

  private resolveDataPath(path: string): any {
    const cleanPath = path.replace(/^workflowData\./, '');
    const keys = cleanPath.split('.');
    let value = this.context.workflowData;
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return undefined;
      }
    }
    
    return value;
  }

  public async execute(): Promise<BrickExecutionResult> {
    try {
      const data = this.resolveDataPath(this.config.dataSource);
      
      // If data doesn't exist yet, return success with null data (component will wait)
      if (!data) {
        brickEventEmitter.emitData(this.id, undefined, { type: 'waiting_for_data' });
        return {
          success: true,
          data: null
        } as BrickExecutionResult & { waiting?: boolean };
      }

      // Initialize editable data
      this.config.display.assistantFields?.forEach((field: any) => {
        if (field.editable && data[field.key] !== undefined) {
          this.editableData[field.key] = data[field.key];
        }
      });

      brickEventEmitter.emitComplete(this.id, undefined, { data });

      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error as Error
      };
    }
  }

  public validate(): boolean | string {
    if (!this.config.dataSource) {
      return 'Data source is required';
    }
    return true;
  }

  public reset(): void {
    this.editableData = {};
    this.isEditing = false;
  }

  public destroy(): void {
    this.editableData = {};
    this.isEditing = false;
  }

  public getState(): any {
    return {
      editableData: this.editableData,
      isEditing: this.isEditing
    };
  }

  public setEditing(editing: boolean): void {
    this.isEditing = editing;
  }

  public updateEditableData(key: string, value: any): void {
    this.editableData[key] = value;
  }

  public saveEdits(): void {
    this.context.setData(prev => ({
      ...prev,
      ...this.editableData
    }));
  }
}

export const JSONDisplayBrickComponent: React.FC<{
  brick: JSONDisplayBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editableValues, setEditableValues] = useState<Record<string, any>>({});
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const executeAndDisplay = async () => {
      try {
        const cfg = brick.config as JSONDisplayBrickConfig;
        
        if ((cfg as any).waitForBrick) {
          const waitForBrickId = (cfg as any).waitForBrick;
          
          const subscriptionId = brickEventEmitter.on(`complete:${waitForBrickId}`, async (data: any) => {
            brickEventEmitter.offById(subscriptionId);
            
            await new Promise(resolve => setTimeout(resolve, 100));
            
            const result = await brick.execute();
            if (result.success && result.data) {
              setData(result.data);
              const initialEditable: Record<string, any> = {};
              cfg.display.assistantFields?.forEach(field => {
                if (field.editable && result.data[field.key] !== undefined) {
                  initialEditable[field.key] = result.data[field.key];
                }
              });
              setEditableValues(initialEditable);
              
              const assistantFields = cfg.display.assistantFields || [];
              if (assistantFields.length > 0) {
                const field = assistantFields[0];
                const value = result.data[field.key];
                if (value !== undefined) {
                  const messageContent = field.format === 'textarea' 
                    ? String(value) 
                    : `${field.label}: ${String(value)}`;
                  
                  context.addAssistantMessageWithDelay({
                    role: 'assistant',
                    content: messageContent,
                    actionButtons: cfg.actions?.map((action: any) => ({
                      label: action.label,
                      variant: action.variant || 'default',
                      action: action.action,
                      onClick: () => handleAction(action)
                    })) || [],
                    enableFileInput: false,
                    enablePromptInput: false
                  }, 0);
                }
              }
            }
          });
          
          const errorSubscriptionId = brickEventEmitter.on(`error:${waitForBrickId}`, (error: Error) => {
            brickEventEmitter.offById(subscriptionId);
            brickEventEmitter.offById(errorSubscriptionId);
            onError(error);
          });
          
          return () => {
            brickEventEmitter.offById(subscriptionId);
            brickEventEmitter.offById(errorSubscriptionId);
          };
        }
        
        const result = await brick.execute();
        if (result.success) {
          // If data is null, it means we're waiting for data to be available
          if (result.data === null) {
            // Set up listener to wait for data updates
            const checkData = () => {
              const dataPath = cfg.dataSource.replace(/^workflowData\./, '');
              const keys = dataPath.split('.');
              // Access workflowData from brick's internal context
              let value = brick.context.workflowData;
              
              for (const key of keys) {
                if (value && typeof value === 'object' && key in value) {
                  value = value[key];
                } else {
                  return null;
                }
              }
              
              return value;
            };

            // Check immediately
            const currentData = checkData();
            if (currentData) {
              setData(currentData);
              const initialEditable: Record<string, any> = {};
              cfg.display.assistantFields?.forEach((field: any) => {
                if (field.editable && currentData[field.key] !== undefined) {
                  initialEditable[field.key] = currentData[field.key];
                }
              });
              setEditableValues(initialEditable);
              
              const assistantFields = cfg.display.assistantFields || [];
              if (assistantFields.length > 0) {
                const field = assistantFields[0];
                const value = currentData[field.key];
                if (value !== undefined) {
                  const messageContent = field.format === 'textarea' 
                    ? String(value) 
                    : `${field.label}: ${String(value)}`;
                  
                  context.addAssistantMessageWithDelay({
                    role: 'assistant',
                    content: messageContent,
                    actionButtons: cfg.actions?.map((action: any) => ({
                      label: action.label,
                      variant: action.variant || 'default',
                      action: action.action,
                      onClick: () => handleAction(action)
                    })) || [],
                    enableFileInput: false,
                    enablePromptInput: false
                  }, 0);
                }
              }
              return;
            }

            // Poll for data (with timeout) - increased timeout for API calls
            let attempts = 0;
            const maxAttempts = 150; // 15 seconds max wait (increased from 5 seconds)
            const pollInterval = setInterval(() => {
              attempts++;
              const currentData = checkData();
              if (currentData) {
                clearInterval(pollInterval);
                setData(currentData);
                const initialEditable: Record<string, any> = {};
                cfg.display.assistantFields?.forEach((field: any) => {
                  if (field.editable && currentData[field.key] !== undefined) {
                    initialEditable[field.key] = currentData[field.key];
                  }
                });
                setEditableValues(initialEditable);
                
                const assistantFields = cfg.display.assistantFields || [];
                if (assistantFields.length > 0) {
                  const field = assistantFields[0];
                  const value = currentData[field.key];
                  if (value !== undefined) {
                    const messageContent = field.format === 'textarea' 
                      ? String(value) 
                      : `${field.label}: ${String(value)}`;
                    
                    context.addAssistantMessageWithDelay({
                      role: 'assistant',
                      content: messageContent,
                      actionButtons: cfg.actions?.map((action: any) => ({
                        label: action.label,
                        variant: action.variant || 'default',
                        action: action.action,
                        onClick: () => handleAction(action)
                      })) || [],
                      enableFileInput: false,
                      enablePromptInput: false
                    }, 0);
                  }
                }
              } else if (attempts >= maxAttempts) {
                clearInterval(pollInterval);
                onError(new Error(`Timeout waiting for data at ${brick.config.dataSource}`));
              }
            }, 100);

            return () => clearInterval(pollInterval);
          } else {
            // Data is available
            setData(result.data);
            const initialEditable: Record<string, any> = {};
            cfg.display.assistantFields?.forEach(field => {
              if (field.editable && result.data[field.key] !== undefined) {
                initialEditable[field.key] = result.data[field.key];
              }
            });
            setEditableValues(initialEditable);
            
            const assistantFields = cfg.display.assistantFields || [];
            if (assistantFields.length > 0) {
              const field = assistantFields[0];
              const value = result.data[field.key];
              if (value !== undefined) {
                const messageContent = field.format === 'textarea' 
                  ? String(value) 
                  : `${field.label}: ${String(value)}`;
                
                context.addAssistantMessageWithDelay({
                  role: 'assistant',
                  content: messageContent,
                  actionButtons: cfg.actions?.map((action: any) => ({
                    label: action.label,
                    variant: action.variant || 'default',
                    action: action.action,
                    onClick: () => handleAction(action)
                  })) || [],
                  enableFileInput: false,
                  enablePromptInput: false
                }, 0);
              }
            }
          }
        } else {
          onError(result.error || new Error('Failed to display JSON'));
        }
      } catch (error) {
        onError(error as Error);
      }
    };

    executeAndDisplay();
  }, [brick]); // workflowData is accessed from brick.context, not WorkflowContext

  const handleAction = useCallback(async (action: any) => {
    if (action.enableEdit) {
      setIsEditing(true);
      return;
    }

    if (action.saveEdits && isEditing) {
      // Save edits to workflow data
      brick.context.setData(prev => ({
        ...prev,
        ...editableValues
      }));
      setIsEditing(false);
    }

    if (action.triggerBrick) {
      // Trigger another brick by emitting an event
      const { brickEventEmitter } = await import('./BrickEventEmitter');
      brickEventEmitter.emit(`trigger:${action.triggerBrick}`, {});
    }

    if (action.nextStep) {
      brick.context.setStep(action.nextStep);
    }

    onComplete({ action: action.action, data: editableValues });
  }, [brick, editableValues, isEditing, onComplete]);

  // JSONDisplayBrick injects messages into chat, so return null (no inline UI)
  return null;
};

