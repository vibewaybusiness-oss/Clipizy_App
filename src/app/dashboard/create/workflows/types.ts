import React from "react";

export type ProjectType = "music_video_clip" | "video_clip" | "business_ad" | "automate_workflow";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  files?: {
    images: (File | { name: string; size?: number; type?: string; fileId?: string; url?: string })[];
    audio: (File | { name: string; size?: number; type?: string; fileId?: string; url?: string })[];
  };
  actionButtons?: Array<{
    label?: string;
    icon?: React.ReactNode;
    onClick: () => void;
    variant?: "default" | "outline" | "ghost";
    size?: "sm" | "lg" | "icon";
    className?: string;
    disabled?: boolean;
  }>;
}

export interface WorkflowContext {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  inputEnabled: boolean;
  setInputEnabled: (enabled: boolean) => void;
  fileInputEnabled: boolean;
  setFileInputEnabled: (enabled: boolean) => void;
  prompt: string;
  setPrompt: (prompt: string) => void;
  uploadedImages: File[];
  setUploadedImages: React.Dispatch<React.SetStateAction<File[]>>;
  uploadedAudio: File[];
  setUploadedAudio: React.Dispatch<React.SetStateAction<File[]>>;
  toast: any;
  fileInputRef: React.RefObject<HTMLInputElement>;
  isGenerating: boolean;
  setIsGenerating: (generating: boolean) => void;
  addAssistantMessageWithDelay: (message: Message, delay?: number) => void;
  projectId?: string | null;
  setProjectId?: (id: string | null) => void;
}
