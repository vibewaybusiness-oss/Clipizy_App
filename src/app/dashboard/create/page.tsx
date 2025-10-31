"use client";

import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useToast } from "@/hooks/ui/use-toast";
import { useWorkflowEngine, ProjectType } from "./workflows";
import type { Message } from "@/types/workflow";
import { WorkflowUI } from "./workflows/WorkflowUI";
import { ProjectType as ApiProjectType } from "@/types/projects";


export default function CreatePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { toast } = useToast();
  const [prompt, setPrompt] = useState("");
  const [uploadedImages, setUploadedImages] = useState<File[]>([]);
  const [uploadedAudio, setUploadedAudio] = useState<File[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [selectedProjectType, setSelectedProjectType] = useState<ProjectType | null>(null);
  const [inputEnabled, setInputEnabled] = useState(false);
  const [fileInputEnabled, setFileInputEnabled] = useState(false);
  const [showProjectTypeCards, setShowProjectTypeCards] = useState(false);
  const [hoveredCardId, setHoveredCardId] = useState<string | null>(null);
  const [isThinking, setIsThinking] = useState(false);
  const [projectId, setProjectId] = useState<string | null>(null);
  
  // Unique message ID generator with counter to prevent duplicates
  const messageIdCounterRef = useRef(0);
  const generateUniqueMessageId = useCallback((prefix: string = 'assistant') => {
    messageIdCounterRef.current += 1;
    return `${prefix}-${Date.now()}-${messageIdCounterRef.current}-${Math.random().toString(36).substring(2, 9)}`;
  }, []);

  const addAssistantMessageWithDelay = useCallback((message: Omit<Message, 'id' | 'timestamp'>, delay: number = 1000 + Math.random() * 500) => {
    setIsThinking(true);
    setTimeout(() => {
      // Deduplicate: Check if message with same content already exists
      setMessages(prev => {
        const messageExists = prev.some(
          msg => msg.role === 'assistant' && 
          msg.content === message.content &&
          (msg.actionButtons?.length || 0) === (message.actionButtons?.length || 0)
        );
        
        if (messageExists) {
          return prev; // Don't add duplicate
        }
        
        const fullMessage: Message = {
          ...message,
          id: generateUniqueMessageId('assistant'),
          timestamp: new Date()
        };
        return [...prev, fullMessage];
      });
      
      if (message.enableFileInput !== undefined) {
        setFileInputEnabled(message.enableFileInput);
      }
      if (message.enablePromptInput !== undefined) {
        setInputEnabled(message.enablePromptInput);
      }
      
      setIsThinking(false);
    }, delay);
  }, []);

  const workflowContext = useMemo(() => ({
    messages,
    setMessages,
    inputEnabled,
    setInputEnabled,
    fileInputEnabled,
    setFileInputEnabled,
    prompt,
    setPrompt,
    uploadedImages,
    setUploadedImages,
    uploadedAudio,
    setUploadedAudio,
    toast,
    fileInputRef,
    isGenerating,
    setIsGenerating,
    addAssistantMessageWithDelay,
    projectId,
    setProjectId
  }), [messages, inputEnabled, fileInputEnabled, prompt, uploadedImages, uploadedAudio, isGenerating, toast, addAssistantMessageWithDelay, projectId]);
  
  // Map project type to workflow ID
  const workflowId = useMemo(() => {
    if (!selectedProjectType) return null;
    const projectTypeToWorkflowId: Record<ProjectType, string> = {
      music_video_clip: "music-clip-workflow",
      video_clip: "video-clip-workflow",
      business_ad: "business-ad-workflow",
      automate_workflow: "automate-workflow",
    };
    return projectTypeToWorkflowId[selectedProjectType];
  }, [selectedProjectType]);

  // Load only the selected workflow engine
  const workflowEngine = useWorkflowEngine({ 
    context: workflowContext, 
    config: workflowId || undefined 
  });

  const workflowHandler = useMemo(() => {
    if (!selectedProjectType || !workflowId) return null;
    return {
      handleProjectSelect: workflowEngine.handleProjectSelect,
      handleUserInput: workflowEngine.handleUserInput,
      handleFileUpload: workflowEngine.handleFileUpload,
      handleBrickAction: workflowEngine.handleBrickAction,
      handleBrickComplete: workflowEngine.handleBrickComplete,
      handleBrickError: workflowEngine.handleBrickError,
      renderModals: workflowEngine.renderModals,
      currentStep: workflowEngine.currentStep,
      currentStepConfig: workflowEngine.currentStepConfig,
      activeBricks: workflowEngine.activeBricks,
    };
  }, [selectedProjectType, workflowId, workflowEngine]);

  useEffect(() => {
    const urlProjectId = searchParams.get('projectId');
    
    if (urlProjectId) {
      setProjectId(urlProjectId);
      // Load project to determine type
      const loadProject = async () => {
        try {
          const { projectsAPI } = await import('@/lib/api/projects');
          const project = await projectsAPI.getProject(urlProjectId);
          
          // Map project type to ProjectType
          const projectTypeMap: Record<string, ProjectType> = {
            'music-clip': 'music_video_clip',
            'music_video_clip': 'music_video_clip',
            'video-clip': 'video_clip',
            'video-edit': 'video_clip',
            'video_clip': 'video_clip',
            'business-ad': 'business_ad',
            'business_ad': 'business_ad',
            'automate-workflow': 'automate_workflow',
            'automate_workflow': 'automate_workflow',
            'custom': 'automate_workflow'
          };
          
          const mappedType = projectTypeMap[project.type] || 'music_video_clip';
          setSelectedProjectType(mappedType);
          console.log('📦 Loaded project:', { id: project.id, type: project.type, mappedType });
        } catch (error) {
          console.error('❌ Failed to load project:', error);
        }
      };
      loadProject();
    } else {
      checkLLMAvailability();
      
      const greeting = [
        "Hi! How can I help you create something amazing today?",
        "Hello! What would you like to create today?",
        "Welcome! What can I help you build?",
        "Hey there! Ready to create something awesome?"
      ][Math.floor(Math.random() * 4)];
      
      const greetingMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: greeting,
        timestamp: new Date()
      };
      
      setMessages([greetingMessage]);
      setTimeout(() => {
        setShowProjectTypeCards(true);
      }, 500);
    }
  }, [searchParams]);

  const checkLLMAvailability = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      await fetch('/api/v1/ai/llm/health', {
        method: 'GET',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
    } catch (error) {
      console.warn('LLM availability check failed:', error);
    }
  };



  const handleProjectTypeSelect = async (type: ProjectType) => {
    setSelectedProjectType(type);
    setShowProjectTypeCards(false);
    
    const projectTypeNames: Record<ProjectType, string> = {
      music_video_clip: "Create a music video clip",
      video_clip: "Create a video clip",
      business_ad: "Create a business ad",
      automate_workflow: "Automate a workflow"
    };
    
    const projectTypeToApiType: Record<ProjectType, ApiProjectType> = {
      music_video_clip: "music-clip",
      video_clip: "video-edit",
      business_ad: "video-edit",
      automate_workflow: "custom"
    };
    
    const projectNames: Record<ProjectType, string> = {
      music_video_clip: "Music Video Clip",
      video_clip: "Video Clip",
      business_ad: "Business Ad",
      automate_workflow: "Automate Workflow"
    };
    
    try {
      const { projectsAPI } = await import('@/lib/api/projects');
      
      const newProject = await projectsAPI.createProject({
        type: projectTypeToApiType[type],
        name: `${projectNames[type]} Project`,
        description: `New ${projectNames[type]} project`
      });
      
      setProjectId(newProject.id);
      
      router.push(`/dashboard/create?projectId=${newProject.id}`);
      
      toast({
        title: "Project created",
        description: `${projectNames[type]} project is ready`,
      });
    } catch (error) {
      console.error('Failed to create project:', error);
      toast({
        title: "Project creation failed",
        description: error instanceof Error ? error.message : "Failed to create project. Please try again.",
        variant: "destructive"
      });
      return;
    }
    
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: projectTypeNames[type],
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    // handleProjectSelect will be called via useEffect when workflowHandler is ready
  };

  // Call handleProjectSelect when workflow is ready after project type selection
  useEffect(() => {
    if (selectedProjectType && workflowHandler && projectId) {
      workflowHandler.handleProjectSelect();
    }
  }, [selectedProjectType, workflowHandler, projectId]);

  const currentStepConfig = workflowHandler?.currentStepConfig || null;

  return (
    <WorkflowUI
      context={workflowContext}
      selectedProjectType={selectedProjectType}
      setSelectedProjectType={setSelectedProjectType}
      workflowHandler={workflowHandler}
      currentStep={currentStepConfig}
      activeBricks={workflowHandler?.activeBricks}
      onBrickAction={(brickId, action, data) => workflowHandler?.handleBrickAction?.(brickId, action, data)}
      onBrickComplete={(brickId, result) => workflowHandler?.handleBrickComplete?.(brickId, result)}
      onBrickError={(brickId, error) => workflowHandler?.handleBrickError?.(brickId, error)}
      onProjectTypeSelect={handleProjectTypeSelect}
      isThinking={isThinking}
      showProjectTypeCards={showProjectTypeCards}
      setShowProjectTypeCards={setShowProjectTypeCards}
      hoveredCardId={hoveredCardId}
      setHoveredCardId={setHoveredCardId}
    />
  );
}
