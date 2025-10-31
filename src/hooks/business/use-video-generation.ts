"use client";

import { useCallback } from "react";
import { useToast } from "@/hooks/ui/use-toast";
import { useCredits } from "./use-credits";
import { videoGenerationAPI, type VideoGenerationRequest } from "@/lib/api/video-generation";

interface UseVideoGenerationProps {
  projectManagement: any;
  // dataPersistence removed - handled by backend storage
  pricingService: any;
  setGeneratingVideo: (generating: boolean) => void;
  markAsSaved: () => void;
}

export function useVideoGeneration({
  projectManagement,
  // dataPersistence removed
  pricingService,
  setGeneratingVideo,
  markAsSaved
}: UseVideoGenerationProps) {
  const { toast } = useToast();
  const { fetchBalance } = useCredits();

  const startVideoGeneration = useCallback(async (
    values: any,
    generationConfig: {
      videoType: string;
      trackCount?: number;
      trackDurations?: number[];
      totalDuration?: number;
      reuse_content?: boolean; // CHANGED: was useSameVideoForAll
      model?: string;
    }
  ): Promise<{ success: boolean; response?: any; error?: string } | undefined> => {
    console.log('=== startVideoGeneration CALLED ===');
    console.log('Values:', values);
    console.log('Project ID:', projectManagement.state.currentProjectId);
    console.log('Generation config:', generationConfig);
    
    if (!projectManagement.state.currentProjectId) {
      toast({
        variant: "destructive",
        title: "No Project",
        description: "No project found. Please create a project first.",
      });
      return { success: false, error: "No project found" };
    }

    try {
      setGeneratingVideo(true);
      
      console.log('Saving all data to backend before generation...');
      // Data persistence handled by backend storage
      markAsSaved();
      console.log('All data saved to backend successfully');
      
      console.log('Calculating cost with settings:', generationConfig);
      
      // Get cost from business API
      const calculatedCost = await pricingService.calculateBudget({
        videoType: generationConfig.videoType || 'scenes',
        trackCount: generationConfig.trackCount || 1,
        trackDurations: generationConfig.trackDurations || [],
        reuse_content: generationConfig.reuse_content || false, // CHANGED: was useSameVideoForAll
        model: generationConfig.model || 'clipizy-model'
      });

      // Credit validation now handled by backend only
      console.log('=== SKIPPING FRONTEND CREDIT VALIDATION ===');
      console.log('Credit validation will be handled by backend API');
      console.log('Calculated cost:', calculatedCost.price.credits);

      // Build generation request
      const generationRequest: VideoGenerationRequest = {
        project_id: projectManagement.state.currentProjectId,
        video_type: generationConfig.videoType || 'scenes',
        video_style: values.videoStyle,
        audio_visualizer: {
          enabled: values.audioVisualizerEnabled || false,
          type: values.audioVisualizerType || 'waveform',
          size: values.audioVisualizerSize || 'medium',
          position_v: values.audioVisualizerPositionV || 'bottom',
          position_h: values.audioVisualizerPositionH || 'center',
          mirroring: values.audioVisualizerMirroring || false
        },
        transitions: {
          audio: values.audioTransition || 'fade',
          video: values.videoTransition || 'crossfade'
        },
        budget: calculatedCost.price.credits,
        track_ids: values.trackIds || [],
        settings: {
          ...values,
          videoDescription: values.videoDescription,
          createIndividualVideos: values.createIndividualVideos,
          createCompilation: values.createCompilation,
          reuse_content: values.reuse_content // CHANGED: was useSameVideoForAll
        },
        estimated_credits: calculatedCost.price.credits,
        priority: 0,
        auto: values.auto !== false // Default to auto unless explicitly disabled
      };

      console.log('Starting video generation with request:', generationRequest);
      console.log('Request details:', {
        project_id: generationRequest.project_id,
        video_type: generationRequest.video_type,
        budget: generationRequest.budget,
        track_ids: generationRequest.track_ids,
        estimated_credits: generationRequest.estimated_credits,
        auto: generationRequest.auto
      });
      
      const response = await videoGenerationAPI.generateVideo(generationRequest);
      
      console.log('Video generation started:', response);
      console.log('Response credits_info:', response?.credits_info);
      
      const creditsInfo = response?.credits_info;
      if (creditsInfo) {
        toast({
          title: "Video Generation Started",
          description: `Your video is being generated for ${creditsInfo.cost} credits. Transaction ID: ${creditsInfo.transaction_id}`,
        });
      } else {
        console.warn('Video generation response missing credits_info:', response);
        toast({
          title: "Video Generation Started",
          description: `Your video is being generated for ${calculatedCost} credits. You'll receive a notification when it's ready.`,
        });
      }
      
      // Return success result
      return { success: true, response };
      
    } catch (error: any) {
      console.warn('Video generation failed:', error);
      
      if (error.status === 402) {
        // Handle 402 Payment Required error - refresh credits first
        console.log('402 error data:', error.errorData);
        
        try {
          console.log('Backend insufficient credits detected, refreshing balance from backend...');
          await fetchBalance();
        } catch (refreshError) {
          console.error('Failed to refresh credits after 402 error:', refreshError);
        }
        
        if (error.errorData && typeof error.errorData === 'object' && error.errorData.detail && error.errorData.detail.error === 'Insufficient credits') {
          // Show detailed insufficient credits information
          const creditDetails = error.errorData.detail;
          console.log('Insufficient credits details:', {
            required: creditDetails.required_credits,
            current: creditDetails.current_balance,
            shortfall: creditDetails.shortfall
          });
          
          toast({
            variant: "destructive",
            title: "Insufficient Credits",
            description: `You need ${creditDetails.required_credits} credits to generate this video, but you only have ${creditDetails.current_balance} credits. Shortfall: ${creditDetails.shortfall} credits.`,
          });
        } else {
          toast({
            variant: "destructive",
            title: "Insufficient Credits",
            description: "You don't have enough credits for this generation.",
          });
        }
      } else {
        let errorMessage = "Failed to start video generation. Please try again.";
        let errorDescription = error?.message || "An unexpected error occurred.";
        
        // Handle specific error cases
        if (error?.status === 400) {
          if (error?.message?.includes('Project must be in completed or draft state')) {
            errorMessage = "Project Status Error";
            errorDescription = "The project is in an invalid state. Please try again.";
          } else if (error?.message?.includes('Insufficient credits')) {
            errorMessage = "Insufficient Credits";
            errorDescription = error.message;
          }
        } else if (error?.status === 404) {
          errorMessage = "Project Not Found";
          errorDescription = "The project could not be found. Please refresh and try again.";
        } else if (error?.status === 500) {
          errorMessage = "Server Error";
          errorDescription = "A server error occurred. Please try again later.";
        }
        
        toast({
          variant: "destructive",
          title: errorMessage,
          description: errorDescription,
        });
      }
      
      // Return failure result
      return { success: false, error: error.message || 'Unknown error' };
    } finally {
      setGeneratingVideo(false);
    }
  }, [projectManagement, pricingService, setGeneratingVideo, markAsSaved, toast, fetchBalance]);

  return {
    startVideoGeneration
  };
}
