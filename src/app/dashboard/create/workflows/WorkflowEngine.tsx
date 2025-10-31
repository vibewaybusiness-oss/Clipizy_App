"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { WorkflowContext, WorkflowConfig, WorkflowStep, WorkflowHelpers } from '@/types/workflow';
import { BrickConfig, BrickContext, BrickInstance, BrickExecutionResult } from '@/types/bricks';
import { brickFactory } from './bricks/BrickFactory';
import { brickEventEmitter } from './bricks/BrickEventEmitter';
import { workflowLoader } from './utils/workflowLoader';
import { projectsAPI } from "@/lib/api/projects";

interface UseWorkflowEngineOptions<TData extends Record<string, any>> {
  context: WorkflowContext;
  config: WorkflowConfig | string;
  autoSaveFn?: (projectId: string, data: any) => Promise<void>;
  loadStateFn?: (projectId: string) => Promise<any>;
  enabled?: boolean;
}

interface UseWorkflowEngineReturn<TData extends Record<string, any>> {
  workflowData: TData;
  helpers: WorkflowHelpers;
  currentStep: string;
  currentStepConfig: WorkflowStep | null;
  activeBricks: Map<string, BrickInstance>;
  handleProjectSelect: (projectType?: string) => void;
  handleUserInput: (input: string) => void;
  handleFileUpload: (files: File[]) => void;
  handleBrickAction: (brickId: string, action: string, data: any) => void;
  handleBrickComplete: (brickId: string, result: any) => void;
  handleBrickError: (brickId: string, error: Error) => void;
  renderModals: () => React.ReactNode;
}

export function useWorkflowEngine<TData extends Record<string, any>>({
  context,
  config: configOrPath,
  autoSaveFn,
  loadStateFn,
  enabled = true
}: UseWorkflowEngineOptions<TData>): UseWorkflowEngineReturn<TData> {
  const [workflowConfig, setWorkflowConfig] = useState<WorkflowConfig | null>(null);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [workflowData, setWorkflowData] = useState<TData>({} as TData);
  const [activeBricks, setActiveBricks] = useState<Map<string, BrickInstance>>(new Map());
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isInitializedRef = useRef(false);
  const isLoadingStateRef = useRef(false);
  const isStartingRef = useRef(false);
  const brickEventSubscriptionsRef = useRef<string[]>([]);
  const executedStepsRef = useRef<Set<string>>(new Set());
  const lastExecutedStepRef = useRef<string>('');

  useEffect(() => {
    if (!enabled) {
      return;
    }
    const loadConfig = async () => {
      // debug: disabled verbose log
      executedStepsRef.current.clear();
    lastExecutedStepRef.current = '';
      if (typeof configOrPath === 'string') {
        try {
          const loadedConfig = await workflowLoader.loadFromJSON(configOrPath);
          // debug: disabled verbose log
          setWorkflowConfig(loadedConfig);
          setCurrentStep(loadedConfig.initialStep);
        } catch (error) {
          console.error('❌ Failed to load workflow config:', error);
          context.toast({
            title: 'Workflow Error',
            description: 'Failed to load workflow configuration',
            variant: 'destructive'
          });
        }
      } else {
        // debug: disabled verbose log
        setWorkflowConfig(configOrPath);
        setCurrentStep(configOrPath.initialStep);
      }
    };

    loadConfig();
  }, [configOrPath, enabled]);

  useEffect(() => {
    if (!workflowConfig || !context.projectId || !loadStateFn || isLoadingStateRef.current || isInitializedRef.current) {
      return;
    }
    
    const loadProjectState = async () => {
      isLoadingStateRef.current = true;
      
      try {
        const savedState = await loadStateFn(context.projectId!);
        
        if (savedState && typeof savedState === 'object') {
          const { currentStep: savedStep, chat: savedChat, ...restOfData } = savedState as any;
          
          setWorkflowData(restOfData as TData);
          
          if (savedChat && Array.isArray(savedChat) && savedChat.length > 0 && context.messages.length === 0) {
            const restoredMessages = savedChat.map((msg: any) => ({
              id: msg.id,
              role: msg.role,
              content: msg.content,
              timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
              files: msg.files,
              actionButtons: msg.actionButtons
            }));
            
            context.setMessages(prev => [...prev, ...restoredMessages]);
          }
          
          isInitializedRef.current = true;
          
          if (savedStep && workflowConfig.steps[savedStep]) {
            await new Promise(resolve => setTimeout(resolve, 100));
            setCurrentStep(savedStep);
          }
        }
      } catch (error) {
        console.error('Failed to load project state:', error);
      } finally {
        isLoadingStateRef.current = false;
      }
    };
    
    loadProjectState();
  }, [workflowConfig, context.projectId, loadStateFn]);



  const saveState = useCallback(async (projectId: string | null | undefined) => {
    if (!projectId || !autoSaveFn || !workflowConfig) return;
    
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
    
    saveTimeoutRef.current = setTimeout(async () => {
      try {
        const serializedMessages = context.messages.map(msg => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp.toISOString(),
          files: msg.files,
          actionButtons: msg.actionButtons
        }));
        
        const serializedWorkflowData = { ...workflowData };
        
        const serializedData = {
          projectType: workflowConfig.id,
          projectData: {
            settings: {
              ...serializedWorkflowData,
              currentStep,
              chat: serializedMessages
            },
            analysis: null
          }
        };
        
        await autoSaveFn(projectId, serializedData);
      } catch (error) {
        console.error('Failed to save workflow state:', error);
        context.toast({
          title: 'Save failed',
          description: error instanceof Error ? error.message : 'Failed to save workflow state',
          variant: 'destructive'
        });
      }
    }, 500);
  }, [workflowData, currentStep, autoSaveFn, context.messages, context.toast, workflowConfig]);

  


  const handleBrickCompleteCallback = useCallback((brickId: string, result: BrickExecutionResult) => {
    // debug: disabled verbose log
    if (!workflowConfig || !result.success) return;

    const step = workflowConfig.steps[currentStep];
    if (!step) return;

    // Engine processes brick output
    const data: any = (result as any).data || {};
    
    // Inject user message if brick returned one
    if (data.userMessage) {
      context.setMessages(prev => ([
        ...prev,
        {
          id: `user-${Date.now()}`,
          role: 'user',
          content: data.userMessage,
          timestamp: new Date()
        }
      ]));
    }

    // Decision routing based on LLM returnValue when provided
    let nextStep: string | undefined;

    if (data && typeof data.returnValue !== 'undefined') {
      const decisionMap: Record<string, Record<string, string>> = {
        track_input: {
          ai_generation: 'track_ai_description'
        },
        track_ai_lyrics: {
          skip: 'track_generating'
        },
        reference_images: {
          skip: 'reference_image_description'
        },
        reference_image_description: {
          ai_description: 'video_styles'
        },
        video_description: {
          ai_description: 'reference_images'
        }
      };
      const stepMap = decisionMap[currentStep] || {};
      nextStep = stepMap[String(data.returnValue)];
    }

    if (!nextStep) {
      nextStep = typeof step.nextStep === 'function'
        ? (step.nextStep as any)(workflowData)
        : step.nextStep;
    }

    // debug: disabled verbose log
    if (nextStep && workflowConfig.steps[nextStep]) {
      // debug: disabled verbose log
      setStepInternal(nextStep);
    } else {
      // debug: disabled verbose log
    }
  }, [workflowConfig, currentStep, workflowData]);

  const setStepInternal = useCallback(async (stepId: string) => {
    if (!workflowConfig || !workflowConfig.steps[stepId]) {
      console.error(`Step ${stepId} not found`);
      return;
    }

    brickEventSubscriptionsRef.current.forEach(subId => {
      brickEventEmitter.offById(subId);
    });
    brickEventSubscriptionsRef.current = [];

    activeBricks.forEach(brick => {
      if (brick && typeof brick.destroy === 'function') {
        brick.destroy();
      }
    });
    activeBricks.clear();
    setActiveBricks(new Map());

    // Clear execution tracking for the step when changing
    const executionKey = `${stepId}-${workflowConfig?.id || 'default'}`;
    executedStepsRef.current.delete(executionKey);

    setCurrentStep(stepId);

    if (context.projectId) {
      await saveState(context.projectId);
    }
  }, [workflowConfig, context.projectId, saveState]);

  const createBrickContext = useCallback((): BrickContext => {
    return {
      workflowData,
      setData: setWorkflowData,
      setStep: setStepInternal,
      saveState,
      toast: context.toast,
      projectId: context.projectId || undefined
    };
  }, [workflowData, context.toast, context.projectId, saveState, setStepInternal]);

  const handleProjectSelect = useCallback(async (projectType?: string) => {
    // debug: disabled verbose log
    
    executedStepsRef.current.clear();
    lastExecutedStepRef.current = '';
    
    // If a project already exists, just start the workflow
    if (context.projectId) {
      // debug: disabled verbose log
      return;
    }

    // Prevent double-starts
    if (isStartingRef.current) {
      console.log('⏳ Project creation already in progress, ignoring duplicate request');
      return;
    }
    isStartingRef.current = true;

    if (!workflowConfig && !projectType) return;

    try {
      // Map frontend project types to API-supported types
      const projectTypeMapping: Record<string, string> = {
        'music_video_clip': 'music-clip',
        'video_clip': 'video-edit',
        'audio_clip': 'audio-edit',
        'image_clip': 'image-edit',
        'custom': 'custom'
      };

      const apiProjectType = projectTypeMapping[projectType || workflowConfig?.id || ''] || 'custom';
      
      const projectData = {
        name: workflowConfig?.name || `${apiProjectType} Project`,
        type: apiProjectType as any,
        description: workflowConfig?.description || `Create a ${apiProjectType} project`,
        ...workflowData
      };

      const result = await projectsAPI.createProject(projectData);
      
      if (result && result.id) {
        context.setProjectId?.(result.id);
        context.toast?.({
          title: 'Project Created',
          description: 'Your project has been created successfully',
          variant: 'default'
        });
      } else {
        throw new Error('Failed to create project');
      }
    } catch (error) {
      console.error('Failed to create project:', error);
      context.toast({
        title: 'Project Creation Failed',
        description: error instanceof Error ? error.message : 'Failed to create project',
        variant: 'destructive'
      });
    }
    finally {
      isStartingRef.current = false;
    }
  }, [workflowConfig, workflowData, context, context.projectId]);

  const handleUserInput = useCallback((input: string) => {
    const hasFiles = context.uploadedImages.length > 0 || context.uploadedAudio.length > 0;
    
    if (!input.trim() && !hasFiles) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user' as const,
      content: input || (hasFiles ? `Uploaded ${context.uploadedImages.length + context.uploadedAudio.length} file(s)` : ''),
      timestamp: new Date(),
      files: hasFiles ? {
        images: [...context.uploadedImages],
        audio: [...context.uploadedAudio]
      } : undefined
    };

    context.setMessages(prev => [...prev, userMessage]);

    setWorkflowData(prev => {
      const updated: any = {
        ...prev,
        userInput: input || userMessage.content,
        uploadedFiles: hasFiles ? [...context.uploadedImages, ...context.uploadedAudio] : prev.uploadedFiles
      };
      
      return updated as TData;
    });

    context.setUploadedImages(() => []);
    context.setUploadedAudio(() => []);

    if (context.projectId) {
      saveState(context.projectId);
    }
  }, [context, saveState, currentStep, workflowConfig, setStepInternal]);

  const handleFileUpload = useCallback((files: File[]) => {
    if (!files.length) return;

    const imageFiles = files.filter(f => f.type.startsWith('image/'));
    const audioFiles = files.filter(f => f.type.startsWith('audio/'));

    if (imageFiles.length > 0) {
      context.setUploadedImages(prev => [...prev, ...imageFiles]);
    }
    if (audioFiles.length > 0) {
      context.setUploadedAudio(prev => [...prev, ...audioFiles]);
    }

    setWorkflowData(prev => ({
      ...prev,
      uploadedFiles: files
    }));
  }, [context]);

  const handleBrickAction = useCallback((brickId: string, action: string, data: any) => {
    const brick = activeBricks.get(brickId);
    if (brick && typeof (brick as any).handleAction === 'function') {
      (brick as any).handleAction(action, data);
    }
  }, [activeBricks]);

  const handleBrickComplete = useCallback((brickId: string, result: any) => {
    console.log(`Brick ${brickId} completed:`, result);
    
    const normalized: BrickExecutionResult = (result && typeof result.success === 'boolean')
      ? result
      : { success: true, data: result } as BrickExecutionResult;
    
    handleBrickCompleteCallback(brickId, normalized);
    
    if (context.projectId) {
      saveState(context.projectId);
    }
  }, [context.projectId, saveState, handleBrickCompleteCallback]);

  const handleBrickError = useCallback((brickId: string, error: Error) => {
    console.error(`Brick ${brickId} error:`, error);
    
    context.toast({
      title: 'Brick Error',
      description: error.message,
      variant: 'destructive'
    });
  }, [context]);

  const renderModals = useCallback(() => {
    return null;
  }, []);

  const helpers: WorkflowHelpers = {
    setData: setWorkflowData,
    setStep: setStepInternal,
    saveState,
    toast: context.toast,
    projectId: context.projectId
  };

  const currentStepConfig = workflowConfig?.steps[currentStep] || null;

  const executeStep = useCallback(async (stepId: string) => {
    if (!workflowConfig) {
      // debug: disabled verbose log
      return;
    }

    // Use workflow ID in execution key to prevent cross-workflow conflicts
    const executionKey = `${stepId}-${workflowConfig.id || 'default'}`;
    if (executedStepsRef.current.has(executionKey)) {
      // debug: disabled verbose log
      return;
    }

    const step = workflowConfig.steps[stepId];
    if (!step) {
      console.error('❌ Step not found:', stepId);
      return;
    }

    // debug: disabled verbose log
    executedStepsRef.current.add(executionKey);

    try {
      const brickContext = createBrickContext();
      const bricks: BrickInstance[] = [];

      if (!step.bricks || !Array.isArray(step.bricks)) {
        console.warn('⚠️ Step has no bricks defined:', stepId);
        return;
      }

      for (const brickConfig of step.bricks) {
        try {
          // debug: disabled verbose log
          const brick = await brickFactory.create(brickConfig, brickContext);
          // debug: disabled verbose log
          bricks.push(brick);
          activeBricks.set(brick.id, brick);
        } catch (error) {
          console.error(`❌ Failed to create brick ${brickConfig.id}:`, error);
          context.toast({
            title: 'Brick Error',
            description: `Failed to create brick: ${brickConfig.id}`,
            variant: 'destructive'
          });
        }
      }
    
      setActiveBricks(new Map(activeBricks));

      const subscriptions: string[] = [];

      bricks.forEach(brick => {
        const subscriptionId = brickEventEmitter.on(`complete:${brick.id}`, async (result: any) => {
          const normalized: BrickExecutionResult = (result && typeof result.success === 'boolean')
            ? result
            : { success: true, data: result } as BrickExecutionResult;
          handleBrickCompleteCallback(brick.id, normalized);
        });

        subscriptions.push(subscriptionId);

        const errorSubscriptionId = brickEventEmitter.on(`error:${brick.id}`, (error: Error | string) => {
          const errorMessage = error instanceof Error ? error.message : (typeof error === 'string' ? error : 'Unknown error');
          context.toast({
            title: 'Brick Error',
            description: errorMessage,
            variant: 'destructive'
          });
        });

        subscriptions.push(errorSubscriptionId);

        // Listen for trigger events
        const triggerSubscriptionId = brickEventEmitter.on(`trigger:${brick.id}`, async () => {
          if (typeof (brick as any).trigger === 'function') {
            await (brick as any).trigger();
          }
        });

        subscriptions.push(triggerSubscriptionId);
      });

      brickEventSubscriptionsRef.current.push(...subscriptions);

      const backgroundBricks = bricks.filter(b => b.type === 'background');
      const userInputBricks = bricks.filter(b => b.type === 'user_input');
      const llmBricks = bricks.filter(b => b.type === 'llm');
      const otherBricks = bricks.filter(b => b.type !== 'background' && b.type !== 'user_input' && b.type !== 'llm');

      if (step.bricks.length > 0) {

        // Execute non-user-input bricks immediately
        for (const brick of otherBricks) {
          try {
            // debug: disabled verbose log
            await brick.execute();
            // debug: disabled verbose log
          } catch (error) {
            console.error(`Failed to execute brick ${brick.id}:`, error);
          }
        }

        // Execute LLM bricks and process their message output
        // Track processed bricks to prevent duplicate messages
        const processedBricks = new Set<string>();
        
        for (const brick of llmBricks) {
          // Prevent duplicate brick execution
          if (processedBricks.has(brick.id)) {
            continue;
          }
          processedBricks.add(brick.id);
          
          try {
            const result = await brick.execute();
            
            // Engine processes brick output and injects messages
            if (result.success && result.data?.message) {
              const messageData = result.data.message;
              
              // Convert action buttons to proper format with onClick handlers
              const actionButtons = messageData.actionButtons?.map((btn: any) => ({
                label: btn.label,
                variant: btn.variant || 'default',
                onClick: () => {
                  // Emit button click event to the brick
                  brickEventEmitter.emit(`button:${brick.id}:${btn.action}`, {});
                }
              }));

              // Engine injects the message (deduplication handled in addAssistantMessageWithDelay)
              context.addAssistantMessageWithDelay({
                role: 'assistant',
                content: messageData.content,
                actionButtons,
                enableFileInput: messageData.enableFileInput,
                enablePromptInput: messageData.enablePromptInput
              }, messageData.showDelay || 1000);
            }
          } catch (error) {
            console.error(`Failed to initialize LLM brick ${brick.id}:`, error);
          }
        }

        // Execute background bricks asynchronously without blocking
        // debug: disabled verbose log
        backgroundBricks.forEach(() => {});

        const backgroundPromises = backgroundBricks
          .filter(brick => brick.type === 'background')
          .map(async (brick) => {
            const bgConfig = brick.config as any;
            // debug: disabled verbose log
            
            if (bgConfig.trigger === 'immediate' || bgConfig.trigger === 'on_step_enter') {
              // debug: disabled verbose log
              try {
                const result = await brick.execute();
                // debug: disabled verbose log
                return { brickId: brick.id, success: true, result };
              } catch (error) {
                console.error(`❌ Background brick ${brick.id} failed:`, error);
                return { brickId: brick.id, success: false, error };
              }
            } else {
              // debug: disabled verbose log
              return { brickId: brick.id, success: true, result: 'skipped' };
            }
          });

        // Don't await background bricks - let them run in parallel
        Promise.all(backgroundPromises).then(results => {
          // debug: disabled verbose log
        });
      }

      const hasLLMWithMessage = step.bricks.some((brickConfig: any) => {
        if (brickConfig.type !== 'llm') return false;
        return brickConfig.assistantMessage?.content || brickConfig.prompt?.placeholder;
      });

      if (step.assistantMessage && !hasLLMWithMessage) {
        const content = typeof step.assistantMessage.content === 'function'
          ? step.assistantMessage.content(workflowData)
          : step.assistantMessage.content;

        const delay = step.assistantMessage.showDelay || 0;

        if (content && content.trim() !== '') {
          context.addAssistantMessageWithDelay({
            role: 'assistant',
            content,
            enableFileInput: step.assistantMessage.enableFileInput,
            enablePromptInput: step.assistantMessage.enablePromptInput
          }, delay);
        }
      }

      if (step.autoSave && context.projectId) {
        await saveState(context.projectId);
      }

      // Auto-progress to next step if no user interaction is required
      // or if this is just a setup step
      const requiresUserInteraction = userInputBricks.length > 0 || llmBricks.length > 0;
      if (!requiresUserInteraction) {
        // debug: disabled verbose log
        setTimeout(() => {
          const nextStep = typeof step.nextStep === 'function'
            ? step.nextStep(workflowData)
            : step.nextStep;

          if (nextStep && workflowConfig.steps[nextStep]) {
            // debug: disabled verbose log
            setStepInternal(nextStep);
          } else {
            // debug: disabled verbose log
          }
        }, 1000); // Small delay to ensure UI is rendered
      } else {
        // debug: disabled verbose log
      }

    } catch (error) {
      console.error('Failed to execute step:', error);
      context.toast({
        title: 'Step Error',
        description: error instanceof Error ? error.message : 'Failed to execute step',
        variant: 'destructive'
      });
    }
  }, [workflowConfig, workflowData, createBrickContext, context, saveState, activeBricks, currentStep, handleBrickCompleteCallback, setStepInternal]);

  useEffect(() => {
    if (!enabled || !workflowConfig || !currentStep) return;
    
    // Prevent duplicate execution - check both execution tracking AND last executed step
    const executionKey = `${currentStep}-${workflowConfig.id || 'default'}`;
    const fullKey = `${executionKey}-${workflowConfig.id}`;
    
    // Skip if already executed or if we're re-executing the same step
    if (executedStepsRef.current.has(executionKey) || lastExecutedStepRef.current === fullKey) {
      return;
    }
    
    lastExecutedStepRef.current = fullKey;
    executeStep(currentStep);
  }, [enabled, workflowConfig?.id, currentStep]); // Removed executeStep from dependencies to prevent loops

  return {
    workflowData,
    helpers,
    currentStep,
    currentStepConfig,
    activeBricks,
    handleProjectSelect,
    handleUserInput,
    handleFileUpload,
    handleBrickAction,
    handleBrickComplete,
    handleBrickError,
    renderModals
  };
}