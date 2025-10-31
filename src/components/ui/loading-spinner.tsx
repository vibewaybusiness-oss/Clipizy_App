"use client";

import React from 'react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  color?: 'primary' | 'white' | 'muted';
}

const sizeClasses = {
  sm: 'w-3 h-3',
  md: 'w-4 h-4',
  lg: 'w-6 h-6'
};

const colorClasses = {
  primary: 'border-primary border-t-transparent',
  white: 'border-white border-t-transparent',
  muted: 'border-muted-foreground border-t-transparent'
};

export function LoadingSpinner({ 
  size = 'md', 
  className,
  color = 'primary'
}: LoadingSpinnerProps) {
  return (
    <div 
      className={cn(
        'border-2 rounded-full animate-spin',
        sizeClasses[size],
        colorClasses[color],
        className
      )}
    />
  );
}
