import { BaseApiClient } from './base';
import { API_BASE_URL, API_PATHS } from './config';

export interface VideoGenerationRequest {
  project_id: string;
  video_type: string;
  video_style?: string;
  audio_visualizer?: Record<string, any>;
  transitions?: Record<string, any>;
  budget?: number;
  track_ids?: string[];
  settings?: Record<string, any>;
  estimated_credits?: number;
  estimated_completion_time?: string;
  priority?: number;
  auto?: boolean;
}

export interface VideoGenerationResponse {
  job_id: string;
  project_id: string;
  status: string;
  estimated_completion_time?: string;
  message: string;
  credits_info?: {
    cost: number;
    transaction_id: string;
    message: string;
  };
}

export interface GenerationStatusResponse {
  job_id: string;
  status: string;
  progress_percentage?: number;
  current_step?: string;
  estimated_completion?: string;
  error_message?: string;
  output_paths?: string[];
  job_metadata?: any;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface ManualImageGenerationPayload {
  prompt: string;
  scene_index: number;
  video_type: string;
  video_style?: string;
  regenerate?: boolean;
}

export interface ManualPromptUpdatePayload {
  prompt: string;
  approve: boolean;
  scene_prompts?: string[];
}

export interface ManualSceneGenerationPayload {
  scene_index: number;
  prompt: string;
  video_style?: string;
}

export interface ManualVideoGenerationPayload {
  scene_index: number;
  prompt: string;
  video_style?: string;
}

export interface ManualGenerationResponse {
  success: boolean;
  asset_path?: string;
  credits_spent?: number;
  message?: string;
  error?: string;
}

class VideoGenerationAPI extends BaseApiClient {
  constructor() {
    super(API_BASE_URL);
  }

  async generateVideo(request: VideoGenerationRequest): Promise<VideoGenerationResponse> {
    return this.post<VideoGenerationResponse>(API_PATHS.MUSIC_CLIP.GENERATE, request);
  }

  async checkCredits(request: VideoGenerationRequest): Promise<{
    project_id: string;
    required_credits: number;
    track_count: number;
    video_type: string;
    message: string;
  }> {
    return this.post<{
      project_id: string;
      required_credits: number;
      track_count: number;
      video_type: string;
      message: string;
    }>('/api/music-clip/check-credits', request);
  }

  async getGenerationStatus(jobId: string): Promise<GenerationStatusResponse> {
    return this.get<GenerationStatusResponse>(API_PATHS.MUSIC_CLIP.STATUS(jobId));
  }

  async getJobStatus(projectId: string): Promise<GenerationStatusResponse | null> {
    try {
      return await this.get<GenerationStatusResponse>(API_PATHS.MUSIC_CLIP.PROJECT_STATUS(projectId));
    } catch (error) {
      console.error('Error fetching job status:', error);
      return null;
    }
  }

  async cancelGeneration(jobId: string): Promise<{ job_id: string; status: string; message: string }> {
    return this.post<{ job_id: string; status: string; message: string }>(`/api/music-clip/cancel/${jobId}`);
  }

  async approvePrompt(payload: ManualPromptUpdatePayload): Promise<{ success: boolean; message: string; next_step: string }> {
    return this.post<{ success: boolean; message: string; next_step: string }>('/api/music-clip/manual/prompt-approval', payload);
  }

  async regenerateImage(payload: ManualSceneGenerationPayload): Promise<{ success: boolean; image_path: string; scene_index: number; credits_deducted: number; remaining_credits: number }> {
    return this.post<{ success: boolean; image_path: string; scene_index: number; credits_deducted: number; remaining_credits: number }>('/api/music-clip/manual/regenerate-image', payload);
  }

  async regenerateVideo(payload: ManualVideoGenerationPayload): Promise<{ success: boolean; video_path: string; scene_index: number; credits_deducted: number; remaining_credits: number }> {
    return this.post<{ success: boolean; video_path: string; scene_index: number; credits_deducted: number; remaining_credits: number }>('/api/music-clip/manual/regenerate-video', payload);
  }
}

export const videoGenerationAPI = new VideoGenerationAPI();
