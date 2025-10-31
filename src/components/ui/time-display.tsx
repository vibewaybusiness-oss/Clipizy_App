"use client";

import React from 'react';
import { formatTime, formatTimeWithHours } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface TimeDisplayProps {
  seconds: number;
  showHours?: boolean;
  className?: string;
  variant?: 'default' | 'badge' | 'inline';
}

export function TimeDisplay({ 
  seconds, 
  showHours = false, 
  className,
  variant = 'default'
}: TimeDisplayProps) {
  const formattedTime = showHours ? formatTimeWithHours(seconds) : formatTime(seconds);
  
  if (variant === 'badge') {
    return (
      <span className={cn(
        'font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full text-xs',
        className
      )}>
        {formattedTime}
      </span>
    );
  }
  
  if (variant === 'inline') {
    return (
      <span className={cn('text-sm text-muted-foreground', className)}>
        {formattedTime}
      </span>
    );
  }
  
  return (
    <span className={cn('text-sm', className)}>
      {formattedTime}
    </span>
  );
}
