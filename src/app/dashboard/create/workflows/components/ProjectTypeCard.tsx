"use client";

import React from "react";
import { Music, PlayCircle, BadgeDollarSign, Loader2 } from "lucide-react";

interface ProjectTypeCardProps {
  type: string;
  title: string;
  description: string;
  icon: string;
  isSelected: boolean;
  onClick: () => void;
  isHovered?: boolean;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  variant?: "card" | "line";
}

export function ProjectTypeCard({
  type,
  title,
  description,
  icon,
  isSelected,
  onClick,
  isHovered,
  onMouseEnter,
  onMouseLeave,
  variant = "card"
}: ProjectTypeCardProps) {
  const isOtherCardHovered = isHovered !== undefined && !isHovered;

  const getCardStyles = () => {
    switch (type) {
      case "music_video_clip":
        return {
          card: isSelected 
            ? "border-blue-400 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/40 dark:to-cyan-950/40 shadow-lg" 
            : isHovered
            ? "border-blue-300 bg-gradient-to-br from-blue-50/50 to-cyan-50/50 dark:from-blue-950/20 dark:to-cyan-950/20 hover:shadow-md"
            : isOtherCardHovered
            ? "border-blue-200 bg-gradient-to-br from-blue-50/30 to-cyan-50/30 dark:from-blue-950/10 dark:to-cyan-950/10 opacity-60"
            : "border-blue-200 bg-gradient-to-br from-blue-50/50 to-cyan-50/50 dark:from-blue-950/20 dark:to-cyan-950/20 hover:border-blue-300 hover:shadow-md",
          iconBg: "from-blue-500/20 to-cyan-500/20",
          icon: "text-blue-600 dark:text-blue-400",
          name: "Create a music video clip with AI-generated visuals"
        };
      case "video_clip":
        return {
          card: isSelected 
            ? "border-green-400 bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-950/40 dark:to-teal-950/40 shadow-lg" 
            : isHovered
            ? "border-green-300 bg-gradient-to-br from-green-50/50 to-teal-50/50 dark:from-green-950/20 dark:to-teal-950/20 hover:shadow-md"
            : isOtherCardHovered
            ? "border-green-200 bg-gradient-to-br from-green-50/30 to-teal-50/30 dark:from-green-950/10 dark:to-teal-950/10 opacity-60"
            : "border-green-200 bg-gradient-to-br from-green-50/50 to-teal-50/50 dark:from-green-950/20 dark:to-teal-950/20 hover:border-green-300 hover:shadow-md",
          iconBg: "from-green-500/20 to-teal-500/20",
          icon: "text-green-600 dark:text-green-400",
          name: "Create a short video clip with AI-generated content"
        };
      case "business_ad":
        return {
          card: isSelected 
            ? "border-purple-400 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/40 dark:to-pink-950/40 shadow-lg" 
            : isHovered
            ? "border-purple-300 bg-gradient-to-br from-purple-50/50 to-pink-50/50 dark:from-purple-950/20 dark:to-pink-950/20 hover:shadow-md"
            : isOtherCardHovered
            ? "border-purple-200 bg-gradient-to-br from-purple-50/30 to-pink-50/30 dark:from-purple-950/10 dark:to-pink-950/10 opacity-60"
            : "border-purple-200 bg-gradient-to-br from-purple-50/50 to-pink-50/50 dark:from-purple-950/20 dark:to-pink-950/20 hover:border-purple-300 hover:shadow-md",
          iconBg: "from-purple-500/20 to-pink-500/20",
          icon: "text-purple-600 dark:text-purple-400",
          name: "Create a professional business advertisement"
        };
      case "automate_workflow":
        return {
          card: isSelected 
            ? "border-orange-400 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950/40 dark:to-red-950/40 shadow-lg" 
            : isHovered
            ? "border-orange-300 bg-gradient-to-br from-orange-50/50 to-red-50/50 dark:from-orange-950/20 dark:to-red-950/20 hover:shadow-md"
            : isOtherCardHovered
            ? "border-orange-200 bg-gradient-to-br from-orange-50/30 to-red-50/30 dark:from-orange-950/10 dark:to-red-950/10 opacity-60"
            : "border-orange-200 bg-gradient-to-br from-orange-50/50 to-red-50/50 dark:from-orange-950/20 dark:to-red-950/20 hover:border-orange-300 hover:shadow-md",
          iconBg: "from-orange-500/20 to-red-500/20",
          icon: "text-orange-600 dark:text-orange-400",
          name: "Automate a content creation workflow"
        };
      default:
        return {
          card: isSelected 
            ? "border-primary bg-primary/5 shadow-lg" 
            : isHovered
            ? "border-primary/50 hover:shadow-md"
            : isOtherCardHovered
            ? "border-border opacity-60"
            : "border-border hover:border-primary/50 hover:shadow-md",
          iconBg: "from-muted-foreground/20 to-muted-foreground/20",
          icon: "text-muted-foreground"
        };
    }
  };

  const styles = getCardStyles();

  const getIcon = () => {
    switch (type) {
      case "music_video_clip":
        return <Music className={`w-9 h-9 ${styles.icon}`} strokeWidth={2.2} />;
      case "video_clip":
        return <PlayCircle className={`w-9 h-9 ${styles.icon}`} strokeWidth={2.2} />;
      case "business_ad":
        return <BadgeDollarSign className={`w-9 h-9 ${styles.icon}`} strokeWidth={2.2} />;
      case "automate_workflow":
        return <Loader2 className={`w-9 h-9 animate-spin-slow ${styles.icon}`} strokeWidth={2.2} />;
      default:
        return icon;
    }
  };

  if (variant === "line") {
    return (
      <div
        className={`relative flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all duration-300 ${styles.card}`}
        onClick={onClick}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      >
        {isSelected && (
          <div className="absolute -top-2 -right-2 w-5 h-5 bg-primary rounded-full flex items-center justify-center shadow-lg z-10">
            <div className="w-1.5 h-1.5 bg-background rounded-full"></div>
          </div>
        )}

        <div className={`flex-shrink-0 w-14 h-14 bg-gradient-to-br ${styles.iconBg} rounded-lg flex items-center justify-center`}>
          <span className={`text-2xl ${styles.icon}`}>{icon}</span>
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-base text-foreground truncate mb-1">{title}</h3>
          <p className="text-xs text-muted-foreground line-clamp-2">{description}</p>
        </div>

        <div className="absolute inset-0 bg-black/0 hover:bg-black/5 transition-colors rounded-xl pointer-events-none"></div>
      </div>
    );
  }

  return (
    <div
      className={`relative p-6 rounded-2xl border-2 cursor-pointer transition-all duration-300 ${styles.card}`}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {isSelected && (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center shadow-lg z-10">
          <div className="w-2 h-2 bg-background rounded-full"></div>
        </div>
      )}
      <div className="space-y-4">
        <div className="relative">
          <div className={`w-full h-24 bg-gradient-to-br ${styles.iconBg} rounded-xl flex items-center justify-center`}>
            {getIcon()}
          </div>
        </div>
        <div className="space-y-2">
          <h3 className="font-bold text-lg text-foreground">{title}</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
        </div>
        <div className="absolute inset-0 bg-black/0 hover:bg-black/5 transition-colors rounded-2xl pointer-events-none"></div>
      </div>
    </div>
  );
}
