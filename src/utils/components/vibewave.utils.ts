import { Scene, SettingsData } from '../../types/components/vibewave.types';

export const convertToCredits = (dollars: number, creditsRate: number): number => {
  const credits = dollars * creditsRate;
  return Math.ceil(credits / 5) * 5; // Round up to nearest 5
};

export const calculateLoopedBudget = async (
  totalDurationSeconds: number,
  trackCount: number,
  pricingService: any,
  reuseVideo: boolean = false,
  videoType: 'looped-static' | 'looped-animated' | 'recurring-scenes' = 'looped-static'
): Promise<number> => {
  const totalMinutes = totalDurationSeconds / 60;
  const units = reuseVideo ? 1 : trackCount;

  try {
    if (videoType === 'looped-static') {
      const price = await pricingService.calculateImagePrice(units, totalMinutes, 'clipizy-model');
      return price?.credits || 100;
    } else if (videoType === 'looped-animated') {
      const price = await pricingService.calculateLoopedAnimationPrice(units, totalMinutes, 'clipizy-model');
      return price?.credits || 100;
    } else if (videoType === 'recurring-scenes') {
      const price = await pricingService.calculateRecurringScenesPrice(units, totalMinutes, 'clipizy-model');
      return price?.credits || 100;
    }
  } catch (error) {
    console.error('Error calculating looped budget:', error);
  }

  return 100; // Fallback
};

export const calculateScenesBudget = async (
  totalDurationSeconds: number,
  trackDurations: number[],
  pricingService: any,
  reuseVideo: boolean = false
): Promise<number> => {
  const totalMinutes = totalDurationSeconds / 60;
  const longestTrackMinutes = Math.max(...trackDurations) / 60;
  const videoDuration = reuseVideo ? longestTrackMinutes : totalMinutes;

  try {
    const price = await pricingService.calculateVideoPrice(videoDuration, 'clipizy-model');
    return price?.credits || 100;
  } catch (error) {
    console.error('Error calculating scenes budget:', error);
    return 100;
  }
};

export const getScenesInfo = (
  totalDurationSeconds: number,
  trackDurations: number[],
  reuseVideo: boolean = false
) => {
  // Calculate total scenes across all videos: duration / 7.5 seconds per scene
  const totalScenes = Math.ceil(totalDurationSeconds / 7.5);

  // Number of videos (tracks)
  const numberOfVideos = trackDurations.length || 1;

  // When reusing video, create 1 video with all scenes
  // When not reusing, distribute scenes across multiple videos
  const scenesPerVideo = reuseVideo ? totalScenes : Math.ceil(totalScenes / numberOfVideos);
  const actualNumberOfVideos = reuseVideo ? 1 : numberOfVideos;

  return {
    scenesPerVideo,
    numberOfVideos: actualNumberOfVideos,
    totalScenes
  };
};

// fileToDataUri - use @/lib/utils instead
