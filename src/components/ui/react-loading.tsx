"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { ClipizyLogo } from '@/components/common/clipizy-logo';

interface ClipizyLoadingProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function ClipizyLoading({ 
  message = 'Loading...', 
  size = 'md',
  className = ''
}: ClipizyLoadingProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className={`flex flex-col items-center justify-center space-y-4 ${className}`}>
      <motion.div
        className={`${sizeClasses[size]} relative`}
        animate={{ 
          rotate: 360,
          scale: [1, 1.1, 1]
        }}
        transition={{ 
          rotate: { duration: 3, repeat: Infinity, ease: "linear" },
          scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
        }}
      >
        <ClipizyLogo className="w-full h-full" />
        
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-primary/30"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        <motion.div
          className="absolute inset-0 rounded-full border border-primary/20"
          animate={{
            scale: [1, 2, 1],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.5
          }}
        />
      </motion.div>
      
      <motion.p
        className={`text-muted-foreground font-medium ${textSizeClasses[size]}`}
        animate={{
          opacity: [0.6, 1, 0.6]
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {message}
      </motion.p>
    </div>
  );
}

export function ClipizyLoadingOverlay({ 
  message = 'Loading...', 
  size = 'lg',
  className = ''
}: ClipizyLoadingProps) {
  return (
    <div className={`fixed inset-0 bg-background/80 backdrop-blur-sm z-[70] flex items-center justify-center ${className}`}>
      <div className="bg-card border border-border rounded-lg p-8 shadow-lg">
        <ClipizyLoading message={message} size={size} />
      </div>
    </div>
  );
}
