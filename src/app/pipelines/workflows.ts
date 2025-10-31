export interface ProjectSettings {
  videoType: string;
  videoStyle: string;
  animationStyle: string;
  videoFormat: string;
  animationHasAudio: boolean;
  audioVisualizerType: string;
  audioVisualizerEnabled: boolean;
  audioVisualizerPositionV: string;
  audioVisualizerPositionH: string;
  audioVisualizerSize: string;
  audioVisualizerMirroring: string;
  createIndividualVideos: boolean;
  createCompilation: boolean;
  reuse_content: boolean;
  reference_images: any[];
  tracks: string[];
  audioTransition: string;
  videoTransition: string;
  budget: number;
  user_price: number;
  currentStep: string;
  maxReachedStep: string;
  autoValidation: boolean;
  prompt_user_input: string;
}
