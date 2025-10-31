"use client";

import React, { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";

interface HintMessageProps {
  children: React.ReactNode;
  content: string;
  position?: "top" | "bottom" | "left" | "right";
  align?: "start" | "center" | "end";
  className?: string;
}

export function HintMessage({ 
  children, 
  content, 
  position = "bottom", 
  align = "center",
  className = ""
}: HintMessageProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const updateTooltipPosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let top = 0;
    let left = 0;

    // Calculate position based on trigger element
    switch (position) {
      case "top":
        top = triggerRect.top - tooltipRect.height - 8;
        break;
      case "bottom":
        top = triggerRect.bottom + 8;
        break;
      case "left":
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.left - tooltipRect.width - 8;
        break;
      case "right":
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + 8;
        break;
    }

    // Calculate horizontal alignment
    switch (align) {
      case "start":
        if (position === "top" || position === "bottom") {
          left = triggerRect.left;
        }
        break;
      case "center":
        if (position === "top" || position === "bottom") {
          left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        }
        break;
      case "end":
        if (position === "top" || position === "bottom") {
          left = triggerRect.right - tooltipRect.width;
        }
        break;
    }

    // Ensure tooltip stays within viewport bounds
    if (left < 8) left = 8;
    if (left + tooltipRect.width > viewportWidth - 8) {
      left = viewportWidth - tooltipRect.width - 8;
    }
    if (top < 8) top = 8;
    if (top + tooltipRect.height > viewportHeight - 8) {
      top = viewportHeight - tooltipRect.height - 8;
    }

    setTooltipPosition({ top, left });
  };

  useEffect(() => {
    if (isVisible) {
      updateTooltipPosition();
      
      const handleResize = () => updateTooltipPosition();
      const handleScroll = () => updateTooltipPosition();
      
      window.addEventListener('resize', handleResize);
      window.addEventListener('scroll', handleScroll, true);
      
      return () => {
        window.removeEventListener('resize', handleResize);
        window.removeEventListener('scroll', handleScroll, true);
      };
    }
  }, [isVisible, position, align]);

  const handleMouseEnter = () => {
    setIsVisible(true);
  };

  const handleMouseLeave = () => {
    setIsVisible(false);
  };

  const tooltipContent = (
    <div
      ref={tooltipRef}
      className={`fixed z-[99999] px-4 py-3 bg-slate-700 text-white text-xs rounded-lg shadow-xl border border-slate-700 transition-all duration-200 pointer-events-none w-64 max-w-[calc(100vw-2rem)] ${
        isVisible ? 'opacity-100' : 'opacity-0'
      } ${className}`}
      style={{
        top: tooltipPosition.top,
        left: tooltipPosition.left,
      }}
    >
      {content}
      {/* Arrow pointing to trigger element */}
      <div 
        className={`absolute w-0 h-0 border-4 border-transparent ${
          position === "top" ? "top-full left-1/2 transform -translate-x-1/2 border-t-slate-700" :
          position === "bottom" ? "bottom-full left-1/2 transform -translate-x-1/2 border-b-slate-700" :
          position === "left" ? "left-full top-1/2 transform -translate-y-1/2 border-l-slate-700" :
          "right-full top-1/2 transform -translate-y-1/2 border-r-slate-700"
        }`}
      />
    </div>
  );

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="inline-block"
      >
        {children}
      </div>
      {isVisible && createPortal(tooltipContent, document.body)}
    </>
  );
}


