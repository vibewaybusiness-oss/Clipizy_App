"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { 
  Film, 
  Clock, 
  Zap, 
  CheckCircle, 
  Sparkles,
  Brain,
  Image as ImageIcon,
  Video
} from "lucide-react";

interface GenerationConfirmationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  videoType: string;
  estimatedCredits: number;
  estimatedTime: string;
  isGenerating?: boolean;
}

export function GenerationConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  videoType,
  estimatedCredits,
  estimatedTime,
  isGenerating = false
}: GenerationConfirmationDialogProps) {
  const getVideoTypeInfo = (type: string) => {
    switch (type) {
      case 'looped-static':
        return {
          title: 'Static Loop Video',
          description: 'A single static image that loops with your music',
          icon: ImageIcon,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50 dark:bg-blue-950/20',
          borderColor: 'border-blue-200 dark:border-blue-800'
        };
      case 'looped-animated':
        return {
          title: 'Animated Loop Video',
          description: 'A single animated scene that loops with your music',
          icon: Video,
          color: 'text-purple-600',
          bgColor: 'bg-purple-50 dark:bg-purple-950/20',
          borderColor: 'border-purple-200 dark:border-purple-800'
        };
      case 'recurring-scenes':
        return {
          title: 'Recurring Scenes Video',
          description: 'Multiple scenes that repeat throughout your music',
          icon: Film,
          color: 'text-green-600',
          bgColor: 'bg-green-50 dark:bg-green-950/20',
          borderColor: 'border-green-200 dark:border-green-800'
        };
      case 'scenes':
        return {
          title: 'Dynamic Scenes Video',
          description: 'Unique scenes that change throughout your music',
          icon: Sparkles,
          color: 'text-orange-600',
          bgColor: 'bg-orange-50 dark:bg-orange-950/20',
          borderColor: 'border-orange-200 dark:border-orange-800'
        };
      default:
        return {
          title: 'Music Video',
          description: 'A custom music video based on your description',
          icon: Film,
          color: 'text-primary',
          bgColor: 'bg-primary/10',
          borderColor: 'border-primary/20'
        };
    }
  };

  const videoTypeInfo = getVideoTypeInfo(videoType);
  const Icon = videoTypeInfo.icon;

  const generationSteps = [
    {
      icon: Brain,
      title: 'Scene Planning & Prompt Generation',
      description: 'AI analyzes your music and creates detailed scene descriptions',
      duration: '30-60 seconds'
    },
    {
      icon: ImageIcon,
      title: 'Image Generation',
      description: 'Creating stunning visuals for each scene',
      duration: '1-2 minutes'
    },
    {
      icon: Video,
      title: 'Video Generation',
      description: 'Animating scenes and synchronizing with music',
      duration: '2-3 minutes'
    }
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${videoTypeInfo.bgColor} ${videoTypeInfo.borderColor} border-2`}>
              <Icon className={`w-5 h-5 ${videoTypeInfo.color}`} />
            </div>
            <div>
              <div className="text-xl font-bold">Confirm Video Generation</div>
              <div className="text-sm font-normal text-muted-foreground">
                {videoTypeInfo.title}
              </div>
            </div>
          </DialogTitle>
          <DialogDescription className="text-base">
            {videoTypeInfo.description}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Generation Details */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
              <Zap className="w-5 h-5 text-primary" />
              <div>
                <div className="text-sm font-medium">Credits Required</div>
                <div className="text-lg font-bold text-primary">{estimatedCredits}</div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
              <Clock className="w-5 h-5 text-primary" />
              <div>
                <div className="text-sm font-medium">Estimated Time</div>
                <div className="text-lg font-bold text-primary">{estimatedTime}</div>
              </div>
            </div>
          </div>

          {/* Generation Process */}
          <div className="space-y-3">
            <h4 className="font-semibold text-foreground">Generation Process</h4>
            <div className="space-y-3">
              {generationSteps.map((step, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-muted/30 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <step.icon className="w-4 h-4 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-foreground">{step.title}</div>
                    <div className="text-sm text-muted-foreground">{step.description}</div>
                    <Badge variant="outline" className="mt-1 text-xs">
                      {step.duration}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Important Notes */}
          <div className="p-4 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-xs font-bold">i</span>
              </div>
              <div className="text-sm text-blue-800 dark:text-blue-200">
                <p className="font-medium mb-1">Important Notes</p>
                <ul className="space-y-1 text-xs">
                  <li>• Your video will be generated using AI and may take several minutes</li>
                  <li>• You can monitor progress in the generation overview page</li>
                  <li>• Credits will be deducted once generation starts</li>
                  <li>• You can regenerate individual scenes if needed</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button 
            variant="outline" 
            onClick={onClose}
            disabled={isGenerating}
          >
            Cancel
          </Button>
          <Button 
            onClick={onConfirm}
            disabled={isGenerating}
            className="btn-ai-gradient text-white"
          >
            {isGenerating ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Starting Generation...
              </>
            ) : (
              <>
                <Film className="w-4 h-4 mr-2" />
                Start Generation ({estimatedCredits} credits)
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
