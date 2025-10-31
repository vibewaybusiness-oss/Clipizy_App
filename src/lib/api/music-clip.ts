import { BaseApiClient } from './base';
import { API_BASE_URL, API_PATHS } from './config';

export interface MusicClipProject {
  id: string;
  name: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  settings?: any;
  tracks?: any[];
}

export interface CreateMusicClipProjectRequest {
  name?: string;
  description?: string;
  settings?: any;
}

export interface UpdateMusicClipProjectRequest {
  name?: string;
  description?: string;
  settings?: any;
}

class MusicClipAPI extends BaseApiClient {
  constructor() {
    super(API_BASE_URL);
  }

  async getProjects(): Promise<MusicClipProject[]> {
    const response = await this.get<{ projects: MusicClipProject[] }>(API_PATHS.MUSIC_CLIP.PROJECTS);
    return response.projects || [];
  }

  async getAllProjects(): Promise<{
    projects: Array<{
      id: string;
      name: string;
      description?: string;
      status: string;
      created_at: string;
      tracks?: Array<{
        id: string;
        name: string;
        duration: number;
        created_at: string;
      }>;
    }>;
  }> {
    return this.get(API_PATHS.MUSIC_CLIP.PROJECTS);
  }

  async createProject(dataOrName?: CreateMusicClipProjectRequest | string, description?: string): Promise<MusicClipProject | { id: string; name: string; description?: string; status: string; created_at: string }> {
    if (typeof dataOrName === 'string') {
      return this.post(API_PATHS.MUSIC_CLIP.PROJECTS, { name: dataOrName, description });
    } else if (dataOrName && typeof dataOrName === 'object') {
      return this.post<MusicClipProject>(API_PATHS.MUSIC_CLIP.PROJECTS, dataOrName);
    } else {
      return this.post(API_PATHS.MUSIC_CLIP.PROJECTS, {});
    }
  }

  async getProject(projectId: string): Promise<MusicClipProject> {
    return this.get<MusicClipProject>(API_PATHS.MUSIC_CLIP.PROJECT(projectId));
  }

  async updateProject(projectId: string, data: UpdateMusicClipProjectRequest): Promise<MusicClipProject> {
    return this.put<MusicClipProject>(API_PATHS.MUSIC_CLIP.PROJECT(projectId), data);
  }

  async deleteProject(projectId: string): Promise<void> {
    return this.delete<void>(API_PATHS.MUSIC_CLIP.PROJECT(projectId));
  }

  async resetProjects(): Promise<void> {
    return this.delete<void>(API_PATHS.MUSIC_CLIP.PROJECTS);
  }

  async getProjectScript(projectId: string): Promise<any> {
    try {
      return await this.get<any>(API_PATHS.MUSIC_CLIP.SCRIPT(projectId));
    } catch (error) {
      // Handle network errors gracefully - don't throw the error
      console.warn('Failed to get project script due to network error:', error);
      // Return empty script to prevent the error from propagating
      return { steps: { music: { settings: {} } } };
    }
  }

  async updateProjectSettings(projectId: string, settings: any): Promise<any> {
    try {
      // Check if user is authenticated before making API call
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      if (!token) {
        console.log('User not authenticated, returning mock response for project settings update');
        return { success: false, error: 'Authentication required' };
      }

      const requestBody = { projectId, ...settings };
      console.log('Updating project settings:', { projectId, settings, requestBody });
      const result = await this.post<any>(`/api/v1/projects/${projectId}/settings`, requestBody);
      console.log('Project settings update result:', result);
      return result;
    } catch (error) {
      // Handle network errors gracefully - don't throw the error
      console.warn('Failed to update project settings due to network error:', error);
      console.warn('Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
        projectId,
        settings
      });
      // Return a mock response to prevent the error from propagating
      return { success: false, error: 'Network error' };
    }
  }

  async getProjectTracks(projectId: string): Promise<any[]> {
    try {
      const response = await this.get<{ tracks: any[] }>(API_PATHS.MUSIC_CLIP.TRACKS(projectId));
      return response.tracks || [];
    } catch (error) {
      // Handle network errors gracefully - don't throw the error
      console.warn('Failed to get project tracks due to network error:', error);
      // Return empty tracks array to prevent the error from propagating
      return [];
    }
  }

  async uploadTrack(projectId: string, file: File, additionalData?: Record<string, any>): Promise<any> {
    const data = { projectId, ...additionalData };
    return this.uploadFile<any>(API_PATHS.MUSIC_CLIP.UPLOAD_TRACK(projectId), file, data);
  }


  async updateProjectScript(projectId: string, script: any): Promise<any> {
    return this.post<any>(`/api/v1/projects/${projectId}/settings`, { script });
  }

  async autoSave(projectId: string, data: any): Promise<void> {
    return this.post<void>(`/api/storage/projects/${projectId}/auto-save`, data);
  }

  async loadState(projectId: string): Promise<any> {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const response = await fetch(`/api/storage/projects/${projectId}/settings`, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
      });
      
      if (!response.ok) {
        return null;
      }
      
      const result = await response.json();
      const settingsData = result.data || result;
      return settingsData;
    } catch (error) {
      console.warn('Failed to load project state:', error);
      return null;
    }
  }

  async getProjectAnalysis(projectId: string): Promise<any> {
    return this.get<any>(`${API_PATHS.MUSIC_CLIP.PROJECT(projectId)}/analysis`);
  }

  async updateProjectAnalysis(projectId: string, analysisData: any): Promise<void> {
    return this.put<void>(`${API_PATHS.MUSIC_CLIP.PROJECT(projectId)}/analysis`, analysisData);
  }
}

export const projectsAPI = new MusicClipAPI();
export const musicClipAPI = new MusicClipAPI();
