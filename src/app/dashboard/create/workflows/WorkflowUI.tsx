"use client";

import { useMemo, useEffect, useState, useCallback, useRef, memo } from "react";
import { ProjectType } from "./types";
import type { WorkflowContext, Message } from "@/types/workflow";
import { Paperclip, ArrowUp, Music, X, User, Loader2, Play, Pause } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProjectTypeCard } from "./components/ProjectTypeCard";
import { ClipizyLogo } from "@/components/common/clipizy-logo";
import { BrickRenderer } from "./components/BrickRenderer";
import { OverlayGateway } from "./components/OverlayGateway";
import { BrickInstance } from "@/types/bricks";
import { WorkflowStep } from "@/types/workflow";

const AudioTrackItem = memo(function AudioTrackItem({ fileName, audioUrl, fileId }: { fileName: string; audioUrl: string | null; fileId?: string }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const wasPlayingRef = useRef(false);
  
  useEffect(() => {
    if (!audioRef.current) return;
    
    const audio = audioRef.current;
    const handleEnded = () => {
      setIsPlaying(false);
      wasPlayingRef.current = false;
    };
    const handlePause = () => {
      setIsPlaying(false);
      wasPlayingRef.current = false;
    };
    const handlePlay = () => {
      setIsPlaying(true);
      wasPlayingRef.current = true;
    };
    
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('play', handlePlay);
    
    if (wasPlayingRef.current && !audio.paused) {
      setIsPlaying(true);
    }
    
    return () => {
      const wasPlaying = !audio.paused;
      wasPlayingRef.current = wasPlaying;
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('play', handlePlay);
    };
  }, [audioUrl]);
  
  useEffect(() => {
    if (audioRef.current && wasPlayingRef.current && !audioRef.current.paused) {
      setIsPlaying(true);
    }
  }, [audioUrl]);
  
  const handlePlayPause = useCallback(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play().catch(err => {
          console.error('Failed to play audio:', err);
          setIsPlaying(false);
        });
      }
    }
  }, [isPlaying]);
  
  if (!audioUrl) {
    return (
      <div className="flex items-center gap-2.5 text-xs sm:text-sm bg-background/40 px-2.5 py-1.5 rounded-lg border border-border/30">
        <Music className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-primary" />
        <span className="truncate font-medium">{fileName}</span>
      </div>
    );
  }
  
  return (
    <div className="flex items-center gap-2.5 text-xs sm:text-sm bg-background/40 px-2.5 py-1.5 rounded-lg border border-border/30">
      <button
        onClick={handlePlayPause}
        className="flex-shrink-0 w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-primary/10 hover:bg-primary/20 flex items-center justify-center transition-colors"
        aria-label={isPlaying ? "Pause" : "Play"}
      >
        {isPlaying ? (
          <Pause className="w-3 h-3 sm:w-4 sm:h-4 text-primary" />
        ) : (
          <Play className="w-3 h-3 sm:w-4 sm:h-4 text-primary" />
        )}
      </button>
      <Music className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-primary flex-shrink-0" />
      <span className="truncate font-medium flex-1">{fileName}</span>
      <audio ref={audioRef} src={audioUrl} preload="metadata" key={fileId || audioUrl} />
    </div>
  );
});

interface WorkflowUIProps {
  context: WorkflowContext;
  selectedProjectType: ProjectType | null;
  setSelectedProjectType: (type: ProjectType | null) => void;
  workflowHandler: {
    handleProjectSelect: () => void;
    handleUserInput: (input: string) => void;
    handleFileUpload: (files: File[]) => void;
    renderModals: () => React.ReactNode;
  } | null;
  onProjectTypeSelect: (type: ProjectType) => void;
  isThinking: boolean;
  showProjectTypeCards: boolean;
  setShowProjectTypeCards: (show: boolean) => void;
  hoveredCardId: string | null;
  setHoveredCardId: (id: string | null) => void;
  // New props for brick system
  currentStep?: WorkflowStep | null;
  activeBricks?: Map<string, BrickInstance>;
  onBrickAction?: (brickId: string, action: string, data: any) => void;
  onBrickComplete?: (brickId: string, result: any) => void;
  onBrickError?: (brickId: string, error: Error) => void;
}

export function WorkflowUI({
  context,
  selectedProjectType,
  setSelectedProjectType,
  workflowHandler,
  onProjectTypeSelect,
  isThinking,
  showProjectTypeCards,
  setShowProjectTypeCards,
  hoveredCardId,
  setHoveredCardId,
  currentStep,
  activeBricks,
  onBrickAction,
  onBrickComplete,
  onBrickError
}: WorkflowUIProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageContainerRefs = useRef<Map<string, number>>(new Map());
  const [isDragOver, setIsDragOver] = useState(false);
  const [showChatLayout, setShowChatLayout] = useState(false);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState<string>("");
  
  // Unique message ID generator with counter to prevent duplicates
  const messageIdCounterRef = useRef(0);
  const generateUniqueMessageId = useCallback((prefix: string = 'message') => {
    messageIdCounterRef.current += 1;
    return `${prefix}-${Date.now()}-${messageIdCounterRef.current}-${Math.random().toString(36).substring(2, 9)}`;
  }, []);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const maxHeight = 400;
      textareaRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
      textareaRef.current.style.overflowY = scrollHeight > maxHeight ? 'auto' : 'hidden';
    }
  }, [context.prompt]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [context.messages]);

  useEffect(() => {
    if (context.messages.length > 0 && !showChatLayout) {
      setShowChatLayout(true);
    }
  }, [context.messages.length, showChatLayout]);

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleGenerate();
    }
  };

  const handleGenerate = () => {
    if (!context.inputEnabled) return;
    const currentPrompt = context.prompt.trim();
    const hasFiles = context.uploadedAudio.length > 0 || context.uploadedImages.length > 0;
    
    if (selectedProjectType && workflowHandler) {
      if (!currentPrompt.trim() && !hasFiles) {
        context.toast({
          title: "Missing input",
          description: "Please provide your input or upload files",
          variant: "destructive"
        });
        return;
      }
      workflowHandler.handleUserInput(currentPrompt || "");
      context.setPrompt("");
      context.setUploadedImages(() => []);
      context.setUploadedAudio(() => []);
      return;
    }
    
    if (!currentPrompt && !hasFiles) {
      context.toast({
        title: "Missing Information",
        description: "Please provide a prompt or upload files",
        variant: "destructive"
      });
      return;
    }

    const userMessage: Message = {
      id: generateUniqueMessageId('user'),
      role: "user",
      content: currentPrompt || (hasFiles ? `Uploaded ${context.uploadedImages.length + context.uploadedAudio.length} file(s)` : ""),
      timestamp: new Date(),
      files: hasFiles ? {
        images: [...context.uploadedImages],
        audio: [...context.uploadedAudio]
      } : undefined
    };
    
    context.setMessages(prev => [...prev, userMessage]);
    context.setPrompt("");
    context.setUploadedImages(() => []);
    context.setUploadedAudio(() => []);
  };

  const handleFileButtonClick = () => {
    context.fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    const audioFiles = files.filter(file => file.type.startsWith('audio/'));
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    if (audioFiles.length > 0) {
      context.setUploadedAudio(prev => [...prev, ...audioFiles]);
    }
    if (imageFiles.length > 0) {
      context.setUploadedImages(prev => [...prev, ...imageFiles]);
    }

    if (workflowHandler) {
      workflowHandler.handleFileUpload(files);
    }

    e.target.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (!context.fileInputEnabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;

    const audioFiles = files.filter(file => file.type.startsWith('audio/'));
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    if (audioFiles.length > 0) {
      context.setUploadedAudio(prev => [...prev, ...audioFiles]);
    }
    if (imageFiles.length > 0) {
      context.setUploadedImages(prev => [...prev, ...imageFiles]);
    }

    if (workflowHandler) {
      workflowHandler.handleFileUpload(files);
    }
  };

  const handleEditMessage = (messageId: string) => {
    const message = context.messages.find(m => m.id === messageId);
    if (message) {
      setEditingMessageId(messageId);
      setEditingContent(message.content);
    }
  };

  const handleSaveEdit = () => {
    if (editingMessageId) {
      context.setMessages(prev => 
        prev.map(msg => 
          msg.id === editingMessageId 
            ? { ...msg, content: editingContent }
            : msg
        )
      );
      setEditingMessageId(null);
      setEditingContent("");
    }
  };

  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditingContent("");
  };

  const renderMessage = (message: Message) => {
    const isUser = message.role === "user";
    const isAssistant = message.role === "assistant";
    const hasFiles = message.files && (message.files.images.length > 0 || message.files.audio.length > 0);
    const isEditing = editingMessageId === message.id;

    return (
      <div
        key={message.id}
        ref={(el) => {
          if (el) {
            messageContainerRefs.current.set(message.id, el.offsetTop);
          }
        }}
        className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
      >
        {!isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="w-4 h-4 text-primary" />
          </div>
        )}
        
        <div className={`max-w-[80%] ${isUser ? 'order-first' : ''}`}>
          <div className={`rounded-2xl px-4 py-3 ${
            isUser 
              ? 'bg-primary text-primary-foreground' 
              : 'bg-muted'
          }`}>
            {isEditing ? (
              <div className="space-y-2">
                <textarea
                  value={editingContent}
                  onChange={(e) => setEditingContent(e.target.value)}
                  className="w-full p-2 border rounded resize-none bg-background text-foreground"
                  rows={3}
                />
                <div className="flex gap-2">
                  <Button size="sm" onClick={handleSaveEdit}>Save</Button>
                  <Button size="sm" variant="outline" onClick={handleCancelEdit}>Cancel</Button>
                </div>
              </div>
            ) : (
              <div className="whitespace-pre-wrap break-words">
                {message.content}
              </div>
            )}
            
            {hasFiles && (
              <div className="mt-3 space-y-2">
                {message.files?.images.map((file, index) => (
                  <div key={index} className="relative">
                    <img
                      src={file instanceof File ? URL.createObjectURL(file) : file.url}
                      alt={file.name}
                      className="max-w-full h-auto rounded-lg max-h-64 object-cover"
                    />
                  </div>
                ))}
                
                {message.files?.audio.map((file, index) => (
                  <AudioTrackItem
                    key={index}
                    fileName={file.name}
                    audioUrl={file instanceof File ? URL.createObjectURL(file) : file.url || null}
                    fileId={'fileId' in file ? file.fileId : undefined}
                  />
                ))}
              </div>
            )}
            
            {message.actionButtons && message.actionButtons.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {message.actionButtons.map((button, index) => (
                  <Button
                    key={index}
                    variant={button.variant || "default"}
                    size={button.size === "md" ? "sm" : (button.size || "sm")}
                    onClick={button.onClick}
                    className={button.className}
                    disabled={button.disabled}
                  >
                    {button.icon}
                    {button.label}
                  </Button>
                ))}
              </div>
            )}
          </div>
          
          <div className={`text-xs text-muted-foreground mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {message.timestamp.toLocaleTimeString()}
            {isUser && (
              <button
                onClick={() => handleEditMessage(message.id)}
                className="ml-2 text-primary hover:underline"
              >
                Edit
              </button>
            )}
          </div>
        </div>
        
        {isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="w-4 h-4 text-primary" />
          </div>
        )}
      </div>
    );
  };

  const renderBricks = () => {
    if (!currentStep || !activeBricks || !currentStep.bricks) return null;

    return (
      <div className="space-y-4 mb-6">
        {currentStep.bricks.map(brickConfig => {
          // Hide file/user_input bricks when prompt/chat input is active or when there are messages
          if (brickConfig.type === 'user_input' && (context.inputEnabled || context.fileInputEnabled || context.messages.length > 0)) {
            return null;
          }
          const brick = activeBricks.get(brickConfig.id);
          if (!brick) return null;

          return (
            <BrickRenderer
              key={brickConfig.id}
              brick={brick}
              onAction={onBrickAction}
              onComplete={onBrickComplete}
              onError={onBrickError}
              context={context}
            />
          );
        })}
      </div>
    );
  };

  // Inline project type selection within chat; no full-screen overlay

  if (showChatLayout) {
    return (
      <div className="flex flex-col h-screen max-h-screen bg-gradient-to-br from-background via-background to-muted/20 animate-in slide-in-from-bottom duration-500">
        <OverlayGateway context={context} />
        <div className="border-b border-border/40 bg-gradient-to-b from-background via-background/95 to-background/90 backdrop-blur-xl supports-[backdrop-filter]:bg-background/80 sticky top-0 z-10 shadow-sm shadow-black/5 dark:shadow-black/20">
          <div className="max-w-4xl mx-auto px-4 py-6 sm:py-7 md:py-8">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-1 h-8 sm:h-10 bg-gradient-to-b from-blue-400 via-purple-500 to-purple-600 rounded-full"></div>
              <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 dark:from-blue-400 dark:via-purple-500 dark:to-pink-500 bg-clip-text text-transparent leading-tight">
                Create Your Content
              </h1>
            </div>
            <div className="pl-4">
              <p className="text-sm sm:text-base md:text-lg text-muted-foreground/90 leading-relaxed">
                Describe your vision and our AI will bring it to life
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-6 sm:py-8">
          <div className="max-w-4xl mx-auto space-y-5 sm:space-y-6">
            {renderBricks()}

            {/* Chat bubbles as before */}
            {context.messages.map((message, messageIndex) => {
              const contentStr = typeof message.content === 'string' ? message.content : String(message.content || '');
              const isError = contentStr.toLowerCase().includes("error") || contentStr.toLowerCase().includes("sorry");
              const hasBeenRepliedTo = messageIndex < context.messages.length - 1;
              const showActionButtons = message.actionButtons && message.actionButtons.length > 0 && !hasBeenRepliedTo;
              const isLoading = contentStr.toLowerCase().includes("uploading") && message.id.startsWith("upload-loading");
              
              return (
                <div
                  key={message.id}
                  className={`flex gap-3 sm:gap-4 animate-in fade-in duration-300 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  {message.role === "assistant" && (
                    <div className="flex-shrink-0 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-blue-400/20 via-purple-500/20 to-purple-600/20 dark:from-blue-500/20 dark:via-purple-600/20 dark:to-purple-700/20 flex items-center justify-center ring-2 ring-blue-400/20 dark:ring-purple-600/20 shadow-sm">
                      <ClipizyLogo className="w-5 h-5 sm:w-6 sm:h-6" />
                    </div>
                  )}
                  
                  <div
                    data-message-id={message.id}
                    ref={(el) => {
                      if (el && message.id && !editingMessageId) {
                        const width = el.getBoundingClientRect().width;
                        messageContainerRefs.current.set(message.id, width);
                      }
                    }}
                    className={`max-w-[85%] sm:max-w-[75%] md:max-w-[70%] rounded-2xl sm:rounded-3xl px-4 sm:px-5 py-3 sm:py-4 shadow-lg transition-all duration-200 ${
                      message.role === "user"
                        ? "bg-card text-foreground border border-blue-400/30 dark:border-blue-500/40 dark:bg-blue-950/20 shadow-muted/50 backdrop-blur-sm"
                        : isError
                        ? "bg-destructive/10 text-destructive border-2 border-destructive/20 shadow-destructive/5"
                        : "bg-card text-foreground border border-blue-400/20 dark:border-purple-600/40 dark:bg-purple-950/20 shadow-muted/50 backdrop-blur-sm"
                    }`}
                    style={editingMessageId === message.id && messageContainerRefs.current.has(message.id) 
                      ? { width: `${messageContainerRefs.current.get(message.id)}px`, minWidth: `${messageContainerRefs.current.get(message.id)}px` }
                      : undefined
                    }
                  >
                    {editingMessageId === message.id ? (
                      <div className="space-y-2 w-full">
                        <textarea
                          value={editingContent}
                          onChange={(e) => {
                            setEditingContent(e.target.value);
                            e.target.style.height = 'auto';
                            e.target.style.height = `${Math.min(e.target.scrollHeight, 300)}px`;
                          }}
                          onKeyDown={(e) => {
                            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                              e.preventDefault();
                              context.setMessages(prev => prev.map(msg => 
                                msg.id === message.id ? { ...msg, content: editingContent } : msg
                              ));
                              setEditingMessageId(null);
                              setEditingContent("");
                            } else if (e.key === "Escape") {
                              setEditingMessageId(null);
                              setEditingContent("");
                            }
                          }}
                          className="w-full min-h-[100px] max-h-[300px] text-sm sm:text-base px-3 py-2 rounded-lg bg-background border-2 border-primary/30 focus:border-primary/60 focus:ring-2 focus:ring-primary/20 resize-none overflow-y-auto"
                          autoFocus
                        />
                        <div className="flex items-center gap-2 mt-3 w-full">
                          <Button
                            size="sm"
                            variant="default"
                            className="flex-1"
                            onClick={() => {
                              context.setMessages(prev => prev.map(msg => 
                                msg.id === message.id ? { ...msg, content: editingContent } : msg
                              ));
                              setEditingMessageId(null);
                              setEditingContent("");
                            }}
                          >
                            Save
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1"
                            onClick={() => {
                              setEditingMessageId(null);
                              setEditingContent("");
                            }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className={`flex items-center gap-2 ${isLoading ? 'justify-start' : ''}`}>
                        {isLoading && (
                          <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin text-primary flex-shrink-0" />
                        )}
                        <p className={`whitespace-pre-wrap break-words leading-relaxed ${message.role === "user" ? "text-sm sm:text-base" : "text-sm sm:text-base"} ${isLoading ? 'text-muted-foreground' : ''}`}>
                          {contentStr}
                        </p>
                      </div>
                    )}
                    
                    {showActionButtons && message.actionButtons && editingMessageId !== message.id && (
                      <div className="flex items-center gap-2 mt-3">
                        {message.actionButtons.map((button, index) => {
                          const buttonLabel = (button.label || "").toLowerCase();
                          const isAIGeneration = buttonLabel.includes("generate") || 
                                                 buttonLabel.includes("ai") ||
                                                 (buttonLabel.includes("confirm") && buttonLabel.includes("pay")) ||
                                                 buttonLabel.includes("confirm & pay");
                          const isPaperclip = button.icon && !button.label;
                          let buttonClassName: string;
                          let isDisabled = false;
                          
                          if (isAIGeneration && button.variant === "default") {
                            buttonClassName = `${button.className || "flex-1"} btn-ai-gradient`;
                          } else if (isPaperclip) {
                            buttonClassName = `${button.className || "flex-shrink-0"} ${!context.fileInputEnabled ? "opacity-50 cursor-not-allowed" : ""}`;
                            isDisabled = !context.fileInputEnabled;
                          } else {
                            buttonClassName = button.className || (button.icon ? "flex-shrink-0" : "flex-1");
                          }
                          
                          const handleClick = (e: React.MouseEvent) => {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            if (!button.onClick) {
                              console.warn('Button has no onClick handler:', button.label);
                              return;
                            }
                            
                            const isEditButton = button.label === "Edit";
                            
                            if (isEditButton) {
                              const messageElement = document.querySelector(`[data-message-id="${message.id}"]`) as HTMLElement | null;
                              if (messageElement) {
                                const width = messageElement.getBoundingClientRect().width;
                                messageContainerRefs.current.set(message.id, width);
                              }
                              setEditingMessageId(message.id);
                              setEditingContent(contentStr);
                            } else if (isPaperclip) {
                              if (context.fileInputRef.current) {
                                const wasDisabled = context.fileInputRef.current.disabled;
                                if (wasDisabled && context.fileInputEnabled) {
                                  context.fileInputRef.current.disabled = false;
                                }
                                context.fileInputRef.current.click();
                                if (wasDisabled) {
                                  context.fileInputRef.current.disabled = wasDisabled;
                                }
                              }
                            } else {
                              try {
                                button.onClick();
                              } catch (error) {
                                console.error('Error executing button onClick:', error);
                                context.toast({
                                  variant: "destructive",
                                  title: "Action failed",
                                  description: "Failed to execute action"
                                });
                              }
                            }
                          };
                          
                          return (
                            <Button
                              key={index}
                              variant={isAIGeneration && button.variant === "default" ? "default" : (button.variant || "default")}
                              size={button.size === "md" ? "sm" : (button.size || "sm")}
                              onClick={handleClick}
                              className={buttonClassName}
                              disabled={isDisabled || button.disabled}
                              title={button.label || "Upload file"}
                            >
                              {button.icon || button.label}
                            </Button>
                          );
                        })}
                      </div>
                    )}
                    
                    {message.files && (
                      <div className="mt-3.5 space-y-2.5">
                        {message.files.images.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {message.files.images.map((file, index) => {
                              const isFileObject = file instanceof File;
                              const fileData = isFileObject ? null : (file as any);
                              const imageUrl = isFileObject 
                                ? URL.createObjectURL(file) 
                                : (fileData?.url || null);
                              const fileName = isFileObject 
                                ? file.name 
                                : (fileData?.name || 'Image');
                              
                              return (
                                <div
                                  key={index}
                                  className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl overflow-hidden border border-border/40 bg-background/60 shadow-md ring-1 ring-black/5 flex items-center justify-center"
                                >
                                  {imageUrl ? (
                                    <img
                                      src={imageUrl}
                                      alt={fileName}
                                      className="w-full h-full object-cover"
                                    />
                                  ) : (
                                    <div className="w-full h-full flex items-center justify-center bg-muted text-muted-foreground text-xs">
                                      {fileName}
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        )}
                        {message.files.audio.length > 0 && (
                          <div className="space-y-1.5">
                            {message.files.audio.map((file, index) => {
                              const isFileObject = file instanceof File;
                              const fileData = isFileObject ? null : (file as any);
                              const fileName = isFileObject 
                                ? file.name 
                                : (fileData?.name || 'Audio file');
                              const audioUrl = isFileObject 
                                ? URL.createObjectURL(file) 
                                : (fileData?.url || null);
                              const fileId = fileData?.fileId || (isFileObject ? `${message.id}-${file.name}-${file.size}` : null);
                              
                              return (
                                <AudioTrackItem
                                  key={`${message.id}-audio-${fileId || index}`}
                                  fileName={fileName}
                                  audioUrl={audioUrl}
                                  fileId={fileId}
                                />
                              );
                            })}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {isError && (
                      <div className="mt-2 flex items-center gap-1.5 text-xs text-destructive/70">
                        <div className="w-1 h-1 rounded-full bg-destructive/50"></div>
                        <span>Error detected</span>
                      </div>
                    )}
                  </div>

                  {message.role === "user" && (
                    <div className="flex-shrink-0 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-blue-400/20 via-blue-500/20 to-blue-600/20 dark:from-blue-500/20 dark:via-blue-600/20 dark:to-blue-700/20 flex items-center justify-center ring-2 ring-blue-400/20 dark:ring-blue-600/20 shadow-md">
                      <User className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  )}
                </div>
              );
            })}

            {/* Project type selector appears after greeting */}
            {(!selectedProjectType && showProjectTypeCards) && (
              <div className="flex gap-3 sm:gap-4 animate-in fade-in duration-300 justify-start">
                <div className="flex-shrink-0 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-blue-400/20 via-purple-500/20 to-purple-600/20 dark:from-blue-500/20 dark:via-purple-600/20 dark:to-purple-700/20 flex items-center justify-center ring-2 ring-blue-400/20 dark:ring-purple-600/20 shadow-sm">
                  <ClipizyLogo className="w-5 h-5 sm:w-6 sm:h-6" />
                </div>
                <div className="max-w-[85%] sm:max-w-[75%] md:max-w-[70%] rounded-2xl sm:rounded-3xl px-4 sm:px-5 py-3 sm:py-4 shadow-lg border border-blue-400/20 dark:border-purple-600/40 dark:bg-purple-950/20 bg-card text-foreground">
                  <div className="text-center space-y-3 pb-3">
                    <h1 className="text-xl font-bold">Choose Your Project Type</h1>
                    <p className="text-muted-foreground">Select the type of content you want to create with AI</p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
                    <div className={`transition-all duration-200${hoveredCardId && hoveredCardId !== 'music_video_clip' ? ' opacity-40 grayscale' : ''}`}>
                      <ProjectTypeCard
                        type="music_video_clip"
                        title="Music Video Clip"
                        description="Create a music video clip with AI-generated visuals"
                        icon="music"
                        isSelected={false}
                        isHovered={hoveredCardId === 'music_video_clip'}
                        onMouseEnter={() => setHoveredCardId('music_video_clip')}
                        onMouseLeave={() => setHoveredCardId(null)}
                        onClick={() => onProjectTypeSelect("music_video_clip")}
                      />
                    </div>
                    <div className={`transition-all duration-200${hoveredCardId && hoveredCardId !== 'video_clip' ? ' opacity-40 grayscale' : ''}`}>
                      <ProjectTypeCard
                        type="video_clip"
                        title="Video Clip"
                        description="Create a short video clip with AI-generated content"
                        icon="play"
                        isSelected={false}
                        isHovered={hoveredCardId === 'video_clip'}
                        onMouseEnter={() => setHoveredCardId('video_clip')}
                        onMouseLeave={() => setHoveredCardId(null)}
                        onClick={() => onProjectTypeSelect("video_clip")}
                      />
                    </div>
                    <div className={`transition-all duration-200${hoveredCardId && hoveredCardId !== 'business_ad' ? ' opacity-40 grayscale' : ''}`}>
                      <ProjectTypeCard
                        type="business_ad"
                        title="Business Ad"
                        description="Create a professional business advertisement"
                        icon="user"
                        isSelected={false}
                        isHovered={hoveredCardId === 'business_ad'}
                        onMouseEnter={() => setHoveredCardId('business_ad')}
                        onMouseLeave={() => setHoveredCardId(null)}
                        onClick={() => onProjectTypeSelect("business_ad")}
                      />
                    </div>
                    <div className={`transition-all duration-200${hoveredCardId && hoveredCardId !== 'automate_workflow' ? ' opacity-40 grayscale' : ''}`}>
                      <ProjectTypeCard
                        type="automate_workflow"
                        title="Automate Workflow"
                        description="Automate your content creation workflow"
                        icon="loader"
                        isSelected={false}
                        isHovered={hoveredCardId === 'automate_workflow'}
                        onMouseEnter={() => setHoveredCardId('automate_workflow')}
                        onMouseLeave={() => setHoveredCardId(null)}
                        onClick={() => onProjectTypeSelect("automate_workflow")}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {(context.isGenerating || isThinking) && (
              <div className="flex gap-3 sm:gap-4 justify-start animate-in fade-in duration-300">
                <div className="flex-shrink-0 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-blue-400/20 via-purple-500/20 to-purple-600/20 dark:from-blue-500/20 dark:via-purple-600/20 dark:to-purple-700/20 flex items-center justify-center ring-2 ring-blue-400/20 dark:ring-purple-600/20 shadow-sm animate-pulse">
                  <ClipizyLogo className="w-5 h-5 sm:w-6 sm:h-6" />
                </div>
                <div className="bg-card text-foreground border border-blue-400/20 dark:border-purple-600/40 rounded-2xl sm:rounded-3xl px-4 sm:px-5 py-3 sm:py-4 shadow-lg shadow-muted/50 backdrop-blur-sm">
                  <div className="flex gap-1.5 items-center">
                    <span className="w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-500 dark:from-blue-500 dark:to-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-500 dark:from-blue-500 dark:to-purple-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-500 dark:from-blue-500 dark:to-purple-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    <span className="ml-2 text-xs sm:text-sm text-muted-foreground">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="border-t border-border/50 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60 sticky bottom-0 z-10 shadow-lg shadow-black/5">
          <div className="max-w-4xl mx-auto px-4 py-4 sm:py-5">
            {(context.uploadedImages.length > 0 || context.uploadedAudio.length > 0) && (
              <div className="mb-3 sm:mb-4 flex flex-wrap gap-2 sm:gap-2.5">
                {context.uploadedImages.map((file, index) => {
                  const isFileObject = file instanceof File;
                  const imageUrl = isFileObject ? URL.createObjectURL(file) : null;
                  const fileName = isFileObject ? file.name : (file as any).name || 'Image';
                  
                  return (
                  <div
                    key={`img-${index}`}
                    className="group relative w-14 h-14 sm:w-16 sm:h-16 rounded-xl overflow-hidden border-2 border-border/50 bg-background shadow-md ring-1 ring-black/5 transition-all hover:scale-105 hover:shadow-lg"
                  >
                    {imageUrl ? (
                      <img
                        src={imageUrl}
                        alt={fileName}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-muted text-muted-foreground text-xs">
                        {fileName}
                      </div>
                    )}
                    <button
                      onClick={() => context.setUploadedImages(prev => prev.filter((_, i) => i !== index))}
                      className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-all duration-200 backdrop-blur-sm"
                      aria-label="Remove image"
                    >
                      <X className="w-4 h-4 text-white" />
                    </button>
                  </div>
                  );
                })}
                {context.uploadedAudio.map((file, index) => (
                  <div
                    key={`audio-${index}`}
                    className="flex items-center gap-2 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-xl border border-border/50 bg-muted/50 text-xs sm:text-sm shadow-sm hover:shadow-md transition-shadow"
                  >
                    <Music className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-primary" />
                    <span className="max-w-[120px] sm:max-w-[150px] truncate font-medium">{file.name}</span>
                    <button
                      onClick={() => context.setUploadedAudio(prev => prev.filter((_, i) => i !== index))}
                      className="ml-1 hover:text-destructive transition-colors p-0.5 rounded hover:bg-destructive/10"
                      aria-label="Remove audio"
                    >
                      <X className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    </button>
                  </div>
                ))}
                {context.uploadedAudio.length > 1 && (
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-primary/10 text-primary text-xs font-medium">
                    <Music className="w-3 h-3" />
                    <span>Compilation ({context.uploadedAudio.length} files)</span>
                  </div>
                )}
              </div>
            )}

            <div 
              className="relative"
              onDragEnter={(e) => {
                if (!context.fileInputEnabled) return;
                e.preventDefault();
                e.stopPropagation();
                setIsDragOver(true);
              }}
              onDragOver={(e) => {
                if (!context.fileInputEnabled) return;
                e.preventDefault();
                e.stopPropagation();
              }}
              onDragLeave={(e) => {
                if (!context.fileInputEnabled) return;
                e.preventDefault();
                e.stopPropagation();
                setIsDragOver(false);
              }}
              onDrop={(e) => {
                if (!context.fileInputEnabled) return;
                e.preventDefault();
                e.stopPropagation();
                setIsDragOver(false);
                
                const files = Array.from(e.dataTransfer.files);
                if (files.length > 0 && workflowHandler) {
                  workflowHandler.handleFileUpload(files);
                }
              }}
            >
              <div className={`relative transition-all duration-300 ${isDragOver ? 'scale-[1.01]' : ''}`}>
                <textarea
                  ref={textareaRef}
                  value={context.prompt}
                  onChange={(e) => context.setPrompt(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder={context.inputEnabled ? "Type your message..." : context.fileInputEnabled ? "Upload files or use the buttons above..." : "Follow the prompts to create your content"}
                  disabled={!context.inputEnabled}
                  className={`w-full min-h-[64px] sm:min-h-[72px] text-base px-4 sm:px-5 py-3.5 sm:py-4 pr-28 sm:pr-32 rounded-2xl sm:rounded-3xl bg-card border-2 transition-all duration-300 resize-none overflow-hidden shadow-lg shadow-black/5 focus:shadow-xl focus:shadow-primary/10 ${
                    !context.inputEnabled 
                      ? 'opacity-60 cursor-not-allowed'
                      : isDragOver 
                      ? 'border-primary/60 bg-primary/10 ring-4 ring-primary/20 scale-[1.01]' 
                      : 'border-border/60 focus:border-primary/60 focus:ring-4 focus:ring-primary/10'
                  }`}
                  style={{ maxHeight: '200px' }}
                />
                {isDragOver && (
                  <div className="absolute inset-0 flex items-center justify-center bg-primary/15 rounded-2xl sm:rounded-3xl pointer-events-none z-10 backdrop-blur-sm border-2 border-dashed border-primary/40">
                    <div className="text-center">
                      <p className="text-base sm:text-lg font-semibold text-primary mb-1">
                        {selectedProjectType === "music_video_clip" ? "Drop audio files here" : "Drop files here"}
                      </p>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        {selectedProjectType === "music_video_clip" ? "Up to 20 audio files for compilation" : "Images or audio files"}
                      </p>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="absolute right-3 sm:right-4 bottom-3 sm:bottom-4 flex items-center gap-2">
                <input
                  ref={context.fileInputRef}
                  type="file"
                  accept={selectedProjectType === "music_video_clip" ? "audio/*,.mp3,.wav,.m4a,.aac,.flac" : "image/*,audio/*"}
                  multiple={selectedProjectType === "music_video_clip"}
                  onChange={(e) => {
                    const files = e.target.files;
                    if (files && files.length > 0) {
                      const fileArray = Array.from(files);
                      if (workflowHandler) {
                        workflowHandler.handleFileUpload(fileArray);
                      } else if (context.fileInputEnabled) {
                        const imageFiles = fileArray.filter(file => file.type.startsWith("image/"));
                        const audioFiles = fileArray.filter(file => file.type.startsWith("audio/"));
                        if (imageFiles.length > 0) {
                          context.setUploadedImages(prev => [...prev, ...imageFiles]);
                        }
                        if (audioFiles.length > 0) {
                          context.setUploadedAudio(prev => [...prev, ...audioFiles]);
                        }
                      }
                    }
                    if (e.target) {
                      e.target.value = '';
                    }
                  }}
                  className="hidden"
                  disabled={!context.fileInputEnabled}
                />
                
                 <Button
                   onClick={handleFileButtonClick}
                   size="sm"
                   variant="ghost"
                   disabled={!context.fileInputEnabled}
                   className="h-9 w-9 sm:h-10 sm:w-10 p-0 rounded-xl hover:bg-muted transition-all duration-200 shadow-sm hover:shadow-md border border-border/50 disabled:opacity-50 disabled:cursor-not-allowed"
                   aria-label="Upload files"
                 >
                   <Paperclip className="w-4 h-4 sm:w-5 sm:h-5" />
                 </Button>
                
                 <Button
                   onClick={handleGenerate}
                   size="sm"
                   disabled={context.isGenerating || !context.inputEnabled || (!context.prompt.trim() && context.uploadedAudio.length === 0 && context.uploadedImages.length === 0)}
                   className="h-9 w-9 sm:h-10 sm:w-10 p-0 rounded-xl bg-gradient-to-br from-primary via-primary to-primary/90 hover:from-primary/90 hover:via-primary/90 hover:to-primary/80 text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transition-all duration-200"
                   aria-label="Send"
                 >
                   <ArrowUp className="w-4 h-4 sm:w-5 sm:h-5" />
                 </Button>
              </div>
            </div>

            <p className="text-xs sm:text-sm text-muted-foreground mt-3 sm:mt-3.5 text-center">
              {context.inputEnabled 
                ? "Press Ctrl+Enter to send" 
                : "Follow the prompts to create your content"}
            </p>
          </div>
        </div>

        {workflowHandler && workflowHandler.renderModals()}
      </div>
    );
  }

  return null;
}
