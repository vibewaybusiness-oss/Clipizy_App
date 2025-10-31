"use client";

import React, { useCallback, memo } from 'react';
import { Button } from '@/components/ui/button';
import { Play, Pause, Volume2 } from 'lucide-react';
import { useAudio } from '@/contexts/AudioContext';
import { cn } from '@/lib/utils';

interface AudioControlsProps {
  track: any;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const sizeClasses = {
  sm: 'h-6 w-6',
  md: 'h-8 w-8',
  lg: 'h-10 w-10'
};

const iconSizeClasses = {
  sm: 'w-3.5 h-3.5',
  md: 'w-4 h-4',
  lg: 'w-5 h-5'
};

export const AudioControls = memo(function AudioControls({
  track,
  className,
  size = 'md',
  showLabel = false
}: AudioControlsProps) {
  const { playTrack, pauseAll, currentlyPlayingId, isPlaying: contextIsPlaying } = useAudio();

  const handlePlayPause = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    
    // Check if this track is currently playing
    if (currentlyPlayingId === track.id && contextIsPlaying) {
      // Pause the current track
      pauseAll();
    } else {
      // Play this track (this will stop all other audio)
      playTrack(track);
    }
  }, [track, currentlyPlayingId, contextIsPlaying, playTrack, pauseAll]);

  const isPlaying = currentlyPlayingId === track.id && contextIsPlaying;
  const hasAudio = !!(track?.url || (track?.file && track.file.size > 0) || track?.filePath);

  // Debug: Log if component is rendering (removed to prevent loop)
  
  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <div
        onClick={handlePlayPause}
        className={cn(
          'cursor-pointer flex items-center justify-center',
          'text-black dark:text-white',
          'disabled:cursor-not-allowed disabled:opacity-50',
          'transition-colors duration-200',
          !hasAudio && 'cursor-not-allowed opacity-50',
          sizeClasses[size]
        )}
        title={!hasAudio ? "No audio content available" : (isPlaying ? "Pause" : "Play")}
      >
        {isPlaying ? (
          <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
            <rect x="6" y="4" width="4" height="16" rx="1"/>
            <rect x="14" y="4" width="4" height="16" rx="1"/>
          </svg>
        ) : (
          <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
            <polygon points="5,3 19,12 5,21"/>
          </svg>
        )}
      </div>
      
      {showLabel && (
        <span className="text-xs text-muted-foreground">
          {isPlaying ? 'Playing' : 'Paused'}
        </span>
      )}
    </div>
  );
});
