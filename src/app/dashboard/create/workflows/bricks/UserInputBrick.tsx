"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { 
  BrickConfig, 
  BrickContext, 
  BrickInstance, 
  BrickExecutionResult,
  UserInputBrickConfig,
  UserInputBrickState,
  UserInputBrickActions
} from '@/types/bricks';
import { brickEventEmitter } from './BrickEventEmitter';
import { brickErrorHandler } from './BrickError';
import { brickValidator } from './BrickValidation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Upload, X, AlertCircle } from 'lucide-react';

export class UserInputBrick implements BrickInstance {
  public id: string;
  public type: string = 'user_input';
  public config: UserInputBrickConfig;
  public context: BrickContext;
  private state: UserInputBrickState;
  private actions: UserInputBrickActions;

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as UserInputBrickConfig;
    this.context = context;
    this.state = {
      value: this.getDefaultValue(),
      error: undefined,
      touched: false,
      dirty: false,
      valid: true,
      loading: false
    };
    this.actions = this.createActions();
  }

  private getDefaultValue(): any {
    switch (this.config.inputType) {
      case 'text':
      case 'file':
        return '';
      case 'multiselect':
      case 'select':
        return [];
      case 'checkbox':
        return false;
      case 'radio':
        return null;
      default:
        return null;
    }
  }

  private createActions(): UserInputBrickActions {
    return {
      setValue: (value: any) => {
        this.state.value = value;
        this.state.dirty = true;
        this.validateValue();
        this.emitStateChange();
      },
      setError: (error: string) => {
        this.state.error = error;
        this.state.valid = false;
        this.emitStateChange();
      },
      setTouched: (touched: boolean) => {
        this.state.touched = touched;
        this.emitStateChange();
      },
      setDirty: (dirty: boolean) => {
        this.state.dirty = dirty;
        this.emitStateChange();
      },
      setLoading: (loading: boolean) => {
        this.state.loading = loading;
        this.emitStateChange();
      },
      validate: () => {
        return this.validateValue();
      },
      reset: () => {
        this.state = {
          value: this.getDefaultValue(),
          error: undefined,
          touched: false,
          dirty: false,
          valid: true,
          loading: false
        };
        this.emitStateChange();
      }
    };
  }

  private validateValue(): boolean | string {
    if (!this.config.validation) {
      this.state.valid = true;
      this.state.error = undefined;
      return true;
    }

    const validationRule: any = {
      ...this.config.validation,
      pattern: this.config.validation?.pattern ? new RegExp(this.config.validation.pattern) : undefined
    };
    
    const result = brickValidator.validate(this.state.value, validationRule);
    this.state.valid = result.valid;
    this.state.error = result.valid ? undefined : result.errors[0];

    return result.valid ? true : result.errors[0];
  }

  private emitStateChange(): void {
    brickEventEmitter.emitData(this.id, undefined, {
      type: 'state_change',
      state: this.state
    });
  }

  public async execute(): Promise<BrickExecutionResult> {
    try {
      this.actions.setTouched(true);
      const isValid = this.validateValue();

      if (!isValid) {
        return {
          success: false,
          error: new Error(this.state.error || 'Validation failed')
        };
      }

      // Save to workflow data
      this.context.setData(prev => {
        const updated = { ...prev };
        const { key, type, backendKey, backendType, backendSubkey } = this.config.saveConfig;
        
        // Transform data based on save type
        let transformedValue = this.state.value;
        if (this.config.inputType === 'file' && this.state.value instanceof File) {
          transformedValue = {
            fileName: this.state.value.name,
            fileSize: this.state.value.size,
            fileType: this.state.value.type,
            file: this.state.value
          };
        }

        // Apply save type transformation
        switch (type) {
          case 'string':
            updated[key] = transformedValue;
            break;
          case 'object':
            updated[key] = transformedValue;
            break;
          case 'array':
            updated[key] = Array.isArray(transformedValue) ? transformedValue : [transformedValue];
            break;
          case 'dict':
            updated[key] = { ...updated[key], ...transformedValue };
            break;
        }

        return updated;
      });

      // Emit completion event
      brickEventEmitter.emitComplete(this.id, undefined, {
        value: this.state.value,
        saveConfig: this.config.saveConfig
      });

      return {
        success: true,
        data: {
          value: this.state.value,
          saveConfig: this.config.saveConfig
        }
      };

    } catch (error) {
      const brickError = brickErrorHandler.handleError(
        error as Error,
        this.id,
        this.type,
        { config: this.config, value: this.state.value }
      );
      
      return {
        success: false,
        error: brickError
      };
    }
  }

  public validate(): boolean | string {
    return this.validateValue();
  }

  public reset(): void {
    this.actions.reset();
  }

  public destroy(): void {
    this.state = {
      value: this.getDefaultValue(),
      error: undefined,
      touched: false,
      dirty: false,
      valid: true,
      loading: false
    };
  }

  public getState(): UserInputBrickState {
    return { ...this.state };
  }

  public getActions(): UserInputBrickActions {
    return this.actions;
  }
}

export const UserInputBrickComponent: React.FC<{
  brick: UserInputBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [state, setState] = useState<UserInputBrickState>(brick.getState());

  useEffect(() => {
    const handleStateChange = (data: any) => {
      if (data.type === 'state_change') {
        setState(data.state);
      }
    };

    const subscriptionId = brickEventEmitter.on(`data:${brick.id}`, handleStateChange);
    
    return () => {
      brickEventEmitter.offById(subscriptionId);
    };
  }, [brick.id]);

  const handleValueChange = useCallback((value: any) => {
    brick.getActions().setValue(value);
  }, [brick]);

  const handleBlur = useCallback(() => {
    brick.getActions().setTouched(true);
  }, [brick]);

  const handleSubmit = useCallback(async () => {
    try {
      const result = await brick.execute();
      if (result.success) {
        const cfg = brick.config;
        let content = '';
        if (cfg.inputType === 'text') {
          content = String(state.value || '').trim();
        } else if (cfg.inputType === 'file') {
          if (Array.isArray(state.value)) content = `Uploaded ${state.value.length} file(s)`;
          else if (state.value?.name) content = `Uploaded ${state.value.name}`;
          else content = 'Uploaded file(s)';
        } else if (cfg.inputType === 'multiselect') {
          const labels = (cfg.options || []).filter(o => (state.value || []).includes(o.value)).map(o => o.label);
          content = labels.length ? `Selected: ${labels.join(', ')}` : 'No selection';
        } else if (cfg.inputType === 'select' || cfg.inputType === 'radio') {
          const option = (cfg.options || []).find(o => o.value === state.value);
          content = option ? `Selected: ${option.label}` : 'No selection';
        } else if (cfg.inputType === 'checkbox') {
          content = state.value ? (cfg.label || 'Checked') : (cfg.label ? `${cfg.label} (unchecked)` : 'Unchecked');
        }

        if (content) {
          context.setMessages(prev => ([
            ...prev,
            {
              id: `user-${Date.now()}`,
              role: 'user',
              content,
              timestamp: new Date()
            }
          ]));
        }
        onComplete(result.data);
      } else {
        onError(result.error || new Error('Execution failed'));
      }
    } catch (error) {
      onError(error as Error);
    }
  }, [brick, onComplete, onError, context, state.value]);

  const renderInput = () => {
    const { inputType, placeholder, label, options, accept, multiple, maxFiles } = brick.config;

    switch (inputType) {
      case 'text':
        return (
          <Textarea
            value={state.value}
            onChange={(e) => handleValueChange(e.target.value)}
            onBlur={handleBlur}
            placeholder={placeholder}
            disabled={state.loading}
            className={state.error ? 'border-destructive' : ''}
          />
        );

      case 'file':
        return (
          <div className="space-y-2">
            <input
              type="file"
              accept={accept}
              multiple={multiple}
              onChange={(e) => {
                if (e.target.files) {
                  const files = Array.from(e.target.files);
                  if (maxFiles && files.length > maxFiles) {
                    brick.getActions().setError(`Maximum ${maxFiles} files allowed`);
                    return;
                  }
                  handleValueChange(multiple ? files : files[0]);
                }
              }}
              onBlur={handleBlur}
              disabled={state.loading}
              className="hidden"
              id={`file-input-${brick.id}`}
            />
            <Button
              type="button"
              variant="outline"
              onClick={() => document.getElementById(`file-input-${brick.id}`)?.click()}
              disabled={state.loading}
            >
              <Upload className="w-4 h-4 mr-2" />
              Choose Files
            </Button>
            {state.value && (
              <div className="text-sm text-muted-foreground">
                {Array.isArray(state.value) 
                  ? `${state.value.length} file(s) selected`
                  : `Selected: ${state.value.name}`
                }
              </div>
            )}
          </div>
        );

      case 'select':
        return (
          <Select
            value={state.value}
            onValueChange={handleValueChange}
            disabled={state.loading}
          >
            <SelectTrigger className={state.error ? 'border-destructive' : ''}>
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent>
              {options?.map((option, index) => (
                <SelectItem 
                  key={index} 
                  value={option.value} 
                  disabled={option.disabled}
                >
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case 'multiselect':
        return (
          <div className="space-y-2">
            {options?.map((option, index) => (
              <div key={index} className="flex items-center space-x-2">
                <Checkbox
                  id={`${brick.id}-${index}`}
                  checked={Array.isArray(state.value) && state.value.includes(option.value)}
                  onCheckedChange={(checked) => {
                    const currentValues = Array.isArray(state.value) ? state.value : [];
                    if (checked) {
                      handleValueChange([...currentValues, option.value]);
                    } else {
                      handleValueChange(currentValues.filter(v => v !== option.value));
                    }
                  }}
                  disabled={state.loading || option.disabled}
                />
                <Label htmlFor={`${brick.id}-${index}`}>{option.label}</Label>
              </div>
            ))}
          </div>
        );

      case 'checkbox':
        return (
          <div className="flex items-center space-x-2">
            <Checkbox
              id={brick.id}
              checked={state.value}
              onCheckedChange={handleValueChange}
              disabled={state.loading}
            />
            <Label htmlFor={brick.id}>{label}</Label>
          </div>
        );

      case 'radio':
        return (
          <RadioGroup
            value={state.value}
            onValueChange={handleValueChange}
            disabled={state.loading}
          >
            {options?.map((option, index) => (
              <div key={index} className="flex items-center space-x-2">
                <RadioGroupItem
                  value={option.value}
                  id={`${brick.id}-${index}`}
                  disabled={option.disabled}
                />
                <Label htmlFor={`${brick.id}-${index}`}>{option.label}</Label>
              </div>
            ))}
          </RadioGroup>
        );

      default:
        return (
          <Input
            value={state.value}
            onChange={(e) => handleValueChange(e.target.value)}
            onBlur={handleBlur}
            placeholder={placeholder}
            disabled={state.loading}
            className={state.error ? 'border-destructive' : ''}
          />
        );
    }
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-card">
      <div className="space-y-2">
        {brick.config.label && (
          <Label className="text-sm font-medium">
            {brick.config.label}
            {brick.config.validation?.required && <span className="text-destructive ml-1">*</span>}
          </Label>
        )}
        
        {renderInput()}
        
        {state.error && (
          <div className="flex items-center gap-2 text-sm text-destructive">
            <AlertCircle className="w-4 h-4" />
            <span>{state.error}</span>
          </div>
        )}
        
        <div className="flex justify-end">
          <Button
            onClick={handleSubmit}
            disabled={state.loading || !state.valid}
            className="min-w-[100px]"
          >
            {state.loading ? 'Processing...' : 'Submit'}
          </Button>
        </div>
      </div>
    </div>
  );
};
