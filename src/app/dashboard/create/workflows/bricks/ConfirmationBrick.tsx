"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { BrickInstance, BrickExecutionResult } from '@/types/bricks';
import { BrickConfig, BrickContext, ConfirmationBrickConfig } from '@/types/workflow';
import { brickEventEmitter } from './BrickEventEmitter';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';

export class ConfirmationBrick implements BrickInstance {
  public id: string;
  public type: string = 'confirmation';
  public config: ConfirmationBrickConfig;
  public context: BrickContext;

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as ConfirmationBrickConfig;
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

  private interpolateTemplate(template: string): string {
    return template.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
      const value = this.resolveDataPath(path.trim());
      return value !== undefined ? String(value) : match;
    });
  }

  public async execute(): Promise<BrickExecutionResult> {
    try {
      // Just prepare the confirmation UI, actual completion happens on user action
      return {
        success: true,
        data: {}
      };
    } catch (error) {
      return {
        success: false,
        error: error as Error
      };
    }
  }

  public validate(): boolean | string {
    if (!this.config.message) {
      return 'Message is required';
    }
    if (!this.config.actions || this.config.actions.length === 0) {
      return 'At least one action is required';
    }
    return true;
  }

  public reset(): void {
    // No state to reset
  }

  public destroy(): void {
    // No cleanup needed
  }

  public getState(): any {
    return {};
  }
}

export const ConfirmationBrickComponent: React.FC<{
  brick: ConfirmationBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [displayData, setDisplayData] = useState<any>(null);
  const [editedValue, setEditedValue] = useState<string>('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    brick.execute();

    // Load display data if configured
    const cfg = brick.config as ConfirmationBrickConfig;
    if (cfg.displayData?.source) {
      const data = brick.resolveDataPath(cfg.displayData.source);
      setDisplayData(data);
      setEditedValue(String(data || ''));
    }
  }, [brick]);

  const handleAction = useCallback((action: any) => {
    const cfg = brick.config as ConfirmationBrickConfig;

    // Save edits if required
    if (action.saveEdit && cfg.displayData?.editable && cfg.displayData.source) {
      const path = cfg.displayData.source.replace(/^workflowData\./, '');
      brick.context.setData(prev => ({
        ...prev,
        [path]: editedValue
      }));
    }

    // Navigate to next step
    if (action.nextStep) {
      brick.context.setStep(action.nextStep);
    }

    // Trigger another brick
    if (action.triggerBrick) {
      onComplete({ action: action.action, triggerBrick: action.triggerBrick });
      return;
    }

    onComplete({ action: action.action });
  }, [brick, editedValue, onComplete]);

  const cfg = brick.config as ConfirmationBrickConfig;
  const message = brick.interpolateTemplate(cfg.message);

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-card">
      {/* Message */}
      <p className="text-sm font-medium">{message}</p>

      {/* Display Data (if configured) */}
      {cfg.displayData && displayData !== null && (
        <div className="space-y-2">
          {cfg.displayData.editable ? (
            cfg.displayData.format === 'textarea' ? (
              <Textarea
                value={editedValue}
                onChange={(e) => setEditedValue(e.target.value)}
                className="min-h-[100px]"
              />
            ) : (
              <Input
                value={editedValue}
                onChange={(e) => setEditedValue(e.target.value)}
              />
            )
          ) : (
            <div className="p-3 bg-muted rounded-md text-sm whitespace-pre-wrap">
              {String(displayData)}
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        {cfg.actions.map((action, idx) => (
          <Button
            key={idx}
            variant={action.variant || 'default'}
            onClick={() => handleAction(action)}
          >
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  );
};

