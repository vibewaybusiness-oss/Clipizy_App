import { BaseApiClient } from './base';
import { API_BASE_URL } from './config';

export interface StepValidationRequest {
  job_id: string;
  step: 'prompts' | 'images' | 'videos';
  item_id?: string;
  validate_all: boolean;
}

export interface StepValidationResponse {
  success: boolean;
  message: string;
  next_step?: string;
  items_validated: number;
}

export interface RegenerateRequest {
  job_id: string;
  step: 'images' | 'videos';
  item_id: string;
  prompt?: string;
}

export interface RegenerateResponse {
  success: boolean;
  message: string;
  new_item_id: string;
}

export interface GenerationProgressResponse {
  job_id: string;
  current_step: 'prompts' | 'images' | 'videos' | 'completed';
  status: string;
  progress: {
    prompts: {
      status: 'pending' | 'completed';
      items: any[];
    };
    images: {
      status: 'pending' | 'completed';
      items: any[];
    };
    videos: {
      status: 'pending' | 'completed';
      items: any[];
    };
  };
  items: any[];
  can_proceed: boolean;
}

class StepByStepGenerationAPI extends BaseApiClient {
  constructor() {
    super(API_BASE_URL);
  }

  async getGenerationProgress(jobId: string): Promise<GenerationProgressResponse> {
    return this.get(`/api/video-generation/progress/${jobId}`);
  }

  async validateStep(request: StepValidationRequest): Promise<StepValidationResponse> {
    return this.post('/api/video-generation/validate-step', request);
  }

  async regenerateItem(request: RegenerateRequest): Promise<RegenerateResponse> {
    return this.post('/api/video-generation/regenerate', request);
  }
}

export const stepByStepGenerationAPI = new StepByStepGenerationAPI();
