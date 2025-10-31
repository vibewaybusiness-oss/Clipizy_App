"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { BrickInstance, BrickExecutionResult } from '@/types/bricks';
import { BrickConfig, BrickContext, MediaDisplayBrickConfig } from '@/types/workflow';
import { brickEventEmitter } from './BrickEventEmitter';
import { Button } from '@/components/ui/button';
import { Play, Pause, Volume2, Download, RotateCcw } from 'lucide-react';

export class MediaDisplayBrick implements BrickInstance {
  public id: string;
  public type: string = 'media_display';
  public config: MediaDisplayBrickConfig;
  public context: BrickContext;

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as MediaDisplayBrickConfig;
    this.context = context;
  }

  private resolveDataPath(path: string): any {
    const cleanPath = path.replace(/^workflowData\./, '');
    const keys = cleanPath.split('.');
    let value = this.context.workflowData;
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return undefined;
      }
    }
    
    return value;
  }

  private interpolateTemplate(template: string): string {
    return template.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
      const value = this.resolveDataPath(path.trim());
      return value !== undefined ? String(value) : match;
    });
  }

  public async execute(): Promise<BrickExecutionResult> {
    try {
      const mediaUrl = this.resolveDataPath(this.config.dataSource);
      
      if (!mediaUrl) {
        return {
          success: false,
          error: new Error(`No media URL found at ${this.config.dataSource}`)
        };
      }

      brickEventEmitter.emitComplete(this.id, undefined, { mediaUrl });

      return {
        success: true,
        data: { mediaUrl }
      };
    } catch (error) {
      return {
        success: false,
        error: error as Error
      };
    }
  }

  public validate(): boolean | string {
    if (!this.config.dataSource) {
      return 'Data source is required';
    }
    if (!this.config.mediaType) {
      return 'Media type is required';
    }
    return true;
  }

  public reset(): void {
    // No state to reset
  }

  public destroy(): void {
    // No cleanup needed
  }

  public getState(): any {
    return {};
  }
}

export const MediaDisplayBrickComponent: React.FC<{
  brick: MediaDisplayBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [mediaUrl, setMediaUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = React.useRef<HTMLAudioElement>(null);
  const videoRef = React.useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const executeAndDisplay = async () => {
      try {
        const result = await brick.execute();
        if (result.success) {
          setMediaUrl(result.data.mediaUrl);
        } else {
          onError(result.error || new Error('Failed to load media'));
        }
      } catch (error) {
        onError(error as Error);
      }
    };

    executeAndDisplay();
  }, [brick]);

  const handleAction = useCallback((action: any) => {
    if (action.nextStep) {
      brick.context.setStep(action.nextStep);
    }
    
    if (action.triggerBrick) {
      // Trigger another brick (e.g., regenerate)
      onComplete({ action: action.action, triggerBrick: action.triggerBrick });
    } else {
      onComplete({ action: action.action });
    }
  }, [brick, onComplete]);

  const togglePlay = useCallback(() => {
    const media = brick.config.mediaType === 'audio' ? audioRef.current : videoRef.current;
    if (!media) return;

    if (isPlaying) {
      media.pause();
    } else {
      media.play();
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying, brick.config.mediaType]);

  const cfg = brick.config as MediaDisplayBrickConfig;

  if (!mediaUrl) {
    return null;
  }

  const title = cfg.metadata?.title ? brick.interpolateTemplate(cfg.metadata.title) : undefined;
  const description = cfg.metadata?.description ? brick.interpolateTemplate(cfg.metadata.description) : undefined;

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-card">
      {/* Metadata */}
      {(title || description) && (
        <div className="space-y-1">
          {title && <h3 className="font-medium">{title}</h3>}
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
      )}

      {/* Media Player */}
      <div className="space-y-3">
        {cfg.mediaType === 'audio' && (
          <div className="space-y-3">
            <audio
              ref={audioRef}
              src={mediaUrl}
              className="w-full"
              controls={cfg.controls?.play !== false}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
            />
          </div>
        )}

        {cfg.mediaType === 'video' && (
          <video
            ref={videoRef}
            src={mediaUrl}
            className="w-full rounded-lg"
            controls={cfg.controls?.play !== false}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
          />
        )}

        {cfg.mediaType === 'image' && (
          <img
            src={mediaUrl}
            alt={title || 'Generated image'}
            className="w-full rounded-lg"
          />
        )}
      </div>

      {/* Actions */}
      {cfg.actions && cfg.actions.length > 0 && (
        <div className="flex gap-2">
          {cfg.actions.map((action, idx) => {
            const Icon = action.icon === 'refresh' ? RotateCcw : 
                        action.icon === 'download' ? Download : null;

            return (
              <Button
                key={idx}
                variant={action.variant || 'default'}
                onClick={() => handleAction(action)}
              >
                {Icon && <Icon className="w-4 h-4 mr-2" />}
                {action.label}
              </Button>
            );
          })}
        </div>
      )}
    </div>
  );
};

