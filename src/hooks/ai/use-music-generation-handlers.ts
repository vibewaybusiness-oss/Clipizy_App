"use client";

import { useCallback } from "react";
import { useToast } from "../ui/use-toast";
import { useUserOnboarding } from "../users/use-user-onboarding";
import { projectsAPI } from "@/lib/api/projects";
import { useProducerMusicGeneration } from "./use-producer-music-generation";
import type { MusicTrack } from "@/types/domains/music";

interface UseMusicGenerationHandlersProps {
  musicClipState: any;
  musicTracks: any;
  projectManagement: any;
  promptGeneration: any;
  setShowOnboardingLoading: (loading: boolean) => void;
}

export function useMusicGenerationHandlers({
  musicClipState,
  musicTracks,
  projectManagement,
  promptGeneration,
  setShowOnboardingLoading
}: UseMusicGenerationHandlersProps) {
  const { toast } = useToast();
  const userOnboarding = useUserOnboarding();
  
  // Use ProducerAI for music generation
  const { handleGenerateMusicWithProducerAI } = useProducerMusicGeneration({
    musicClipState,
    musicTracks,
    projectManagement,
    setShowOnboardingLoading
  });

  const handleGenerateMusic = useCallback(async (options?: { duration: number; model: string }, isInstrumental?: boolean) => {
    console.log('handleGenerateMusic called with:', { options, isInstrumental, musicPrompt: musicClipState.state.musicPrompt });
    
    if (!musicClipState.state.musicPrompt.trim()) {
      toast({
        variant: "destructive",
        title: "Missing Description",
        description: "Please describe the music you want to generate.",
      });
      return;
    }
    
    await handleGenerateMusicPrompt(undefined, isInstrumental);
  }, [musicClipState.state.musicPrompt, toast]);
  
  const handleGenerateMusicPrompt = useCallback(async (selectedGenre?: string, isInstrumental?: boolean) => {
    // Use ProducerAI for music generation instead of Suno
    await handleGenerateMusicWithProducerAI(selectedGenre, isInstrumental);
  }, [handleGenerateMusicWithProducerAI]);
  
  const handleGenerateMusicDescription = useCallback(async (selectedGenre?: string, isInstrumental?: boolean) => {
    console.log('🎵 Generating music description:', { selectedGenre, isInstrumental });
    
    if (isInstrumental !== undefined) {
      musicClipState.actions.setIsInstrumental(isInstrumental);
    }

    try {
      console.log('🎵 Calling promptGeneration.generateMusicDescription...');
      const data = await promptGeneration.generateMusicDescription(selectedGenre, isInstrumental);
      console.log('🎵 Received data:', data);

      musicClipState.actions.setMusicPrompt(data.prompt.prompt);

      toast({
        title: "Music Description Generated",
        description: `Generated ${data.prompt.category} style description for your music.`,
      });

    } catch (error) {
      console.error('❌ Error generating music description:', error);
      toast({
        variant: "destructive",
        title: "Generation Failed",
        description: "Failed to generate music description. Please try again.",
      });
    }
  }, [musicClipState, promptGeneration, toast]);
  
  const handleGenreSelect = useCallback(async (genre: string, isInstrumental: boolean) => {
    await handleGenerateMusicDescription(genre, isInstrumental);
  }, [handleGenerateMusicDescription]);
  
  const handleRandomGenerate = useCallback(async (isInstrumental: boolean) => {
    await handleGenerateMusicDescription(undefined, isInstrumental);
  }, [handleGenerateMusicDescription]);

  return {
    handleGenerateMusic,
    handleGenerateMusicPrompt,
    handleGenerateMusicDescription,
    handleGenreSelect,
    handleRandomGenerate
  };
}
