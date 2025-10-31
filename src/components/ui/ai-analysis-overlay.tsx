"use client";

import React from "react";

interface AIAnalysisOverlayProps {
  isVisible: boolean;
  title?: string;
  subtitle?: string;
  progress?: number;
}

export function AIAnalysisOverlay({
  isVisible,
  title = "AI Analysis",
  subtitle = "Analyzing your music...",
  progress
}: AIAnalysisOverlayProps) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/90 backdrop-blur-md">
      <div className="text-center space-y-6">
        {/* Simple Loading Circle */}
        <div className="w-16 h-16 rounded-full border-4 border-primary/20 border-t-primary animate-spin mx-auto"></div>
        
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-white">{title}</h2>
          <p className="text-sm text-gray-300">{subtitle}</p>
        </div>
      </div>
    </div>
  );
}