"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

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
          scale: [1, 1.05, 1]
        }}
        transition={{ 
          scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
        }}
      >
        {/* Custom ECG-style animated logo */}
        <svg
          viewBox="0 0 512 512"
          className="w-full h-full"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
        >
          <defs>
            {/* Gradient for outer ring */}
            <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#66b4f6" />
              <stop offset="100%" stopColor="#9275cf" />
            </linearGradient>

            {/* Gradient for waveform */}
            <linearGradient id="waveGradient" x1="0%" y1="50%" x2="100%" y2="50%">
              <stop offset="0%" stopColor="#66b4f6" />
              <stop offset="100%" stopColor="#9275cf" />
            </linearGradient>
          </defs>

          {/* Outer circle */}
          <circle
            cx="256"
            cy="256"
            r="200"
            stroke="url(#ringGradient)"
            strokeWidth="30"
            fill="none"
          />

          {/* ECG-style animated waveform */}
          <motion.path
            d="M120 260 L160 260 Q180 200 200 260 L220 360 L250 140 L280 360 L310 200 L330 260 L390 260"
            stroke="url(#waveGradient)"
            strokeWidth="30"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
              repeatType: "reverse"
            }}
          />
          
          {/* ECG pulse effect - moving dot */}
          <motion.circle
            cx="120"
            cy="260"
            r="8"
            fill="#66b4f6"
            animate={{
              x: [0, 270, 0],
              opacity: [1, 0.3, 1]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </svg>
        
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-primary/30"
          animate={{
            scale: [1, 1.3, 1],
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
            scale: [1, 1.6, 1],
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
    <div className={`fixed inset-0 bg-black/90 backdrop-blur-sm z-[70] flex items-center justify-center ${className}`}>
      <div className="bg-card border border-border rounded-lg p-8 shadow-lg">
        <ClipizyLoading message={message} size={size} />
      </div>
    </div>
  );
}
