"use client";

import React, { useState, useEffect } from "react";
import { Info, X, HelpCircle, Lightbulb, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface InfoPopupProps {
  className?: string;
}

export function InfoPopup({ className = "" }: InfoPopupProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);

    // Add CSS for responsive positioning
    const style = document.createElement('style');
    style.textContent = `
      [data-info-popup] {
        position: fixed !important;
        top: 16px !important;
        left: 64px !important;
        z-index: 70 !important;
      }
      @media (min-width: 768px) {
        [data-info-popup] {
          left: 16px !important;
        }
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  const infoItems = [
    {
      icon: <Sparkles className="w-4 h-4" />,
      title: "AI-Powered Creation",
      description: "Transform your audio into stunning music videos with AI"
    },
    {
      icon: <Lightbulb className="w-4 h-4" />,
      title: "Quick Tips",
      description: "Upload high-quality audio for best results"
    },
    {
      icon: <HelpCircle className="w-4 h-4" />,
      title: "Need Help?",
      description: "Check our documentation or contact support"
    }
  ];

  // Don't render on server to prevent hydration mismatch
  if (!isClient) {
    return null;
  }

  return (
    <div
      data-info-popup
      className={`fixed top-4 left-16 z-[70] md:left-4 ${className}`}
      style={{
        position: 'fixed',
        top: '16px',
        left: '64px',
        zIndex: 70
      }}
    >
      {!isExpanded ? (
        <Button
          onClick={() => setIsExpanded(true)}
          size="sm"
          variant="outline"
          className="bg-background/95 backdrop-blur-sm border-border/50 shadow-lg hover:bg-accent/50 transition-all duration-200"
        >
          <Info className="w-4 h-4 mr-2" />
          Info
        </Button>
      ) : (
        <Card className="w-80 bg-background/95 backdrop-blur-sm border-border/50 shadow-xl">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center">
                <Info className="w-4 h-4 mr-2" />
                Quick Info
              </CardTitle>
              <Button
                onClick={() => setIsExpanded(false)}
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0 hover:bg-accent/50"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pt-0 space-y-3">
            {infoItems.map((item, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-0.5 text-primary">
                  {item.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground">
                    {item.title}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
            <div className="pt-2 border-t border-border/50">
              <div className="flex items-center justify-between">
                <Badge variant="secondary" className="text-xs">
                  clipizy AI
                </Badge>
                <span className="text-xs text-muted-foreground">
                  Always here to help
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
