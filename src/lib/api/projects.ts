"use client";

import { BaseApiClient } from './base';
import { getBackendUrl } from '@/lib/config';
import { 
  BaseProject, 
  ProjectType, 
  CreateProjectRequest, 
  UpdateProjectRequest, 
  ProjectData,
  PROJECT_CONFIGS 
} from '@/types/projects';

// Unified projects API - supports all project types

const API_BASE_URL = getBackendUrl();

export interface ProjectsAPI {
  // Project CRUD operations
  createProject: (data: CreateProjectRequest) => Promise<BaseProject>;
  getProject: (projectId: string) => Promise<BaseProject>;
  getProjects: (userId: string, type?: ProjectType) => Promise<BaseProject[]>;
  getAllProjects: () => Promise<{ projects: BaseProject[] }>;
  updateProject: (projectId: string, data: UpdateProjectRequest) => Promise<BaseProject>;
  deleteProject: (projectId: string) => Promise<void>;
  
  // Project data operations
  saveProjectData: (projectId: string, data: ProjectData) => Promise<void>;
  loadProjectData: (projectId: string) => Promise<any>;
  getProjectSettings: (projectId: string) => Promise<any>;
  
  // File operations
  uploadProjectFile: (projectId: string, file: File, metadata?: any) => Promise<string>;
  deleteFile: (projectId: string, fileId: string) => Promise<void>;
  getProjectFiles: (projectId: string) => Promise<any[]>;
  getTrackUrl: (projectId: string, trackId: string) => Promise<string>;
  
  // Auto-save operations
  autoSave: (projectId: string, data: any) => Promise<void>;
  pushDataOnRefresh: (projectId: string, data: any) => Promise<void>;
  
  // Legacy methods for backward compatibility
  updateProjectStatus: (projectId: string, status: string) => Promise<void>;
  createMusicClipProject: (name: string, description: string) => Promise<BaseProject>;
  uploadTrack: (projectId: string, file: File, metadata: any) => Promise<any>;
  getProjectScript: (projectId: string) => Promise<any>;
}

class ProjectsService extends BaseApiClient implements ProjectsAPI {
  private static instance: ProjectsService;
  private saveQueue: Map<string, any> = new Map();
  private saveTimeouts: Map<string, NodeJS.Timeout> = new Map();
  private isOnline: boolean = typeof window !== 'undefined' ? navigator.onLine : true;
  private retryAttempts: Map<string, number> = new Map();
  private notFoundProjects: Set<string> = new Set();
  private pendingSaves: Set<string> = new Set();
  private maxRetries = 3;
  private saveDelay = 3000;

  constructor() {
    super(API_BASE_URL);
    if (typeof window !== 'undefined') {
      this.setupEventListeners();
    }
  }

  public static getInstance(): ProjectsService {
    if (!ProjectsService.instance) {
      ProjectsService.instance = new ProjectsService();
    }
    return ProjectsService.instance;
  }

  private setupEventListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.processSaveQueue();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });

    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.flushAllSaves();
      }
    });

    window.addEventListener('beforeunload', () => {
      this.flushAllSaves();
    });

    setInterval(() => {
      this.flushAllSaves();
    }, 60000);
  }

  // Project CRUD operations
  async createProject(data: CreateProjectRequest): Promise<BaseProject> {
    const response = await this.post<any>('/api/storage/projects', data);
    // Handle wrapped response format from backend
    if (response.data) {
      return response.data;
    } else {
      return response;
    }
  }

  async getProject(projectId: string): Promise<BaseProject> {
    const response = await this.get<any>(`/api/storage/projects/${projectId}`);
    // Handle wrapped response format from backend
    if (response.data) {
      return response.data;
    } else {
      return response;
    }
  }

  async getProjects(userId: string, type?: ProjectType): Promise<BaseProject[]> {
    try {
      const params = new URLSearchParams();
      if (type) {
        params.append('type', type);
      }
      const response = await this.get<any>(`/api/storage/projects?${params}`);
      // Handle wrapped response format from backend
      if (response.data && response.data.projects) {
        return response.data.projects;
      } else if (response.projects) {
        return response.projects;
      } else {
        return [];
      }
    } catch (error: any) {
      console.error('Error fetching projects:', error);
      // Return empty array on error
      return [];
    }
  }

  async getAllProjects(): Promise<{ projects: BaseProject[] }> {
    try {
      const response = await this.get<any>('/api/storage/projects');
      // Handle wrapped response format from backend
      if (response.data && response.data.projects) {
        return { projects: response.data.projects };
      } else if (response.projects) {
        return { projects: response.projects };
      } else {
        return { projects: [] };
      }
    } catch (error: any) {
      console.error('Error fetching projects:', error);
      // Return empty projects array on error
      return { projects: [] };
    }
  }

  async updateProject(projectId: string, data: UpdateProjectRequest): Promise<BaseProject> {
    return this.put<BaseProject>(`/api/storage/projects/${projectId}`, data);
  }

  async deleteProject(projectId: string): Promise<void> {
    await this.delete(`/api/storage/projects/${projectId}`);
  }

  // Project data operations
  async saveProjectData(projectId: string, data: ProjectData): Promise<void> {
    await this.post(`/api/storage/projects/${projectId}/data`, data);
  }

  async loadProjectData(projectId: string): Promise<any> {
    // Load only from backend - no localStorage fallback
    const response = await this.get<{ data: any }>(`/api/storage/projects/${projectId}/data`);
    return response.data;
  }

  async getProjectSettings(projectId: string): Promise<any> {
    // Fetch project settings from the v1 API endpoint
    const response = await this.get<any>(`/api/v1/projects/${projectId}/settings`);
    return response;
  }

  // File operations
  async uploadProjectFile(projectId: string, file: File, metadata?: any): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_type', 'music-clip');
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    try {
      console.log('📤 Uploading file:', {
        projectId,
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type,
        endpoint: `/api/storage/projects/${projectId}/files/upload`
      });

      const response = await this.post<{ 
        status?: string;
        data?: { 
          id?: string;
          filename?: string;
          [key: string]: any;
        };
        file_id?: string;
        id?: string;
      }>(`/api/storage/projects/${projectId}/files/upload`, formData);

      console.log('📥 Upload response:', response);

      // Backend returns data.id in the standard response format
      const fileId = response.data?.id || response.file_id || response.id || response.data?.file_id || '';
      
      if (!fileId) {
        console.error('❌ No file ID in response:', response);
        throw new Error(`Upload failed: No file ID returned. Response: ${JSON.stringify(response)}`);
      }

      console.log('✅ File uploaded successfully, fileId:', fileId);
      return fileId;
    } catch (error: any) {
      console.error('❌ Upload error:', error);
      throw error;
    }
  }


  async deleteFile(projectId: string, fileId: string): Promise<void> {
    await this.delete(`/api/storage/projects/${projectId}/files/${fileId}`);
  }

  async getProjectFiles(projectId: string): Promise<any[]> {
    const response = await this.get<{ files: any[] }>(`/api/storage/projects/${projectId}/files`);
    return response.files;
  }

  async getTrackUrl(projectId: string, trackId: string): Promise<string> {
    const response = await this.get<{ url: string }>(`/api/storage/projects/${projectId}/files/${trackId}/url`);
    return response.url;
  }

  // Auto-save operations
  async autoSave(projectId: string, data: any): Promise<void> {
    await this.scheduleSave(projectId, data);
  }

  public scheduleSave(projectId: string, data: any) {
    const hasDataToSave = data.projectData || data.data;
    
    if (!hasDataToSave) {
      return;
    }

    // Check if we're already saving this project to prevent concurrent saves
    if (this.saveTimeouts.has(projectId)) {
      console.log(`Save already scheduled for project ${projectId}, skipping duplicate`);
      return;
    }

    const currentData = this.saveQueue.get(projectId) || {
      projectId,
      projectType: data.projectType,
      data: null,
      timestamp: Date.now()
    };

    const updatedData = {
      ...currentData,
      ...data,
      timestamp: Date.now()
    };

    this.saveQueue.set(projectId, updatedData);

    const timeout = setTimeout(() => {
      this.saveToBackend(projectId, updatedData);
    }, this.saveDelay);

    this.saveTimeouts.set(projectId, timeout);
  }

  private async saveToBackend(projectId: string, data: any) {
    if (!this.isOnline) {
      console.log(`Offline - cannot save project ${projectId}, backend storage required`);
      return;
    }

    // Check if this project has been marked as not found (404)
    if (this.notFoundProjects.has(projectId)) {
      console.warn(`Project ${projectId} marked as not found, skipping save`);
      return;
    }

    // Check if user is authenticated before saving
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (!token) {
      console.log('User not authenticated, skipping auto-save');
      return;
    }

    // Additional check: verify token is not expired
    try {
      if (token && typeof window !== 'undefined') {
        const tokenData = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Math.floor(Date.now() / 1000);
        if (tokenData.exp && tokenData.exp < currentTime) {
          console.log('Token expired, skipping auto-save');
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          return;
        }
      }
    } catch (error) {
      console.log('Invalid token format, skipping auto-save');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      return;
    }

    try {
      // Save project data using centralized storage service
      if (data.projectData || data.data) {
        await this.post(`/api/storage/projects/${projectId}/update-data`, {
          new_data: data.projectData || data.data,
          merge_strategy: "merge"
        });
      }

      // Data saved to backend storage
      
      // Note: Metadata update removed to prevent duplicate saves
      // The auto-save endpoint handles the main data, metadata updates
      // should be handled separately when actually needed

      this.saveQueue.delete(projectId);
      this.retryAttempts.delete(projectId);
      this.saveTimeouts.delete(projectId);
    } catch (error: any) {
      console.error(`Auto-save failed for project ${projectId}:`, error);
      this.saveTimeouts.delete(projectId);
      
      // If project not found (404), stop trying to save to this project
      if (error?.status === 404 || error?.response?.status === 404) {
        console.warn(`Project ${projectId} not found (404), stopping auto-save attempts`);
        this.notFoundProjects.add(projectId);
        this.pendingSaves.delete(projectId);
        this.retryAttempts.delete(projectId);
        this.saveQueue.delete(projectId);
        return;
      }
      
      this.handleSaveError(projectId, data);
    }
  }

  private async updateProjectMetadata(projectId: string, metadata: any) {
    try {
      await this.post(`/api/storage/projects/${projectId}/metadata`, metadata);
    } catch (error) {
      console.error(`Failed to update project metadata for ${projectId}:`, error);
    }
  }

  // saveToLocalStorage method removed - backend storage only

  private handleSaveError(projectId: string, data: any) {
    const retryCount = this.retryAttempts.get(projectId) || 0;
    if (retryCount < this.maxRetries) {
      console.log(`Retrying save for project ${projectId} (attempt ${retryCount + 1})`);
      this.retryAttempts.set(projectId, retryCount + 1);
      
      // Retry after exponential backoff
      const retryDelay = Math.pow(2, retryCount) * 1000;
      setTimeout(() => {
        this.saveToBackend(projectId, data);
      }, retryDelay);
    } else {
      console.error(`Max retries reached for project ${projectId}, save failed`);
    }
  }

  public async flushAllSaves() {
    const promises = Array.from(this.saveQueue.entries()).map(([projectId, data]) =>
      this.saveToBackend(projectId, data)
    );

    try {
      await Promise.allSettled(promises);
    } catch (error) {
      console.error('Error flushing saves:', error);
    }
  }

  public async pushDataOnRefresh(projectId: string, data: any) {
    console.log(`Pushing data on refresh for project ${projectId}...`);
    
    try {
      // Force immediate save without debouncing
      await this.saveToBackend(projectId, data);
      console.log(`Successfully pushed data on refresh for project ${projectId}`);
    } catch (error) {
      console.error(`Failed to push data on refresh for project ${projectId}:`, error);
      // No fallback - backend storage required
    }
  }


  public getQueueStatus() {
    return {
      queueSize: this.saveQueue.size,
      isOnline: this.isOnline,
      pendingSaves: Array.from(this.pendingSaves),
      notFoundProjects: Array.from(this.notFoundProjects)
    };
  }

  public clearNotFoundProject(projectId: string) {
    this.notFoundProjects.delete(projectId);
  }

  private async processSaveQueue() {
    try {
      const promises = Array.from(this.saveQueue.entries()).map(([projectId, data]) =>
        this.saveToBackend(projectId, data)
      );
      await Promise.allSettled(promises);
    } catch (error) {
      console.error('Error processing save queue:', error);
    }
  }

  // Legacy methods for backward compatibility
  async updateProjectStatus(projectId: string, status: string): Promise<void> {
    await this.put(`/api/storage/projects/${projectId}`, { status });
  }

  async createMusicClipProject(name: string, description: string): Promise<BaseProject> {
    return this.createProject({
      name,
      description,
      type: 'music-clip'
    });
  }


  async uploadTrack(projectId: string, file: File, metadata: any): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));
    
    return this.post(`/api/storage/projects/${projectId}/files/upload`, formData);
  }

  async getProjectScript(projectId: string): Promise<any> {
    const response = await this.get<{ script: any }>(`/api/storage/projects/${projectId}/script`);
    return response.script;
  }
}

export const projectsService = ProjectsService.getInstance();
export const projectsAPI = projectsService;

// Export types for backward compatibility
export type Project = BaseProject;
export type { CreateProjectRequest, UpdateProjectRequest, ProjectData };
