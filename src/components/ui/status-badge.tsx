"use client";

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: 'pending' | 'generated' | 'validated' | 'error' | 'loading';
  className?: string;
}

const statusConfig = {
  pending: {
    variant: 'secondary' as const,
    className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    text: 'Pending'
  },
  generated: {
    variant: 'secondary' as const,
    className: 'bg-blue-100 text-blue-800 border-blue-200',
    text: 'Generated'
  },
  validated: {
    variant: 'secondary' as const,
    className: 'bg-green-100 text-green-800 border-green-200',
    text: 'Validated'
  },
  error: {
    variant: 'destructive' as const,
    className: 'bg-red-100 text-red-800 border-red-200',
    text: 'Error'
  },
  loading: {
    variant: 'secondary' as const,
    className: 'bg-gray-100 text-gray-800 border-gray-200',
    text: 'Loading'
  }
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status];
  
  return (
    <Badge 
      variant={config.variant}
      className={cn(
        'text-xs px-2 py-1',
        config.className,
        className
      )}
    >
      {config.text}
    </Badge>
  );
}
