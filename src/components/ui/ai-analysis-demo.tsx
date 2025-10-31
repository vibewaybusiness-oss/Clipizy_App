"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { AIAnalysisOverlay } from "./ai-analysis-overlay";

export function AIAnalysisDemo() {
  const [isVisible, setIsVisible] = useState(false);
  const [progress, setProgress] = useState(0);

  const startDemo = () => {
    setIsVisible(true);
    setProgress(0);

    // Simulate progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setIsVisible(false), 1000);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 500);
  };

  return (
    <div className="p-8">
      <div className="max-w-md mx-auto text-center space-y-4">
        <h2 className="text-2xl font-bold">AI Analysis Animation Demo</h2>
        <p className="text-muted-foreground">
          Click the button below to see the full-screen AI analysis animation.
        </p>
        <Button onClick={startDemo} className="btn-ai-gradient">
          Start AI Analysis Demo
        </Button>
      </div>

      <AIAnalysisOverlay
        isVisible={isVisible}
        title="Analyzing Music"
        subtitle="AI is processing your audio tracks..."
        progress={progress}
      />
    </div>
  );
}
