"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { BrickInstance, BrickExecutionResult } from '@/types/bricks';
import { BrickConfig, BrickContext, BatchMediaDisplayBrickConfig } from '@/types/workflow';
import { brickEventEmitter } from './BrickEventEmitter';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Play, Pause, CheckCircle, RotateCcw, Edit2, Save, Loader2 } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface MediaItem {
  id: string;
  type: 'text' | 'image' | 'audio' | 'video';
  content: string; // URL for media, text content for text
  status: 'generating' | 'ready' | 'validated' | 'regenerating';
  editedContent?: string;
  isEditing?: boolean;
  generationPrice?: number;
}

export class BatchMediaDisplayBrick implements BrickInstance {
  public id: string;
  public type: string = 'batch_media_display';
  public config: BatchMediaDisplayBrickConfig;
  public context: BrickContext;
  private mediaItems: MediaItem[] = [];
  private currentGenerationIndex: number = 0;
  private allValidated: boolean = false;

  constructor(config: BrickConfig, context: BrickContext) {
    this.id = config.id;
    this.config = config as BatchMediaDisplayBrickConfig;
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
      // Handle pricing variables like {{$image_generation_price}}
      if (path.trim().startsWith('$')) {
        const pricingKey = path.trim().substring(1);
        const pricing = this.context.workflowData.pricing || {};
        return String(pricing[pricingKey] || '0');
      }
      
      const value = this.resolveDataPath(path.trim());
      return value !== undefined ? String(value) : match;
    });
  }

  private async generateMediaItem(index: number): Promise<MediaItem> {
    const generationConfig = this.config.generations[index];
    
    // Call backend to generate media
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    const payload = this.buildPayload(generationConfig);

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(generationConfig.endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const contentPath = generationConfig.contentPath || 'url';
      const content = this.extractFromPath(data, contentPath);

      const mediaItem: MediaItem = {
        id: `${this.id}-media-${index}`,
        type: generationConfig.mediaType,
        content,
        status: 'ready',
        generationPrice: generationConfig.regenerationPrice 
          ? parseFloat(this.interpolateTemplate(generationConfig.regenerationPrice))
          : undefined
      };

      return mediaItem;
    } catch (error) {
      throw new Error(`Failed to generate ${generationConfig.mediaType}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private buildPayload(generationConfig: any): any {
    if (!generationConfig.payload) return {};

    const result: any = {};
    for (const [key, value] of Object.entries(generationConfig.payload)) {
      if (typeof value === 'string' && value.includes('{{')) {
        result[key] = this.interpolateTemplate(value);
      } else {
        result[key] = value;
      }
    }
    return result;
  }

  private extractFromPath(obj: any, path: string): any {
    const keys = path.split('.');
    let value = obj;
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return obj;
      }
    }
    
    return value;
  }

  public async execute(): Promise<BrickExecutionResult> {
    try {
      // Initialize media items
      this.mediaItems = this.config.generations.map((gen, idx) => ({
        id: `${this.id}-media-${idx}`,
        type: gen.mediaType,
        content: '',
        status: 'generating' as const,
        generationPrice: gen.regenerationPrice 
          ? parseFloat(this.interpolateTemplate(gen.regenerationPrice))
          : undefined
      }));

      // Generate all media items sequentially
      for (let i = 0; i < this.config.generations.length; i++) {
        this.currentGenerationIndex = i;
        brickEventEmitter.emitData(this.id, {
          type: 'progress',
          currentIndex: i,
          total: this.config.generations.length,
          items: this.mediaItems
        });

        const mediaItem = await this.generateMediaItem(i);
        this.mediaItems[i] = mediaItem;
        
        brickEventEmitter.emitData(this.id, {
          type: 'item_ready',
          index: i,
          item: mediaItem,
          items: this.mediaItems
        });
      }

      brickEventEmitter.emitComplete(this.id, undefined, {
        items: this.mediaItems
      });

      return {
        success: true,
        data: { items: this.mediaItems }
      };
    } catch (error) {
      return {
        success: false,
        error: error as Error
      };
    }
  }

  public async regenerateItem(index: number): Promise<void> {
    this.mediaItems[index].status = 'regenerating';
    brickEventEmitter.emitData(this.id, {
      type: 'item_regenerating',
      index,
      items: this.mediaItems
    });

    try {
      const mediaItem = await this.generateMediaItem(index);
      this.mediaItems[index] = { ...mediaItem, status: 'ready' };
      
      brickEventEmitter.emitData(this.id, {
        type: 'item_ready',
        index,
        item: this.mediaItems[index],
        items: this.mediaItems
      });
    } catch (error) {
      this.mediaItems[index].status = 'ready';
      throw error;
    }
  }

  public validateItem(index: number): void {
    this.mediaItems[index].status = 'validated';
    brickEventEmitter.emitData(this.id, {
      type: 'item_validated',
      index,
      items: this.mediaItems
    });
  }

  public validateAll(): void {
    this.mediaItems.forEach(item => {
      if (item.status === 'ready') {
        item.status = 'validated';
      }
    });
    this.allValidated = true;
    
    // Save to workflow data
    this.context.setData(prev => ({
      ...prev,
      [this.config.saveKey || 'generatedMedia']: this.mediaItems
    }));

    // Navigate to next step if configured
    if (this.config.onComplete?.nextStep) {
      setTimeout(() => {
        this.context.setStep(this.config.onComplete!.nextStep!);
      }, 300);
    }

    brickEventEmitter.emitComplete(this.id, undefined, {
      items: this.mediaItems,
      allValidated: true
    });
  }

  public updateItemContent(index: number, content: string): void {
    if (this.mediaItems[index].type === 'text') {
      this.mediaItems[index].editedContent = content;
    }
  }

  public saveItemEdit(index: number): void {
    if (this.mediaItems[index].editedContent !== undefined) {
      this.mediaItems[index].content = this.mediaItems[index].editedContent!;
      delete this.mediaItems[index].editedContent;
      this.mediaItems[index].isEditing = false;
      this.mediaItems[index].status = 'ready';
    }
  }

  public validate(): boolean | string {
    if (!this.config.generations || this.config.generations.length === 0) {
      return 'At least one generation configuration is required';
    }
    return true;
  }

  public reset(): void {
    this.mediaItems = [];
    this.currentGenerationIndex = 0;
    this.allValidated = false;
  }

  public destroy(): void {
    this.mediaItems = [];
    this.currentGenerationIndex = 0;
    this.allValidated = false;
  }

  public getState(): any {
    return {
      mediaItems: this.mediaItems,
      currentGenerationIndex: this.currentGenerationIndex,
      allValidated: this.allValidated
    };
  }
}

export const BatchMediaDisplayBrickComponent: React.FC<{
  brick: BatchMediaDisplayBrick;
  onComplete: (value: any) => void;
  onError: (error: Error) => void;
  context: import('@/types/workflow').WorkflowContext;
}> = ({ brick, onComplete, onError, context }) => {
  const [mediaItems, setMediaItems] = useState<MediaItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [total, setTotal] = useState(0);
  const [isGenerating, setIsGenerating] = useState(true);
  const [allGenerated, setAllGenerated] = useState(false);

  useEffect(() => {
    const handleData = (data: any) => {
      if (data.type === 'progress') {
        setCurrentIndex(data.currentIndex);
        setTotal(data.total);
        setMediaItems([...data.items]);
      } else if (data.type === 'item_ready' || data.type === 'item_validated' || data.type === 'item_regenerating') {
        setMediaItems([...data.items]);
      }
    };

    const handleComplete = (data: any) => {
      setIsGenerating(false);
      setAllGenerated(true);
      setMediaItems(data.items);
    };

    const subscriptionId = brickEventEmitter.on(`data:${brick.id}`, handleData);
    const completeId = brickEventEmitter.on(`complete:${brick.id}`, handleComplete);

    // Start execution
    brick.execute().catch(onError);

    return () => {
      brickEventEmitter.offById(subscriptionId);
      brickEventEmitter.offById(completeId);
    };
  }, [brick]);

  const handleRegenerate = useCallback(async (index: number) => {
    try {
      await brick.regenerateItem(index);
    } catch (error) {
      onError(error as Error);
    }
  }, [brick, onError]);

  const handleValidate = useCallback((index: number) => {
    brick.validateItem(index);
    const newItems = [...mediaItems];
    newItems[index].status = 'validated';
    setMediaItems(newItems);
  }, [brick, mediaItems]);

  const handleEdit = useCallback((index: number) => {
    const newItems = [...mediaItems];
    newItems[index].isEditing = true;
    newItems[index].editedContent = newItems[index].content;
    setMediaItems(newItems);
  }, [mediaItems]);

  const handleSaveEdit = useCallback((index: number) => {
    brick.saveItemEdit(index);
    const newItems = [...mediaItems];
    newItems[index].isEditing = false;
    setMediaItems(newItems);
  }, [brick, mediaItems]);

  const handleContentChange = useCallback((index: number, content: string) => {
    brick.updateItemContent(index, content);
    const newItems = [...mediaItems];
    newItems[index].editedContent = content;
    setMediaItems(newItems);
  }, [brick, mediaItems]);

  const handleValidateAll = useCallback(() => {
    brick.validateAll();
    const newItems = mediaItems.map(item => ({
      ...item,
      status: item.status === 'ready' ? 'validated' as const : item.status
    }));
    setMediaItems(newItems);
    onComplete({ allValidated: true, items: newItems });
  }, [brick, mediaItems, onComplete]);

  const renderMediaItem = (item: MediaItem, index: number) => {
    const getStatusColor = () => {
      if (item.status === 'validated') return 'border-green-500 bg-green-50/50';
      if (item.status === 'regenerating') return 'border-orange-500 bg-orange-50/50';
      if (item.status === 'generating') return 'border-gray-300 bg-gray-50/50';
      return 'border-blue-300 bg-blue-50/50';
    };

    const cfg = brick.config.generations[index];

    return (
      <div key={item.id} className={`p-4 border-2 rounded-lg ${getStatusColor()} transition-colors duration-300`}>
        {/* Header with label and actions */}
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium">{cfg.label || `${item.type} ${index + 1}`}</h3>
          <div className="flex items-center gap-2">
            {item.status === 'generating' && (
              <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
            )}
            {item.status === 'regenerating' && (
              <Loader2 className="w-4 h-4 animate-spin text-orange-500" />
            )}
            {item.status === 'validated' && (
              <CheckCircle className="w-5 h-5 text-green-600" />
            )}
          </div>
        </div>

        {/* Media Content */}
        {item.status !== 'generating' && (
          <div className="space-y-3">
            {/* Text */}
            {item.type === 'text' && (
              <div className="space-y-2">
                {item.isEditing ? (
                  <Textarea
                    value={item.editedContent || item.content}
                    onChange={(e) => handleContentChange(index, e.target.value)}
                    className="min-h-[100px]"
                  />
                ) : (
                  <div className="p-3 bg-white rounded border text-sm whitespace-pre-wrap">
                    {item.content}
                  </div>
                )}
              </div>
            )}

            {/* Image */}
            {item.type === 'image' && (
              <img
                src={item.content}
                alt={cfg.label || 'Generated image'}
                className="w-full rounded-lg"
              />
            )}

            {/* Audio */}
            {item.type === 'audio' && (
              <audio
                src={item.content}
                controls
                className="w-full"
              />
            )}

            {/* Video */}
            {item.type === 'video' && (
              <video
                src={item.content}
                controls
                className="w-full rounded-lg"
              />
            )}

            {/* Actions */}
            <div className="flex items-center justify-between pt-2 border-t">
              <div className="flex items-center gap-2">
                {item.type === 'text' && !item.isEditing && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleEdit(index)}
                    disabled={item.status === 'regenerating'}
                  >
                    <Edit2 className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                )}
                
                {item.type === 'text' && item.isEditing && (
                  <Button
                    size="sm"
                    variant="default"
                    onClick={() => handleSaveEdit(index)}
                  >
                    <Save className="w-4 h-4 mr-1" />
                    Save
                  </Button>
                )}

                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleRegenerate(index)}
                  disabled={item.status === 'regenerating' || item.status === 'generating'}
                  className="text-orange-600 hover:text-orange-700"
                >
                  <RotateCcw className="w-4 h-4 mr-1" />
                  Regenerate
                  {item.generationPrice && (
                    <span className="ml-1 text-xs">
                      (${item.generationPrice.toFixed(2)})
                    </span>
                  )}
                </Button>

                {item.status !== 'validated' && (
                  <Button
                    size="sm"
                    variant="default"
                    onClick={() => handleValidate(index)}
                    disabled={item.status === 'regenerating' || item.status === 'generating'}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Validate
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Generating placeholder */}
        {item.status === 'generating' && (
          <div className="flex items-center justify-center py-8">
            <div className="text-center space-y-2">
              <Loader2 className="w-8 h-8 animate-spin mx-auto text-gray-400" />
              <p className="text-sm text-muted-foreground">Generating {item.type}...</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const allValidated = mediaItems.every(item => item.status === 'validated');
  const progress = total > 0 ? ((currentIndex + 1) / total) * 100 : 0;

  return (
    <div className="space-y-4">
      {/* Progress Bar */}
      {isGenerating && (
        <div className="space-y-2 p-4 border rounded-lg bg-card">
          <div className="flex items-center justify-between text-sm">
            <span>Generating media items...</span>
            <span>{currentIndex + 1} / {total}</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}

      {/* Media Items */}
      <div className="space-y-4">
        {mediaItems.map((item, index) => renderMediaItem(item, index))}
      </div>

      {/* Validate All Button */}
      {allGenerated && !allValidated && (
        <div className="flex justify-end pt-4">
          <Button
            size="lg"
            onClick={handleValidateAll}
            className="bg-green-600 hover:bg-green-700"
          >
            <CheckCircle className="w-5 h-5 mr-2" />
            Validate All & Continue
          </Button>
        </div>
      )}

      {allGenerated && allValidated && (
        <div className="flex items-center justify-center gap-2 p-4 border border-green-500 rounded-lg bg-green-50">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <span className="text-sm font-medium text-green-700">
            All media validated! Ready to continue.
          </span>
        </div>
      )}
    </div>
  );
};

