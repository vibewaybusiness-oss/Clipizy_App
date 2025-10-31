"use client";

import React from "react";

interface VideoTypeCardProps {
  id: string;
  name: string;
  description: string;
  icon: string;
  gradient: string;
  isSelected: boolean;
  onClick: () => void;
  hoveredCardId?: string | null;
  onHover?: (cardId: string | null) => void;
}

export function VideoTypeCard({
  id,
  name,
  description,
  icon,
  gradient,
  isSelected,
  onClick,
  hoveredCardId,
  onHover
}: VideoTypeCardProps) {
  const isHovered = hoveredCardId === id;
  const isOtherCardHovered = hoveredCardId !== null && hoveredCardId !== id;

  const getCardStyles = () => {
    switch (id) {
      case "looped-static":
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
          name: "A single static image that loops throughout the entire video duration."
        };
      case "looped-animated":
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
          name: "A seamless animated loop that repeats continuously."
        };
      case "recurring-scenes":
        return {
          card: isSelected 
            ? "border-indigo-400 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-950/40 dark:to-purple-950/40 shadow-lg" 
            : isHovered
            ? "border-indigo-300 bg-gradient-to-br from-indigo-50/50 to-purple-50/50 dark:from-indigo-950/20 dark:to-purple-950/20 hover:shadow-md"
            : isOtherCardHovered
            ? "border-indigo-200 bg-gradient-to-br from-indigo-50/30 to-purple-50/30 dark:from-indigo-950/10 dark:to-purple-950/10 opacity-60"
            : "border-indigo-200 bg-gradient-to-br from-indigo-50/50 to-purple-50/50 dark:from-indigo-950/20 dark:to-purple-950/20 hover:border-indigo-300 hover:shadow-md",
          iconBg: "from-indigo-500/20 to-purple-500/20",
          icon: "text-indigo-600 dark:text-indigo-400",
          name: "Multiple scenes that repeat in a pattern throughout the video."
        };
      case "scenes":
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
          name: "A complete production with unique scenes that change throughout the video."
        };
    }
  };

  const styles = getCardStyles();

  return (
    <div
      className={`relative p-6 rounded-2xl border-2 cursor-pointer transition-all duration-300 ${styles.card}`}
      onClick={onClick}
      onMouseEnter={() => onHover?.(id)}
      onMouseLeave={() => onHover?.(null)}
    >
      {/* Selection indicator */}
      {isSelected && (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center shadow-lg">
          <div className="w-2 h-2 bg-background rounded-full"></div>
        </div>
      )}

      <div className="space-y-4">
        {/* Icon section */}
        <div className="relative">
          <div className={`w-full h-24 bg-gradient-to-br ${styles.iconBg} rounded-xl flex items-center justify-center mb-4`}>
            <span className={`text-3xl ${styles.icon}`}>{icon}</span>
          </div>
        </div>

        {/* Content section */}
        <div className="space-y-3">
          <h3 className="font-bold text-lg text-foreground">{name}</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
        </div>

        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black/0 hover:bg-black/5 transition-colors rounded-2xl pointer-events-none"></div>
      </div>
    </div>
  );
}
