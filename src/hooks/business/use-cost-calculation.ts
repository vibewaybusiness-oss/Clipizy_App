"use client";

import { useState, useEffect, useCallback } from "react";

interface UseCostCalculationProps {
  musicClipState: any;
  musicTracks: any;
  pricingService: any;
}

export function useCostCalculation({
  musicClipState,
  musicTracks,
  pricingService
}: UseCostCalculationProps) {
  const [currentGenerationCost, setCurrentGenerationCost] = useState(0);
  const [musicGenerationPrice, setMusicGenerationPrice] = useState(0);

  const calculateCurrentCost = useCallback(async () => {
    try {
      // Get settings from both state and form (form takes precedence for real-time updates)
      const stateSettings = musicClipState.state.settings;
      const formSettings = musicClipState.forms?.settingsForm?.getValues?.() || null;
      
      // Use form values if available, otherwise fall back to state settings
      const settings = {
        ...stateSettings,
        ...(formSettings || {}),
        // Ensure we have the latest budget from the form
        budget: (formSettings?.budget) || stateSettings?.budget || [100],
        user_price: (formSettings?.user_price) || stateSettings?.user_price || 100
      };
      
      console.log('=== COST CALCULATION DEBUG ===');
      console.log('State settings:', stateSettings);
      console.log('Form settings:', formSettings);
      console.log('Final settings:', settings);
      console.log('Tracks:', musicTracks?.tracks);
      console.log('Tracks length:', musicTracks?.tracks?.length);
      console.log('MusicClipState:', musicClipState);
      console.log('MusicTracks object:', musicTracks);
      
      if (!settings || !musicTracks?.tracks.length) {
        console.log('No settings or tracks available for cost calculation');
        console.log('Settings available:', !!settings);
        console.log('Tracks available:', !!musicTracks?.tracks);
        console.log('Tracks count:', musicTracks?.tracks?.length);
        console.log('Settings keys:', settings ? Object.keys(settings) : 'No settings');
        console.log('Tracks structure:', musicTracks ? Object.keys(musicTracks) : 'No musicTracks');
        setCurrentGenerationCost(0);
        return;
      }
      
      const trackDurations = musicTracks?.tracks.map((track: any) => track.duration);
      console.log('Calculating cost with:', {
        videoType: settings.videoType,
        trackCount: musicTracks?.tracks.length,
        trackDurations,
        reuse_content: settings.reuse_content, // CHANGED: was useSameVideoForAll
        formBudget: formSettings?.budget,
        formUserPrice: formSettings?.user_price
      });
      
      // If the form has a user_price (from BudgetSlider), use that directly
      if (formSettings?.user_price && formSettings.user_price > 0) {
        console.log('Using form user_price directly:', formSettings.user_price);
        setCurrentGenerationCost(formSettings.user_price);
        return;
      }
      
      // Call pricing service directly - no fallback logic (same as BudgetSlider)
      const cost = await pricingService.calculateBudget({
        videoType: settings.videoType || 'scenes',
        trackCount: musicTracks?.tracks.length,
        trackDurations,
        reuse_content: settings.reuse_content || false // CHANGED: was useSameVideoForAll
      });
      
      console.log('=== PRICING SERVICE RESPONSE ===');
      console.log('Full cost response:', cost);
      console.log('Cost price object:', cost?.price);
      console.log('Cost credits:', cost?.price?.credits);
      
      if (cost && cost.price && typeof cost.price.credits === 'number') {
        console.log('Setting current generation cost to:', cost.price.credits);
        setCurrentGenerationCost(cost.price.credits);
      } else {
        console.warn('Invalid cost response structure, using fallback');
        setCurrentGenerationCost(100); // Fallback cost
      }
    } catch (error) {
      console.warn('Cost calculation failed, using fallback pricing:', error);
      
      // Try to calculate a basic fallback cost based on available data
      try {
        const stateSettings = musicClipState.state.settings;
        const formSettings = musicClipState.forms?.settingsForm?.getValues?.() || null;
        const settings = {
          ...stateSettings,
          ...(formSettings || {})
        };
        
        const trackCount = musicTracks?.tracks.length || 1;
        const trackDurations = musicTracks?.tracks.map((track: any) => track.duration) || [180]; // Default 3 minutes
        const totalDuration = trackDurations.reduce((sum: number, duration: number) => sum + duration, 0);
        const videoType = settings?.videoType || 'scenes';
        
        // Basic fallback calculation
        let fallbackCost = 100;
        if (videoType === 'scenes') {
          fallbackCost = Math.max(100, Math.ceil(totalDuration / 30) * 10 * trackCount);
        } else {
          fallbackCost = Math.max(100, Math.ceil(totalDuration / 60) * 15 * trackCount);
        }
        
        console.log('Using fallback cost calculation:', {
          videoType,
          trackCount,
          totalDuration,
          fallbackCost
        });
        
        setCurrentGenerationCost(fallbackCost);
      } catch (fallbackError) {
        console.error('Fallback cost calculation also failed:', fallbackError);
        setCurrentGenerationCost(100); // Final fallback
      }
    }
  }, [musicClipState.state.settings, musicClipState.forms.settingsForm, musicTracks?.tracks, pricingService]);

  useEffect(() => {
    calculateCurrentCost();
  }, [calculateCurrentCost]);

  // Also trigger cost calculation when form values change
  useEffect(() => {
    const subscription = musicClipState.forms.settingsForm.watch((value) => {
      console.log('Settings form values changed, recalculating cost:', value);
      calculateCurrentCost();
    });
    return () => subscription.unsubscribe();
  }, [calculateCurrentCost]);

  useEffect(() => {
    const calculatePrice = () => {
      if (musicClipState.state.musicTracksToGenerate > 0) {
        // Set fixed price of 10 credits per music generation
        const price = musicClipState.state.musicTracksToGenerate * 10;
        setMusicGenerationPrice(price);
      }
    };
    calculatePrice();
  }, [musicClipState.state.musicTracksToGenerate]);

  return {
    currentGenerationCost,
    musicGenerationPrice
  };
}
