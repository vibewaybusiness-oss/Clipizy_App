"use client";

import { ArrowLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { MusicLogo } from "@/components/common/music-logo";
import { TimelineHeader } from "@/components/common/timeline-header";

interface ProjectHeaderProps {
  currentStep: 1 | 2 | 3 | 4;
  maxReachedStep: 1 | 2 | 3 | 4;
  onBack: (e?: React.MouseEvent) => void;
  onStepClick: (step: number) => void;
}

export function ProjectHeader({
  currentStep,
  maxReachedStep,
  onBack,
  onStepClick,
}: ProjectHeaderProps) {
  return (
    <div className="border-b border-border bg-card">
      <div className="max-w-7xl mx-auto px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={(e) => onBack(e)}
              className="flex items-center space-x-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back to Create</span>
            </button>
          </div>

          <div className="flex-1 flex justify-center">
            <TimelineHeader
              currentStep={currentStep}
              maxReachedStep={maxReachedStep}
              totalSteps={4}
              onStepClick={onStepClick}
            />
          </div>

          <Badge className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg flex items-center space-x-2">
            <MusicLogo className="w-4 h-4" />
            <span>Music Clip Creator</span>
          </Badge>
        </div>
      </div>
    </div>
  );
}
