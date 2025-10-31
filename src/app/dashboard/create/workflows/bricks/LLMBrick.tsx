"use client";

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { 
  BrickConfig, 
  BrickContext, 
  BrickInstance, 
  BrickExecutionResult,
  LLMBrickConfig,
  LLMBrickState,
  LLMBrickActions
} from '@/types/bricks';
import { brickEventEmitter } from './BrickEventEmitter';
import { brickErrorHandler } from './BrickError';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Paperclip, Send, Edit2, Check, X } from 'lucide-react';

export class LLMBrick implements BrickInstance {
  public id: string;
  public type: string = 'llm';
  public config: LLMBrickConfig;
  public context: BrickContext;
  private state: LLMBrickState;
  private actions: LLMBrickActions;

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as LLMBrickConfig;
    this.context = context;
    this.state = {
      prompt: '',
      isEditing: false,
      selectedButton: undefined,
      files: []
    };
    this.actions = this.createActions();
    
    // Listen for button clicks from engine
    this.config.buttons?.forEach(btn => {
      brickEventEmitter.on(`button:${this.id}:${btn.action}`, () => {
        this.handleButtonClick(btn.action);
      });
    });
  }

  private createActions(): LLMBrickActions {
    return {
      setPrompt: (prompt: string) => {
        this.state.prompt = prompt;
        this.emitStateChange();
      },
      startEditing: () => {
        this.state.isEditing = true;
        this.emitStateChange();
      },
      stopEditing: () => {
        this.state.isEditing = false;
        this.emitStateChange();
      },
      confirmEdit: () => {
        this.state.isEditing = false;
        this.emitStateChange();
        this.handleButtonClick('confirm_edit');
      },
      cancelEdit: () => {
        this.state.isEditing = false;
        this.emitStateChange();
      },
      selectButton: (buttonId: string) => {
        this.state.selectedButton = buttonId;
        this.emitStateChange();
      },
      addFiles: (files: File[]) => {
        this.state.files = [...this.state.files, ...files];
        this.emitStateChange();
      },
      removeFile: (index: number) => {
        this.state.files = this.state.files.filter((_, i) => i !== index);
        this.emitStateChange();
      },
      clearFiles: () => {
        this.state.files = [];
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

  private handleButtonClick(buttonId: string): void {
    const button = this.config.buttons.find(btn => btn.action === buttonId);
    if (!button) {
      console.warn(`Button with action '${buttonId}' not found`);
      return;
    }

    try {
      // Update context with button action
      this.context.setData(prev => ({
        ...prev,
        [this.id]: {
          action: buttonId,
          returnValue: button.returnValue,
          prompt: this.state.prompt,
          files: this.state.files
        }
      }));

      // Navigate to nextStep if configured
      if ((button as any).nextStep) {
        this.context.setStep((button as any).nextStep);
      }

      // Emit completion event with user message data for engine to process
      brickEventEmitter.emitComplete(this.id, undefined, {
        action: buttonId,
        returnValue: button.returnValue,
        prompt: this.state.prompt,
        files: this.state.files,
        userMessage: button.userMessage, // Engine will inject this
        nextStep: (button as any).nextStep
      });

    } catch (error) {
      const brickError = brickErrorHandler.handleError(
        error as Error,
        this.id,
        this.type,
        { buttonId, config: this.config }
      );
      brickEventEmitter.emitError(this.id, undefined, brickError);
    }
  }

  public async execute(): Promise<BrickExecutionResult> {
    try {
      // LLM bricks don't execute automatically - they wait for user interaction
      brickEventEmitter.emitStatus(this.id, undefined, 'waiting_for_input');
      
      // Prepare assistant message if configured
      const cfg: any = this.config as any;
      const assistantMessage = cfg.assistantMessage?.content
        || this.config.prompt?.placeholder
        || null;

      const actionButtons = Array.isArray(cfg.buttons)
        ? cfg.buttons.map((btn: any) => ({
            label: btn.label,
            variant: btn.variant || 'default',
            action: btn.action
          }))
        : undefined;

      return {
        success: true,
        data: {
          type: 'llm_brick_ready',
          state: this.state,
          config: this.config,
          // Return message data for engine to process
          message: assistantMessage ? {
            role: 'assistant',
            content: assistantMessage,
            actionButtons,
            enableFileInput: cfg.assistantMessage?.enableFileInput,
            enablePromptInput: cfg.assistantMessage?.enablePromptInput,
            showDelay: cfg.assistantMessage?.showDelay ?? 1000
          } : null
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
    if (this.config.activatePrompt && this.state.prompt.trim().length === 0) {
      return 'Prompt is required';
    }

    if (this.config.activateFileUpload && this.state.files.length === 0) {
      return 'Files are required';
    }

    return true;
  }

  public reset(): void {
    this.state = {
      prompt: '',
      isEditing: false,
      selectedButton: undefined,
      files: []
    };
    this.emitStateChange();
  }

  public destroy(): void {
    // Cleanup if needed
    this.state = {
      prompt: '',
      isEditing: false,
      selectedButton: undefined,
      files: []
    };
  }

  public getState(): LLMBrickState {
    return { ...this.state };
  }

  public getActions(): LLMBrickActions {
    return this.actions;
  }

  public triggerButtonClick(buttonId: string): void {
    this.handleButtonClick(buttonId);
  }
}

export const LLMBrickComponent: React.FC<{
  brick: LLMBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [state, setState] = useState<LLMBrickState>(brick.getState());
  const [isLoading, setIsLoading] = useState(false);
  const initializedRef = useRef(false);
  const handleButtonClickRef = useRef<((buttonId: string) => Promise<void>) | null>(null);

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

  const handleButtonClick = useCallback(async (buttonId: string) => {
    setIsLoading(true);
    try {
      brick.getActions().selectButton(buttonId);
      const clicked = brick.config.buttons?.find(btn => btn.action === buttonId);
      
      // Save prompt input from chat to workflowData.userInput if it exists
      const chatPrompt = context.prompt?.trim();
      if (chatPrompt) {
        brick.context.setData((prev: any) => ({
          ...prev,
          userInput: chatPrompt
        }));
        // Clear the prompt input after saving
        context.setPrompt("");
      }
      
      // Show user message BEFORE opening modal (for buttons with userMessage or chat input)
      const hasModal = !!(clicked as any)?.modal;
      const userMessageText = chatPrompt || clicked?.userMessage;
      
      if (userMessageText) {
        context.setMessages(prev => ([
          ...prev,
          {
            id: `user-${Date.now()}`,
            role: 'user',
            content: userMessageText,
            timestamp: new Date()
          }
        ]));
      }
      
      let overlayResult: any = null;
      
      if (hasModal) {
        // Resolve template variables in modalProps
        const rawModalProps = (clicked as any).modalProps || {};
        const resolvedModalProps: any = {};
        
        for (const [key, value] of Object.entries(rawModalProps)) {
          if (typeof value === 'string' && value.includes('{{')) {
            // Template interpolation
            resolvedModalProps[key] = value.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
              const cleanPath = path.trim().replace(/^workflowData\./, '');
              const keys = cleanPath.split('.');
              let resolvedValue: any = brick.context.workflowData;
              
              for (const k of keys) {
                if (resolvedValue && typeof resolvedValue === 'object' && k in resolvedValue) {
                  resolvedValue = resolvedValue[k];
                } else {
                  return match; // Keep original if path not found
                }
              }
              
              return String(resolvedValue);
            });
          } else {
            resolvedModalProps[key] = value;
          }
        }
        
        console.log('🎭 Opening modal:', (clicked as any).modal, 'with resolved props:', resolvedModalProps);
        const { brickEventEmitter } = await import('./BrickEventEmitter');
        try {
          overlayResult = await brickEventEmitter.requestOverlay((clicked as any).modal, resolvedModalProps);
          console.log('✅ Modal resolved with:', overlayResult);
          
          if (overlayResult?.validated) {
            const promptValue = overlayResult?.prompt || overlayResult?.value;
            if (promptValue) {
              brick.context.setData((prev: any) => ({
                ...prev,
                musicDescription: promptValue
              }));
              
              brick.getActions().setPrompt(promptValue);
            }
          }
        } catch (error) {
          console.log('Modal cancelled or error:', error);
          setIsLoading(false);
          return;
        }
      }
      
      brick.triggerButtonClick(buttonId);
      const finalPrompt = overlayResult?.validated 
        ? (overlayResult?.prompt || overlayResult?.value || state.prompt)
        : (chatPrompt || state.prompt);
      
      // Trigger brick if configured
      if ((clicked as any)?.triggerBrick) {
        const { brickEventEmitter } = await import('./BrickEventEmitter');
        brickEventEmitter.emit(`trigger:${(clicked as any).triggerBrick}`, {});
      }
      
      onComplete({
        action: buttonId,
        returnValue: brick.config.buttons.find(btn => btn.action === buttonId)?.returnValue,
        prompt: finalPrompt,
        files: state.files,
        overlayResult: overlayResult
      });
    } catch (error) {
      onError(error as Error);
    } finally {
      setIsLoading(false);
    }
  }, [brick, state.prompt, state.files, onComplete, onError, context]);

  handleButtonClickRef.current = handleButtonClick;

  const handlePromptChange = useCallback((prompt: string) => {
    brick.getActions().setPrompt(prompt);
  }, [brick]);

  const handleFileUpload = useCallback((files: File[]) => {
    brick.getActions().addFiles(files);
  }, [brick]);

  const handleRemoveFile = useCallback((index: number) => {
    brick.getActions().removeFile(index);
  }, [brick]);

  const handleEditToggle = useCallback(() => {
    if (state.isEditing) {
      brick.getActions().confirmEdit();
    } else {
      brick.getActions().startEditing();
    }
  }, [brick, state.isEditing]);

  const handleCancelEdit = useCallback(() => {
    brick.getActions().cancelEdit();
  }, [brick]);

  // LLM bricks don't render UI - engine handles message injection
  return null;
};
