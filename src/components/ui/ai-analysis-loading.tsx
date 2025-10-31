"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";

interface AIAnalysisLoadingProps {
  message?: string;
  isVisible: boolean;
}

export function AIAnalysisLoading({ 
  message = "Analyzing your music with AI...", 
  isVisible 
}: AIAnalysisLoadingProps) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-background/95 backdrop-blur-sm z-[70] flex items-center justify-center">
      <Card className="w-full max-w-md mx-4 bg-card border border-border">
        <CardContent className="p-8">
          <div className="text-center space-y-6">
            {/* Simple Loading Circle */}
            <div className="flex justify-center">
              <div className="w-12 h-12 rounded-full border-4 border-primary/20 border-t-primary animate-spin"></div>
            </div>

            {/* Main Message */}
            <div className="space-y-2">
              <h2 className="text-xl font-semibold text-foreground">
                AI Music Analysis
              </h2>
              <p className="text-sm text-muted-foreground">
                {message}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
