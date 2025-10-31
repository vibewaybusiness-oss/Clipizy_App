"use client";

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Music, Trash2, Clock } from 'lucide-react';
import type { MusicTrack } from '@/types/domains';
import { useAudio } from '@/contexts/AudioContext';
import { formatTimeWithHours, truncateText } from '@/lib/utils';
import { AudioControls } from '@/components/ui/audio-controls';

interface TrackCardProps {
  track: MusicTrack;
  isSelected: boolean;
  isPlaying: boolean;
  hasDescription?: boolean;
  onSelect: (track: MusicTrack, event?: React.MouseEvent) => void;
  onPlayPause: (track: MusicTrack) => void;
  onRemove: (trackId: string) => void;
  selectionIndex?: number;
  totalSelected?: number;
  onDragStart?: (e: React.DragEvent, track: MusicTrack) => void;
  onDragOver?: (e: React.DragEvent, track: MusicTrack) => void;
  onDrop?: (e: React.DragEvent, track: MusicTrack) => void;
  onDragEnd?: () => void;
  isDragging?: boolean;
  isDragOver?: boolean;
  dropPosition?: 'above' | 'below' | null;
  alwaysShowActions?: boolean;
  isUploading?: boolean;
}

export function TrackCard({
  track,
  isSelected,
  isPlaying,
  hasDescription = false,
  onSelect,
  onPlayPause,
  onRemove,
  selectionIndex,
  totalSelected = 0,
  onDragStart,
  onDragOver,
  onDrop,
  onDragEnd,
  isDragging = false,
  isDragOver = false,
  dropPosition = null,
  alwaysShowActions = false,
  isUploading = false
}: TrackCardProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const titleRef = useRef<HTMLDivElement>(null);

  // Use centralized audio management
  const { currentlyPlayingId, isPlaying: contextIsPlaying } = useAudio();

  const handleTitleMouseEnter = () => {
    if (titleRef.current && titleRef.current.scrollWidth > titleRef.current.clientWidth) {
      setIsHovering(true);
      hoverTimeoutRef.current = setTimeout(() => {
        setShowTooltip(true);
      }, 500);
    }
  };

  const handleTitleMouseLeave = () => {
    setIsHovering(false);
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
      hoverTimeoutRef.current = null;
    }
    setShowTooltip(false);
  };

  // Use shared utility function

  return (
    <div className="relative">
      {/* Drop indicator line above */}
      {dropPosition === 'above' && (
        <div className="absolute -top-1 left-0 right-0 h-0.5 bg-primary rounded-full z-10 ">
          <div className="absolute -left-1 -top-1 w-2 h-2 bg-primary rounded-full"></div>
          <div className="absolute -right-1 -top-1 w-2 h-2 bg-primary rounded-full"></div>
        </div>
      )}

      <div
        className={`p-1.5 sm:p-2 lg:p-2.5 rounded-lg border cursor-pointer transition-all duration-200 group relative ${
          isSelected
            ? 'border-primary/60 bg-gradient-to-r from-primary/5 to-primary/10 ring-2 ring-primary/30 '
            : 'border-border/60 hover:border-primary/40 hover:bg-gradient-to-r hover:from-primary/3 hover:to-primary/8 '
        } ${
          isDragging ? 'opacity-50 scale-95' : ''
        } ${
          isDragOver ? 'border-primary/80 bg-primary/10 ring-2 ring-primary/40' : ''
        }`}
        onClick={(e) => onSelect(track, e)}
        draggable
        onDragStart={(e) => onDragStart?.(e, track)}
        onDragOver={(e) => {
          e.preventDefault();
          onDragOver?.(e, track);
        }}
        onDrop={(e) => onDrop?.(e, track)}
        onDragEnd={onDragEnd}
      >
      <div className="space-y-1 sm:space-y-1.5">
        {/* Header Row */}
        <div className="flex items-start space-x-1.5 sm:space-x-2 lg:space-x-3">
          <div className={`w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 rounded-md flex items-center justify-center flex-shrink-0 transition-all duration-200 ${
            hasDescription
              ? 'bg-gradient-to-br from-green-500 to-green-600 text-white border-2 border-green-400 '
              : isSelected
                ? 'bg-gradient-to-br from-primary to-primary/80 text-primary-foreground '
                : 'bg-gradient-to-br from-muted to-muted/80 text-foreground/70 group-hover:from-primary/20 group-hover:to-primary/30 group-hover:text-primary'
          }`}>
            <Music className="w-3 h-3 sm:w-3.5 sm:h-3.5 lg:w-4 lg:h-4" />
          </div>

          <div className="flex-1 min-w-0">
            {/* Title Row */}
            <div className="flex items-center justify-between mb-0.5">
              <div className="flex items-center space-x-1 min-w-0 flex-1">
                <div className="relative flex-1 min-w-0">
                  <h3
                    ref={titleRef}
                    className="font-semibold text-foreground text-xs sm:text-sm lg:text-base truncate flex-1 cursor-default"
                    onMouseEnter={handleTitleMouseEnter}
                    onMouseLeave={handleTitleMouseLeave}
                    title=""
                  >
                    {truncateText(track.name)}
                  </h3>
                  {showTooltip && (
                    <div className="absolute bottom-full left-0 mb-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg  z-50 whitespace-nowrap max-w-xs">
                      {track.name || 'Untitled Track'}
                      <div className="absolute top-full left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                    </div>
                  )}
                </div>
                {/* No audio content indicator */}
                {!track.url && (!track.file || track.file.size === 0) && (
                  <div className="px-1 py-0.5 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium flex-shrink-0">
                    No Audio
                  </div>
                )}
                {/* Multi-selection indicator inline with title */}
                {isSelected && totalSelected > 1 && selectionIndex !== undefined && (
                  <div className="w-3.5 h-3.5 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
                    {selectionIndex + 1}
                  </div>
                )}
              </div>
            </div>

            {/* Metadata Row */}
            <div className="flex items-center space-x-1.5 sm:space-x-2 lg:space-x-3">
              <div className="flex items-center space-x-0.5 text-xs text-foreground/70">
                <Clock className="w-2.5 h-2.5 sm:w-3 sm:h-3" />
                <span>{formatTimeWithHours(track.duration)}</span>
              </div>

              {track.genre && (
                <div className="px-1 py-0.5 bg-gradient-to-r from-primary/10 to-primary/20 text-primary rounded-full text-xs font-semibold border border-primary/20 max-w-[60px] sm:max-w-[80px] lg:max-w-[100px]">
                  <span className="truncate block">{track.genre}</span>
                </div>
              )}
            </div>
          </div>

          {/* Action buttons - always positioned on the right */}
          <div className={`flex items-center space-x-0.5 transition-opacity flex-shrink-0 ${
            alwaysShowActions ? 'opacity-100' : 'opacity-0 group-hover:opacity-100 dark:opacity-100'
          }`}>
            <AudioControls 
              track={track} 
              size="sm"
              className="h-5 w-5 sm:h-6 sm:w-6 lg:h-7 lg:w-7"
            />
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onRemove(track.id);
              }}
              className="h-5 w-5 sm:h-6 sm:w-6 lg:h-7 lg:w-7 p-0 text-destructive hover:text-destructive hover:bg-destructive/20 rounded-md"
            >
              <Trash2 className="w-2.5 h-2.5 sm:w-3 sm:h-3 lg:w-3.5 lg:h-3.5" />
            </Button>
          </div>
        </div>

        {/* Prompt Display */}
        {track.prompt && (
          <div className="bg-muted/30 rounded-md p-1 sm:p-1.5 lg:p-2 border border-border/50">
            <div className="flex items-start space-x-1">
              <div className="w-1 h-1 bg-primary rounded-full mt-1 flex-shrink-0"></div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-foreground/70 mb-0.5">AI Prompt:</p>
                <p className="text-xs text-foreground leading-relaxed italic">
                  "{track.prompt}"
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
      </div>

      {/* Drop indicator line below */}
      {dropPosition === 'below' && (
        <div className="absolute -bottom-1 left-0 right-0 h-0.5 bg-primary rounded-full z-10 ">
          <div className="absolute -left-1 -top-1 w-2 h-2 bg-primary rounded-full"></div>
          <div className="absolute -right-1 -top-1 w-2 h-2 bg-primary rounded-full"></div>
        </div>
      )}

    </div>
  );
}
