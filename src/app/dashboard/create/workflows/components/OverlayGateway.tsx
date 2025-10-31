"use client";

import React, { useEffect, useState, useCallback, useRef } from 'react';
import type { WorkflowContext } from '@/types/workflow';
import { brickEventEmitter } from '../bricks/BrickEventEmitter';
import { GenreSelector } from './GenreSelector';
import { VideoStylesSelector } from './VideoStylesSelector';
import { SelectionModal, SelectionOption } from './SelectionModal';
import { BaseApiClient } from '@/lib/api/base';
import { getBackendUrl } from '@/lib/config';

interface OverlayRequest {
  requestId: string;
  componentId: string;
  props: any;
}

class PromptApiClient extends BaseApiClient {
  constructor() {
    super(getBackendUrl());
  }
}

async function generateMusicPrompt(genre?: string, isInstrumental: boolean = false): Promise<string> {
  const apiClient = new PromptApiClient();
  const params = new URLSearchParams({
    prompt_type: 'music',
    source: 'json',
    instrumental: isInstrumental.toString(),
  });

  if (genre) {
    params.append('categories', genre);
  }

  const response = await apiClient.get(`/api/ai/prompts/random?${params.toString()}`) as {
    status: string;
    message: string;
    data: {
      prompt: string | {
        prompt: string;
        category: string;
        source: string;
      };
      type: string;
      source: string;
      categories: string[];
      instrumental: boolean;
      video_type: string | null;
    };
    timestamp: string;
  };

  const promptData = response.data?.prompt;
  
  if (!promptData) {
    throw new Error('No prompt data in response');
  }
  
  if (typeof promptData === 'string') {
    return promptData;
  }
  
  if (typeof promptData === 'object' && 'prompt' in promptData) {
    return String(promptData.prompt);
  }
  
  throw new Error('Invalid prompt data structure');
}

export function OverlayGateway({ context }: { context: WorkflowContext }) {
  const [current, setCurrent] = useState<OverlayRequest | null>(null);
  // Unique message ID generator with counter to prevent duplicates
  const messageIdCounterRef = useRef(0);
  const generateUniqueMessageId = (prefix: string = 'message') => {
    messageIdCounterRef.current += 1;
    return `${prefix}-${Date.now()}-${messageIdCounterRef.current}-${Math.random().toString(36).substring(2, 9)}`;
  };

  useEffect(() => {
    const subId = brickEventEmitter.on('overlay:open', (payload: OverlayRequest) => {
      if (current) {
        brickEventEmitter.rejectOverlay(current.requestId, new Error('Overlay superseded'));
      }
      setCurrent(payload);
    });

    return () => {
      brickEventEmitter.offById(subId);
    };
  }, [current]);

  const close = useCallback(() => setCurrent(null), []);

  if (!current) return null;

  const { requestId, componentId, props } = current;

  const resolve = async (result: { value?: string; label?: string } | string) => {
    const normalized = typeof result === 'string' ? { value: result, label: String(result) } : result;
    
    if (normalized?.label) {
      context.setMessages(prev => ([
        ...prev,
        { id: generateUniqueMessageId('user'), role: 'user', content: normalized.label!, timestamp: new Date() }
      ]));
    }
    
    brickEventEmitter.resolveOverlay(requestId, normalized);
    close();
  };

  const resolveWithPromptGeneration = async (
    result: { value?: string; label?: string; isInstrumental?: boolean } | string,
    isInstrumental: boolean = false
  ) => {
    const normalized = typeof result === 'string' 
      ? { value: result, label: String(result), isInstrumental } 
      : { ...result, isInstrumental: result.isInstrumental ?? isInstrumental };
    
    if (normalized?.label) {
      context.setMessages(prev => ([
        ...prev,
        { id: generateUniqueMessageId('user'), role: 'user', content: normalized.label!, timestamp: new Date() }
      ]));
    }
    
    const genre = normalized.value === 'random_genre' ? undefined : normalized.value;
    
    const loadingMessageId = generateUniqueMessageId('prompt-loading');
    context.setMessages(prev => ([
      ...prev,
      {
        id: loadingMessageId,
        role: 'assistant',
        content: 'Generating music description...',
        timestamp: new Date()
      }
    ]));

    try {
      const prompt = await generateMusicPrompt(genre, normalized.isInstrumental || false);
      
      const promptMessageId = generateUniqueMessageId('assistant-prompt');
      const promptValue = prompt;
      
      context.setMessages(prev => prev.map(msg => 
        msg.id === loadingMessageId 
          ? {
              id: promptMessageId,
              role: 'assistant',
              content: promptValue,
              timestamp: new Date(),
              actionButtons: [
                {
                  label: 'Confirm',
                  variant: 'default',
                  onClick: () => {
                    const currentPrompt = context.messages.find(m => m.id === promptMessageId)?.content || promptValue;
                    
                    context.setMessages(prev => prev.map(m => 
                      m.id === promptMessageId 
                        ? { ...m, actionButtons: undefined }
                        : m
                    ));
                    
                    context.setMessages(prev => ([
                      ...prev,
                      {
                        id: generateUniqueMessageId('user-confirm'),
                        role: 'user',
                        content: 'Generate my music with this prompt',
                        timestamp: new Date()
                      }
                    ]));
                    
                    brickEventEmitter.resolveOverlay(requestId, { 
                      value: currentPrompt, 
                      label: currentPrompt, 
                      validated: true,
                      prompt: currentPrompt 
                    });
                    
                    close();
                  }
                },
                {
                  label: 'Edit',
                  variant: 'outline',
                  onClick: () => {}
                }
              ]
            }
          : msg
      ));
    } catch (error) {
      console.error('Failed to generate prompt:', error);
      context.setMessages(prev => prev.map(msg => 
        msg.id === loadingMessageId
          ? {
              id: msg.id,
              role: 'assistant',
              content: 'Failed to generate music description. Please try again.',
              timestamp: msg.timestamp
            }
          : msg
      ));
      context.toast({
        title: 'Generation Failed',
        description: 'Failed to generate music description. Please try again.',
        variant: 'destructive'
      });
      brickEventEmitter.rejectOverlay(requestId, error instanceof Error ? error : new Error('Prompt generation failed'));
      close();
    }
  };

  const reject = (err?: any) => {
    brickEventEmitter.rejectOverlay(requestId, err || new Error('Overlay cancelled'));
    close();
  };

  switch (componentId) {
    case 'GenreSelector': {
      const { isInstrumental = false } = props || {};
      return (
        <GenreSelector
          isOpen={true}
          onClose={() => reject()}
          isInstrumental={isInstrumental}
          onInstrumentalChange={() => {}}
          onSelectGenre={(genre: string, instrumental: boolean) => 
            resolveWithPromptGeneration({ value: genre, label: genre, isInstrumental: instrumental }, instrumental)
          }
          onGenerateRandom={(instrumental: boolean) => 
            resolveWithPromptGeneration({ value: 'random_genre', label: 'Random Genre', isInstrumental: instrumental }, instrumental)
          }
        />
      );
    }
    case 'VideoStylesSelector': {
      const selectedStyles: string[] = props?.selectedStyles || [];
      return (
        <VideoStylesSelector
          selectedStyles={selectedStyles}
          isOpen={true}
          onClose={() => reject()}
          onStylesChange={(styles) => {
            const names = Array.isArray(styles) ? styles.join(', ') : String(styles || '');
            resolve({ value: styles?.[0], label: names ? `Selected: ${names}` : '' });
          }}
        />
      );
    }
    case 'SelectionModal': {
      const options: SelectionOption[] = props?.options || [];
      const selectedValue: string = props?.selectedValue || '';
      return (
        <SelectionModal
          isOpen={true}
          onClose={() => reject()}
          title={props?.title || 'Select'}
          description={props?.description || ''}
          options={options}
          selectedValue={selectedValue}
          onSelect={(value, label) => resolve({ value, label: label || value })}
          gridCols={props?.gridCols}
          maxWidth={props?.maxWidth}
          cardDesign={props?.cardDesign}
        />
      );
    }
    default:
      // Unknown overlay: just close
      reject(new Error(`Unknown overlay component: ${componentId}`));
      return null;
  }
}


