import { useState, useCallback } from 'react';
import { useToast } from '../ui/use-toast';
import { BaseApiClient } from '@/lib/api/base';
import { getBackendUrl } from '@/lib/config';

interface PromptGenerationOptions {
  promptType: 'music' | 'image_prompts' | 'video_prompts' | 'random_image' | 'random_video';
  categories?: string[];
  instrumental?: boolean;
  source?: 'json';
  videoType?: string;
}

class PromptApiClient extends BaseApiClient {
  constructor() {
    super(getBackendUrl());
  }
}

export function usePromptGeneration() {
  const [isGenerating, setIsGenerating] = useState(false);
  const { toast } = useToast();
  const apiClient = new PromptApiClient();

  const generatePrompt = useCallback(async (options: PromptGenerationOptions) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('generatePrompt called, setting isGenerating to true');
    }
    setIsGenerating(true);

    try {
      const params = new URLSearchParams({
        prompt_type: options.promptType,
        source: options.source || 'json',
      });

      if (options.instrumental !== undefined) {
        params.append('instrumental', options.instrumental.toString());
      }

      if (options.categories && options.categories.length > 0) {
        params.append('categories', options.categories.join(','));
      }

      if (options.videoType) {
        params.append('video_type', options.videoType);
      }

      if (process.env.NODE_ENV === 'development') {
        console.log('Making API call to:', `/api/ai/prompts/random?${params.toString()}`);
      }
      const response = await apiClient.get(`/api/ai/prompts/random?${params.toString()}`) as { 
        status: string;
        message: string;
        data: { 
          prompt: string;
          type: string;
          source: string;
          categories: string[];
          instrumental: boolean;
          video_type: string | null;
        };
        timestamp: string;
      };
      
      if (process.env.NODE_ENV === 'development') {
        console.log('API response received:', JSON.stringify(response, null, 2));
      }

      if (!response.data?.prompt) {
        throw new Error('No prompt received from server');
      }

      return {
        prompt: response.data.prompt,
        type: response.data.type,
        source: response.data.source,
        categories: response.data.categories,
        instrumental: response.data.instrumental,
        video_type: response.data.video_type
      };

    } catch (error) {
      console.error('Error generating prompt:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      toast({
        variant: "destructive",
        title: "Generation Failed",
        description: `Failed to generate prompt: ${errorMessage}`,
      });
      throw error;
    } finally {
      if (process.env.NODE_ENV === 'development') {
        console.log('generatePrompt completed, setting isGenerating to false');
      }
      setIsGenerating(false);
    }
  }, [toast]);

  const generateMusicDescription = useCallback(async (genre?: string, isInstrumental?: boolean) => {
    return generatePrompt({
      promptType: 'music',
      categories: genre ? [genre] : undefined,
      instrumental: isInstrumental || false,
    });
  }, [generatePrompt]);

  const generateVideoPrompt = useCallback(async (videoType: string, genre?: string, useRandom: boolean = false) => {
    let promptType: 'image_prompts' | 'video_prompts' | 'random_image' | 'random_video' = 'image_prompts';

    if (useRandom) {
      // Use random prompt types based on video type
      if (videoType === 'scenes') {
        promptType = 'random_video';
      } else {
        promptType = 'random_image';
      }
    } else {
      // Use standard prompt types
      if (videoType === 'scenes') {
        promptType = 'video_prompts';
      } else {
        promptType = 'image_prompts';
      }
    }

    return generatePrompt({
      promptType,
      categories: genre ? [genre] : undefined,
      videoType: videoType,
    });
  }, [generatePrompt]);

  return {
    isGenerating,
    generatePrompt,
    generateMusicDescription,
    generateVideoPrompt,
  };
}
