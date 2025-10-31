// VIDEO DOMAIN TYPES
export interface VideoSettings {
  type: 'static' | 'animated_loop' | 'scenes';
  style: string;
  animationStyle: string;
  budget: number[];
  user_price?: number;
}

export interface VideoGenerationRequest {
  projectId: string;
  trackId: string;
  settings: VideoSettings;
  description: string;
  style?: string;
  mood?: string;
}

export interface VideoGenerationResponse {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  video_url?: string;
  thumbnail_url?: string;
  created_at: string;
  updated_at: string;
}

export interface VideoPreview {
  id: string;
  url: string;
  thumbnail: string;
  duration: number;
  size: number;
  format: string;
}
