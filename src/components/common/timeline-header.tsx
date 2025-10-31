"use client";

import React from "react";
import { Check } from "lucide-react";

interface TimelineStep {
  id: number;
  title: string;
  description: string;
}

interface TimelineHeaderProps {
  currentStep: number;
  maxReachedStep: number;
  totalSteps: number;
  onStepClick: (step: number) => void;
  lockNavigation?: boolean; // When true, prevents navigation to previous steps
}

const steps: TimelineStep[] = [
  { id: 1, title: "Music", description: "Upload or generate music" },
  { id: 2, title: "Blueprint", description: "Review AI analysis" },
  { id: 3, title: "Visual Story", description: "Define video concept" },
  { id: 4, title: "Generate", description: "Final touches & create" }
];

export function TimelineHeader({ currentStep, maxReachedStep, totalSteps, onStepClick, lockNavigation = false }: TimelineHeaderProps) {
  return (
    <>
      {/* Desktop Layout */}
      <div className="hidden sm:flex items-center space-x-3">
        {/* Timeline Steps */}
        {steps.slice(0, totalSteps).map((step, index) => {
          const isCompleted = step.id < currentStep;
          const isCurrent = step.id === currentStep;
          const isReached = step.id <= maxReachedStep;
          const isUpcoming = step.id > maxReachedStep;
          const canNavigate = isReached && (!lockNavigation || step.id >= currentStep);
          const isActive = isCurrent || (lockNavigation && step.id === currentStep);

          return (
            <React.Fragment key={step.id}>
              {/* Step Bubble */}
              <div
                className={`flex flex-col items-center space-y-1 group ${
                  canNavigate ? 'cursor-pointer' : isActive ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'
                }`}
                onClick={() => {
                  if (canNavigate || isActive) {
                    onStepClick(step.id);
                  }
                }}
              >
                <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 ${
                      isCompleted
                        ? "bg-primary text-primary-foreground hover:bg-primary/80"
                        : isActive
                        ? "bg-primary text-primary-foreground ring-2 ring-primary/30"
                        : isReached
                        ? "bg-muted text-muted-foreground hover:bg-muted-foreground/20 hover:text-foreground"
                        : "bg-muted/50 text-muted-foreground/50"
                    }`}
                >
                  {isCompleted ? (
                    <Check className="w-3 h-3" />
                  ) : (
                    <span className="text-xs font-semibold">{step.id}</span>
                  )}
                </div>
                <div className="text-center">
                  <div
                    className={`text-xs font-medium transition-colors duration-300 ${
                      isActive
                        ? "text-foreground"
                        : isCompleted
                        ? "text-muted-foreground group-hover:text-foreground"
                        : isReached
                        ? "text-muted-foreground group-hover:text-foreground"
                        : "text-muted-foreground/50"
                    }`}
                  >
                    {step.title}
                  </div>
                </div>
              </div>

              {/* Connector Line */}
              {index < totalSteps - 1 && (
                <div
                  className={`h-0.5 w-6 transition-colors duration-300 ${
                    step.id <= maxReachedStep ? "bg-primary" : "bg-border"
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Mobile Layout - Compact Overlapping Circles */}
      <div className="flex sm:hidden items-center justify-center">
        <div className="relative flex items-center">
          {steps.slice(0, totalSteps).map((step, index) => {
            const isCompleted = step.id < currentStep;
            const isCurrent = step.id === currentStep;
            const isReached = step.id <= maxReachedStep;
            const isUpcoming = step.id > maxReachedStep;
            const canNavigate = isReached && (!lockNavigation || step.id >= currentStep);
            const isActive = isCurrent || (lockNavigation && step.id === currentStep);

            return (
              <div
                key={step.id}
                className={`relative ${
                  canNavigate ? 'cursor-pointer' : isActive ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'
                }`}
                onClick={() => {
                  if (canNavigate || isActive) {
                    onStepClick(step.id);
                  }
                }}
                style={{
                  marginLeft: index > 0 ? '-8px' : '0',
                  zIndex: totalSteps - index
                }}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 border-2 border-background ${
                    isCompleted
                      ? "bg-primary text-primary-foreground hover:bg-primary/80"
                      : isActive
                      ? "bg-primary text-primary-foreground ring-2 ring-primary/30"
                      : isReached
                      ? "bg-muted text-muted-foreground hover:bg-muted-foreground/20 hover:text-foreground"
                      : "bg-muted/50 text-muted-foreground/50"
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <span className="text-sm font-semibold">{step.id}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}
