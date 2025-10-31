"use client";

import React, { useEffect, useState, useCallback } from 'react';
import { BrickInstance } from '@/types/bricks';
import type { WorkflowContext } from '@/types/workflow';
import { LLMBrickComponent } from '../bricks/LLMBrick';
import { UserInputBrickComponent } from '../bricks/UserInputBrick';
import { BackgroundBrickComponent } from '../bricks/BackgroundBrick';
import { JSONDisplayBrickComponent } from '../bricks/JSONDisplayBrick';
import { BackendCallBrickComponent } from '../bricks/BackendCallBrick';
import { WaitingDisplayBrickComponent } from '../bricks/WaitingDisplayBrick';
import { MediaDisplayBrickComponent } from '../bricks/MediaDisplayBrick';
import { ConfirmationBrickComponent } from '../bricks/ConfirmationBrick';
import { BatchMediaDisplayBrickComponent } from '../bricks/BatchMediaDisplayBrick';

interface BrickRendererProps {
  brick: BrickInstance;
  onAction?: (brickId: string, action: string, data: any) => void;
  onComplete?: (brickId: string, result: any) => void;
  onError?: (brickId: string, error: Error) => void;
  context: WorkflowContext;
}

export function BrickRenderer({
  brick,
  onAction,
  onComplete,
  onError,
  context
}: BrickRendererProps) {
  // Never render silent backend bricks
  if (brick.type === 'background') {
    return null;
  }

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleComplete = useCallback((result: any) => {
    setIsLoading(false);
    setError(null);
    onComplete?.(brick.id, result);
  }, [brick.id, onComplete]);

  const handleError = useCallback((err: Error) => {
    setIsLoading(false);
    setError(err.message);
    onError?.(brick.id, err);
  }, [brick.id, onError]);

  const handleAction = useCallback((action: string, data: any) => {
    onAction?.(brick.id, action, data);
  }, [brick.id, onAction]);

  const renderBrickComponent = () => {
    switch (brick.type) {
      case 'llm':
        return (
          <LLMBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      case 'user_input':
        return (
          <UserInputBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      case 'api_call':
        return (
          <BackendCallBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      case 'background':
        return (
          <BackgroundBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      case 'json_display':
        return (
          <JSONDisplayBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      case 'backend_call':
        return (
          <BackendCallBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      case 'waiting_display':
        return (
          <WaitingDisplayBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      case 'media_display':
        return (
          <MediaDisplayBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      case 'confirmation':
        return (
          <ConfirmationBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      case 'batch_media_display':
        return (
          <BatchMediaDisplayBrickComponent
            brick={brick as any}
            onComplete={handleComplete}
            onError={handleError}
            context={context}
          />
        );
      
      default:
        return (
          <div className="p-4 border border-destructive rounded-lg bg-destructive/10">
            <p className="text-destructive text-sm">
              Unknown brick type: {brick.type}
            </p>
          </div>
        );
    }
  };

  if (error) {
    return (
      <div className="p-4 border border-destructive rounded-lg bg-destructive/10">
        <p className="text-destructive text-sm">
          Error in {brick.type} brick: {error}
        </p>
        <button
          onClick={() => {
            setError(null);
            setIsLoading(true);
            brick.execute().then(handleComplete).catch(handleError);
          }}
          className="mt-2 text-xs text-destructive hover:underline"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="brick-renderer">
      {renderBrickComponent()}
    </div>
  );
}
