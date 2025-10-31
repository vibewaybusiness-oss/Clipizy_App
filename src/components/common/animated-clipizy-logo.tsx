'use client';

import { cn } from "@/lib/utils";

interface AnimatedClipizyLogoProps {
  state?: 'idle' | 'loading' | 'success' | 'error';
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export function AnimatedClipizyLogo({ 
  state = 'idle', 
  size = 'medium',
  className 
}: AnimatedClipizyLogoProps) {
  const sizeClasses = {
    small: 'w-8 h-8',
    medium: 'w-12 h-12',
    large: 'w-16 h-16'
  };

  return (
    <div className={cn("relative", sizeClasses[size], className)}>
      <svg
        viewBox="0 0 512 512"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
      >
        <defs>
          {/* Gradients for different states */}
          <linearGradient id="idleGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#66b4f6" />
            <stop offset="100%" stopColor="#9275cf" />
          </linearGradient>

          <linearGradient id="loadingGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#66b4f6" />
            <stop offset="50%" stopColor="#9275cf" />
            <stop offset="100%" stopColor="#66b4f6" />
          </linearGradient>

          <linearGradient id="successGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>

          <linearGradient id="errorGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="100%" stopColor="#dc2626" />
          </linearGradient>

          <linearGradient id="waveGradient" x1="0%" y1="50%" x2="100%" y2="50%">
            <stop offset="0%" stopColor="#66b4f6" />
            <stop offset="100%" stopColor="#9275cf" />
          </linearGradient>
        </defs>

        {/* Outer circle with state-based styling */}
        <circle
          cx="256"
          cy="256"
          r="200"
          stroke={
            state === 'success' ? "url(#successGradient)" :
            state === 'error' ? "url(#errorGradient)" :
            state === 'loading' ? "url(#loadingGradient)" :
            "url(#idleGradient)"
          }
          strokeWidth="30"
          fill="none"
          className={cn(
            state === 'idle' && "animate-pulse",
            state === 'loading' && "animate-spin",
            state === 'success' && "animate-pulse"
          )}
          style={{
            animationDuration: state === 'loading' ? '2s' : '1.5s'
          }}
        />

        {/* ECG-like waveform with animation */}
        <g>
          <path
            d="M120 260 L160 260 Q180 200 200 260 L220 360 L250 140 L280 360 L310 200 L330 260 L390 260"
            stroke="url(#waveGradient)"
            strokeWidth="30"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={cn(
              state === 'loading' && "animate-pulse",
              state === 'success' && "animate-pulse"
            )}
            style={{
              strokeDasharray: state === 'loading' ? '10 5' : 'none',
              animationDuration: state === 'loading' ? '1s' : '2s'
            }}
          />
          
          {/* Animated wave overlay for loading state */}
          {state === 'loading' && (
            <path
              d="M120 260 L160 260 Q180 200 200 260 L220 360 L250 140 L280 360 L310 200 L330 260 L390 260"
              stroke="url(#loadingGradient)"
              strokeWidth="25"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="animate-pulse"
              style={{
                strokeDasharray: '20 10',
                animationDuration: '0.8s'
              }}
            />
          )}
        </g>

        {/* Success checkmark */}
        {state === 'success' && (
          <g className="animate-in fade-in-0 zoom-in-50 duration-500">
            <circle
              cx="256"
              cy="256"
              r="180"
              stroke="url(#successGradient)"
              strokeWidth="20"
              fill="none"
              className="animate-pulse"
            />
            <path
              d="M200 256 L240 296 L320 216"
              stroke="url(#successGradient)"
              strokeWidth="40"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="animate-in fade-in-0 slide-in-from-left-4 duration-700 delay-300"
            />
          </g>
        )}

        {/* Error X */}
        {state === 'error' && (
          <g className="animate-in fade-in-0 zoom-in-50 duration-500">
            <circle
              cx="256"
              cy="256"
              r="180"
              stroke="url(#errorGradient)"
              strokeWidth="20"
              fill="none"
              className="animate-pulse"
            />
            <g className="animate-in fade-in-0 slide-in-from-left-4 duration-700 delay-300">
              <path
                d="M200 200 L312 312"
                stroke="url(#errorGradient)"
                strokeWidth="40"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M312 200 L200 312"
                stroke="url(#errorGradient)"
                strokeWidth="40"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </g>
          </g>
        )}

        {/* Pulsing dots for loading state */}
        {state === 'loading' && (
          <g className="animate-pulse">
            <circle
              cx="100"
              cy="100"
              r="8"
              fill="url(#loadingGradient)"
              className="animate-ping"
              style={{ animationDelay: '0s' }}
            />
            <circle
              cx="412"
              cy="100"
              r="8"
              fill="url(#loadingGradient)"
              className="animate-ping"
              style={{ animationDelay: '0.3s' }}
            />
            <circle
              cx="100"
              cy="412"
              r="8"
              fill="url(#loadingGradient)"
              className="animate-ping"
              style={{ animationDelay: '0.6s' }}
            />
            <circle
              cx="412"
              cy="412"
              r="8"
              fill="url(#loadingGradient)"
              className="animate-ping"
              style={{ animationDelay: '0.9s' }}
            />
          </g>
        )}
      </svg>
    </div>
  );
}
