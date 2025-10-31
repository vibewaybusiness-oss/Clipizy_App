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
        const result = await brick.execute();
        if (result.success) {
          // If data is null, it means we're waiting for data to be available
          if (result.data === null) {
            // Set up listener to wait for data updates
            const checkData = () => {
              const cfg = brick.config as JSONDisplayBrickConfig;
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
              const cfg = brick.config as JSONDisplayBrickConfig;
              const initialEditable: Record<string, any> = {};
              cfg.display.assistantFields?.forEach((field: any) => {
                if (field.editable && currentData[field.key] !== undefined) {
                  initialEditable[field.key] = currentData[field.key];
                }
              });
              setEditableValues(initialEditable);
              return;
            }

            // Poll for data (with timeout) - use useEffect to track workflowData changes
            let attempts = 0;
            const maxAttempts = 50; // 5 seconds max wait
            const pollInterval = setInterval(() => {
              attempts++;
              const currentData = checkData();
              if (currentData) {
                clearInterval(pollInterval);
                setData(currentData);
                const cfg = brick.config as JSONDisplayBrickConfig;
                const initialEditable: Record<string, any> = {};
                cfg.display.assistantFields?.forEach((field: any) => {
                  if (field.editable && currentData[field.key] !== undefined) {
                    initialEditable[field.key] = currentData[field.key];
                  }
                });
                setEditableValues(initialEditable);
              } else if (attempts >= maxAttempts) {
                clearInterval(pollInterval);
                onError(new Error(`Timeout waiting for data at ${brick.config.dataSource}`));
              }
            }, 100);

            return () => clearInterval(pollInterval);
          } else {
            // Data is available
            setData(result.data);
            const cfg = brick.config as JSONDisplayBrickConfig;
            const initialEditable: Record<string, any> = {};
            cfg.display.assistantFields?.forEach(field => {
              if (field.editable && result.data[field.key] !== undefined) {
                initialEditable[field.key] = result.data[field.key];
              }
            });
            setEditableValues(initialEditable);
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

  const cfg = brick.config as JSONDisplayBrickConfig;

  // If data is null (waiting for data), show loading state
  if (!data) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-center space-y-2">
          <Loader2 className="w-6 h-6 animate-spin mx-auto text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Waiting for data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* User Fields - Display as user messages */}
      {cfg.display.userFields && cfg.display.userFields.length > 0 && (
        <div className="space-y-2">
          {cfg.display.userFields.map((field: any, idx: number) => {
            const value = data[field.key];
            if (value === undefined) return null;

            return (
              <div key={idx} className="flex justify-end">
                <div className="max-w-[70%] bg-blue-600 text-white rounded-2xl px-4 py-2">
                  <div className="text-xs opacity-80 mb-1">{field.label}</div>
                  <div className="text-sm">{String(value)}</div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Assistant Fields - Display as assistant messages */}
      {cfg.display.assistantFields && cfg.display.assistantFields.length > 0 && (
        <div className="space-y-2">
          {cfg.display.assistantFields.map((field: any, idx: number) => {
            const value = data[field.key];
            if (value === undefined) return null;

            return (
              <div key={idx} className="flex justify-start">
                <div className="max-w-[70%] bg-card border rounded-2xl px-4 py-3">
                  <div className="text-xs text-muted-foreground mb-2">{field.label}</div>
                  {field.editable && isEditing ? (
                    field.format === 'textarea' ? (
                      <Textarea
                        value={editableValues[field.key] || ''}
                        onChange={(e) => setEditableValues(prev => ({
                          ...prev,
                          [field.key]: e.target.value
                        }))}
                        className="min-h-[100px]"
                      />
                    ) : (
                      <Input
                        value={editableValues[field.key] || ''}
                        onChange={(e) => setEditableValues(prev => ({
                          ...prev,
                          [field.key]: e.target.value
                        }))}
                      />
                    )
                  ) : (
                    <div className="text-sm whitespace-pre-wrap">{String(value)}</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Actions */}
      {cfg.actions && cfg.actions.length > 0 && (
        <div className="flex gap-2 justify-end">
          {cfg.actions.map((action: any, idx: number) => {
            if (action.enableEdit && !isEditing) {
              return (
                <Button
                  key={idx}
                  variant={action.variant || 'outline'}
                  onClick={() => setIsEditing(true)}
                >
                  <Edit2 className="w-4 h-4 mr-2" />
                  {action.label}
                </Button>
              );
            }

            if (action.saveEdits && isEditing) {
              return (
                <Button
                  key={idx}
                  variant={action.variant || 'default'}
                  onClick={() => handleAction(action)}
                >
                  <Save className="w-4 h-4 mr-2" />
                  {action.label}
                </Button>
              );
            }

            if (!action.enableEdit || isEditing) {
              return (
                <Button
                  key={idx}
                  variant={action.variant || 'default'}
                  onClick={() => handleAction(action)}
                >
                  {action.label}
                </Button>
              );
            }

            return null;
          })}
        </div>
      )}
    </div>
  );
};

