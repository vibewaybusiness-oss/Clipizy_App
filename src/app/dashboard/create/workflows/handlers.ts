
"use client";

import { useMemo } from "react";
import { useWorkflowEngine } from "./WorkflowEngine";
import type { WorkflowContext } from "@/types/workflow";
import type { ProjectType } from "./types";

type EngineSubset = {
  handleProjectSelect: (projectType?: string) => void;
  handleUserInput: (input: string) => void;
  handleFileUpload: (files: File[]) => void;
  handleBrickAction: (brickId: string, action: string, data: any) => void;
  handleBrickComplete: (brickId: string, result: any) => void;
  handleBrickError: (brickId: string, error: Error) => void;
  renderModals: () => React.ReactNode;
  currentStep?: string;
  currentStepConfig?: any;
  activeBricks?: Map<string, any>;
};

const projectTypeToWorkflowId: Record<ProjectType, string> = {
  music_video_clip: "music-clip-workflow",
  video_clip: "video-clip-workflow",
  business_ad: "business-ad-workflow",
  automate_workflow: "automate-workflow",
};

// DEPRECATED: Loading all engines at once causes duplicate messages
// Use useWorkflowEngine directly with selected project type instead
export function useWorkflowHandlers(context: WorkflowContext): Record<ProjectType, EngineSubset> {
  throw new Error('useWorkflowHandlers is deprecated. Use useWorkflowEngine with selected project type instead.');
}

export function createWorkflowHandler(
  selected: ProjectType | null,
  handlers: Record<ProjectType, EngineSubset>
) {
  if (!selected) return null;
  return handlers[selected] ?? null;
}