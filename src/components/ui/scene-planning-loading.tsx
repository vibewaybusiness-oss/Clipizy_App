"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ClipizyLoading } from "@/components/ui/clipizy-loading";
import { 
  Brain, 
  FileText, 
  Image as ImageIcon, 
  Video, 
  CheckCircle, 
  Clock,
  Sparkles,
  Zap,
  Loader2
} from "lucide-react";

interface ScenePlanningLoadingProps {
  isVisible: boolean;
  currentStage: 'prompt-generation' | 'image-generation' | 'video-generation' | 'completed';
  progress: number;
  currentTask: string;
  videoType: string;
  estimatedTime?: string;
}

export function ScenePlanningLoading({ 
  isVisible, 
  currentStage, 
  progress, 
  currentTask,
  videoType,
  estimatedTime = "2-3 minutes"
}: ScenePlanningLoadingProps) {
  if (!isVisible) return null;

  const getStageInfo = (stage: string) => {
    switch (stage) {
      case 'prompt-generation':
        return {
          title: "Scene Planning & Prompt Generation",
          description: "Our AI is analyzing your music and creating detailed scene descriptions",
          icon: Brain,
          color: "text-blue-600",
          bgColor: "bg-blue-50 dark:bg-blue-950/20",
          borderColor: "border-blue-200 dark:border-blue-800"
        };
      case 'image-generation':
        return {
          title: "Image Generation",
          description: "Creating stunning visuals for each scene based on your music",
          icon: ImageIcon,
          color: "text-purple-600",
          bgColor: "bg-purple-50 dark:bg-purple-950/20",
          borderColor: "border-purple-200 dark:border-purple-800"
        };
      case 'video-generation':
        return {
          title: "Video Generation",
          description: "Animating your scenes and synchronizing with the music",
          icon: Video,
          color: "text-green-600",
          bgColor: "bg-green-50 dark:bg-green-950/20",
          borderColor: "border-green-200 dark:border-green-800"
        };
      case 'completed':
        return {
          title: "Generation Complete!",
          description: "Your music video is ready for review",
          icon: CheckCircle,
          color: "text-green-600",
          bgColor: "bg-green-50 dark:bg-green-950/20",
          borderColor: "border-green-200 dark:border-green-800"
        };
      default:
        return {
          title: "Preparing Generation",
          description: "Setting up your video generation pipeline",
          icon: Sparkles,
          color: "text-primary",
          bgColor: "bg-primary/10",
          borderColor: "border-primary/20"
        };
    }
  };

  const stageInfo = getStageInfo(currentStage);
  const Icon = stageInfo.icon;

  const getStageSteps = (stage: string) => {
    switch (stage) {
      case 'prompt-generation':
        return [
          { id: 'analyze', label: 'Analyzing music structure', delay: 0 },
          { id: 'plan', label: 'Planning scene breakdown', delay: 1000 },
          { id: 'enhance', label: 'Enhancing prompts with AI', delay: 2000 },
          { id: 'validate', label: 'Validating scene descriptions', delay: 3000 }
        ];
      case 'image-generation':
        return [
          { id: 'prepare', label: 'Preparing image generation', delay: 0 },
          { id: 'generate', label: 'Generating scene images', delay: 1500 },
          { id: 'enhance', label: 'Enhancing image quality', delay: 3000 },
          { id: 'optimize', label: 'Optimizing for video', delay: 4500 }
        ];
      case 'video-generation':
        return [
          { id: 'prepare', label: 'Preparing video generation', delay: 0 },
          { id: 'animate', label: 'Animating scenes', delay: 2000 },
          { id: 'sync', label: 'Synchronizing with music', delay: 4000 },
          { id: 'render', label: 'Rendering final video', delay: 6000 }
        ];
      default:
        return [
          { id: 'init', label: 'Initializing generation', delay: 0 },
          { id: 'setup', label: 'Setting up pipeline', delay: 1000 }
        ];
    }
  };

  const stageSteps = getStageSteps(currentStage);

  return (
    <div className="fixed inset-0 bg-background/95 backdrop-blur-sm z-[70] flex items-center justify-center">
      <Card className="w-full max-w-2xl mx-4 bg-card border border-border">
        <CardContent className="p-8">
          <div className="text-center space-y-6">
            {/* Animated Logo */}
            <div className="flex justify-center">
              <ClipizyLoading message="" size="lg" />
            </div>

            {/* Main Message */}
            <div className="space-y-2">
              <div className="flex items-center justify-center gap-3">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${stageInfo.bgColor} ${stageInfo.borderColor} border-2`}>
                  <Icon className={`w-6 h-6 ${stageInfo.color}`} />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-foreground">
                    {stageInfo.title}
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    {stageInfo.description}
                  </p>
                </div>
              </div>
            </div>

            {/* Video Type Badge */}
            <div className="flex justify-center">
              <Badge variant="outline" className="text-sm px-4 py-2">
                {videoType === 'looped-static' && 'Static Loop Video'}
                {videoType === 'looped-animated' && 'Animated Loop Video'}
                {videoType === 'recurring-scenes' && 'Recurring Scenes Video'}
                {videoType === 'scenes' && 'Dynamic Scenes Video'}
              </Badge>
            </div>

            {/* Current Task */}
            <div className="space-y-2">
              <div className="flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
                <span className="text-sm font-medium text-foreground">
                  {currentTask}
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="h-3" />
            </div>

            {/* Animated Steps */}
            <div className="space-y-3">
              {stageSteps.map((step, index) => (
                <ScenePlanningStep
                  key={step.id}
                  label={step.label}
                  delay={step.delay}
                  isActive={index === Math.floor((progress / 100) * stageSteps.length)}
                  isCompleted={index < Math.floor((progress / 100) * stageSteps.length)}
                />
              ))}
            </div>

            {/* Estimated Time */}
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Clock className="w-4 h-4" />
              <span>Estimated time remaining: {estimatedTime}</span>
            </div>

            {/* Encouraging Message */}
            <p className="text-xs text-muted-foreground">
              {currentStage === 'prompt-generation' && "Creating detailed scene descriptions that will bring your music to life."}
              {currentStage === 'image-generation' && "Generating beautiful visuals that match the mood and energy of your music."}
              {currentStage === 'video-generation' && "Bringing everything together into a stunning music video."}
              {currentStage === 'completed' && "Your music video is ready! You can now review and download your creation."}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

interface ScenePlanningStepProps {
  label: string;
  delay: number;
  isActive: boolean;
  isCompleted: boolean;
}

function ScenePlanningStep({ label, delay, isActive, isCompleted }: ScenePlanningStepProps) {
  const [isVisible, setIsVisible] = React.useState(false);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, delay);

    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div className={`flex items-center space-x-3 transition-all duration-500 ${
      isVisible 
        ? 'opacity-100 translate-x-0' 
        : 'opacity-0 -translate-x-4'
    }`}>
      <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 ${
        isCompleted 
          ? 'bg-green-500 text-white' 
          : isActive 
          ? 'bg-primary text-white animate-pulse' 
          : 'bg-muted text-muted-foreground'
      }`}>
        {isCompleted ? (
          <CheckCircle className="w-3 h-3" />
        ) : isActive ? (
          <Loader2 className="w-3 h-3 animate-spin" />
        ) : (
          <div className="w-2 h-2 rounded-full bg-current" />
        )}
      </div>
      <span className={`text-sm transition-colors duration-300 ${
        isCompleted 
          ? 'text-green-600 dark:text-green-400' 
          : isActive 
          ? 'text-foreground font-medium' 
          : 'text-muted-foreground'
      }`}>
        {label}
      </span>
    </div>
  );
}
