/**
 * Centralized Storage API Client
 * Single source of truth for all project data management operations
 */

import { BaseApiClient } from './base';

export interface FileUploadResult {
  success: boolean;
  key: string;
  url: string;
  filename: string;
  original_filename: string;
  file_type: string;
  content_type: string;
  size: number;
  subfolder: string;
  extracted_metadata: Record<string, any>;
  upload_timestamp: string;
}

export interface BackendInfoResult {
  success: boolean;
  id: string;
  file_type: string;
  url: string;
  parameters: Record<string, any>;
}

export interface ProjectDataUpdateResult {
  success: boolean;
  project_id: string;
  merge_strategy: string;
  results: {
    database_updated: boolean;
    data: any;
    timestamp: string;
  };
  timestamp: string;
}

export type FileType = 'image' | 'video' | 'track' | 'voiceover';
export type MergeStrategy = 'merge' | 'replace' | 'append';

export class CentralizedStorageService extends BaseApiClient {
  /**
   * Upload file with type-based subfolder organization
   * Metadata is automatically extracted on the backend
   */
  async uploadFileByType(
    projectId: string,
    fileType: FileType,
    file: File
  ): Promise<FileUploadResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.post(
      `/api/storage/projects/${projectId}/upload/${fileType}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  }

  /**
   * Save backend information to SQL database
   */
  async saveBackendInformation(
    projectId: string,
    fileUrl: string,
    fileType: FileType,
    parameters: Record<string, any>
  ): Promise<BackendInfoResult> {
    const response = await this.post(
      `/api/storage/projects/${projectId}/save-backend-info`,
      {
        file_url: fileUrl,
        file_type: fileType,
        parameters,
      }
    );

    return response.data;
  }

  /**
   * Main function to update project data with merge logic
   */
  async updateProjectData(
    projectId: string,
    newData: Record<string, any>,
    mergeStrategy: MergeStrategy = 'merge'
  ): Promise<ProjectDataUpdateResult> {
    const response = await this.post(
      `/api/storage/projects/${projectId}/update-data`,
      {
        new_data: newData,
        merge_strategy: mergeStrategy,
      }
    );

    return response.data;
  }

  /**
   * Complete workflow: Upload file and save all related information
   * Metadata is automatically extracted during upload
   */
  async uploadAndSaveComplete(
    projectId: string,
    fileType: FileType,
    file: File,
    parameters: Record<string, any>
  ): Promise<{
    upload: FileUploadResult;
    backend: BackendInfoResult;
    projectData: ProjectDataUpdateResult;
  }> {
    // Step 1: Upload file to S3 (metadata extracted automatically)
    const uploadResult = await this.uploadFileByType(projectId, fileType, file);

    // Step 2: Save backend information to database (with extracted metadata)
    const backendResult = await this.saveBackendInformation(
      projectId,
      uploadResult.url,
      fileType,
      {
        ...parameters,
        extracted_metadata: uploadResult.extracted_metadata
      }
    );

    // Step 3: Update project data with new information
    const projectDataResult = await this.updateProjectData(projectId, {
      [fileType]: {
        id: backendResult.id,
        url: uploadResult.url,
        filename: uploadResult.filename,
        original_filename: uploadResult.original_filename,
        size: uploadResult.size,
        content_type: uploadResult.content_type,
        extracted_metadata: uploadResult.extracted_metadata,
        parameters,
        timestamp: uploadResult.upload_timestamp,
      },
    });

    return {
      upload: uploadResult,
      backend: backendResult,
      projectData: projectDataResult,
    };
  }

  /**
   * Save project data for auto-save functionality
   */
  async saveProjectData(
    projectId: string,
    projectData: Record<string, any>,
    mergeStrategy: MergeStrategy = 'merge'
  ): Promise<ProjectDataUpdateResult> {
    return this.updateProjectData(projectId, projectData, mergeStrategy);
  }

  /**
   * Get supported file types
   */
  getSupportedFileTypes(): FileType[] {
    return ['image', 'video', 'track', 'voiceover'];
  }

  /**
   * Get file type configuration
   */
  getFileTypeConfig(fileType: FileType): {
    subfolder: string;
    allowedTypes: string[];
    maxSize: number;
  } {
    const configs = {
      image: {
        subfolder: 'images',
        allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff'],
        maxSize: 20 * 1024 * 1024, // 20MB
      },
      video: {
        subfolder: 'videos',
        allowedTypes: ['video/mp4', 'video/avi', 'video/mov', 'video/webm', 'video/mkv', 'video/flv'],
        maxSize: 500 * 1024 * 1024, // 500MB
      },
      track: {
        subfolder: 'tracks',
        allowedTypes: ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac', 'audio/aac'],
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      voiceover: {
        subfolder: 'voiceovers',
        allowedTypes: ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac', 'audio/aac'],
        maxSize: 20 * 1024 * 1024, // 20MB
      },
    };

    return configs[fileType];
  }

  /**
   * Validate file before upload
   */
  validateFile(file: File, fileType: FileType): { valid: boolean; error?: string } {
    const config = this.getFileTypeConfig(fileType);

    // Check file type
    if (!config.allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `Invalid file type: ${file.type}. Allowed types: ${config.allowedTypes.join(', ')}`,
      };
    }

    // Check file size
    if (file.size > config.maxSize) {
      return {
        valid: false,
        error: `File too large: ${file.size} bytes. Max size: ${config.maxSize} bytes`,
      };
    }

    return { valid: true };
  }
}

// Create singleton instance
export const centralizedStorageService = new CentralizedStorageService();
