"use client";

import { useCallback } from 'react';
import { 
  ProjectType, 
  ProjectTypeHandler, 
  ProjectManager,
  PROJECT_CONFIGS,
  BaseProject,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectData
} from '@/types/projects';
import { projectsAPI } from '@/lib/api/projects';

interface UseProjectFactoryOptions {
  projectType: ProjectType;
}

interface UseProjectFactoryReturn {
  getHandler: () => ProjectTypeHandler;
  createProject: (data: CreateProjectRequest) => Promise<BaseProject>;
  updateProject: (id: string, data: UpdateProjectRequest) => Promise<BaseProject>;
  deleteProject: (id: string) => Promise<void>;
  getProject: (id: string) => Promise<BaseProject>;
  getProjects: (userId: string) => Promise<BaseProject[]>;
  saveProjectData: (id: string, data: ProjectData) => Promise<void>;
  loadProjectData: (id: string) => Promise<ProjectData>;
  uploadFile: (projectId: string, file: File, metadata?: any) => Promise<string>;
  deleteFile: (projectId: string, fileId: string) => Promise<void>;
  getProjectFiles: (projectId: string) => Promise<any[]>;
}

export function useProjectFactory({ projectType }: UseProjectFactoryOptions): UseProjectFactoryReturn {
  
  const getHandler = useCallback((): ProjectTypeHandler => {
    const config = PROJECT_CONFIGS[projectType];
    
    return {
      projectType,
      createProject: async (data: CreateProjectRequest) => {
        return await projectsAPI.createProject(data);
      },
      updateProject: async (id: string, data: UpdateProjectRequest) => {
        return await projectsAPI.updateProject(id, data);
      },
      deleteProject: async (id: string) => {
        await projectsAPI.deleteProject(id);
      },
      getProject: async (id: string) => {
        return await projectsAPI.getProject(id);
      },
      getProjects: async (userId: string) => {
        return await projectsAPI.getProjects(userId, projectType);
      },
      saveProjectData: async (id: string, data: ProjectData) => {
        await projectsAPI.saveProjectData(id, data);
      },
      loadProjectData: async (id: string) => {
        return await projectsAPI.loadProjectData(id);
      },
      uploadFile: async (projectId: string, file: File, metadata?: any) => {
        // Validate file type
        if (!config.allowedFileTypes.includes('*/*') && !config.allowedFileTypes.includes(file.type)) {
          throw new Error(`File type ${file.type} not allowed for ${projectType} projects`);
        }
        
        // Validate file size
        if (file.size > config.maxFileSize) {
          throw new Error(`File size ${file.size} exceeds maximum allowed size ${config.maxFileSize} for ${projectType} projects`);
        }
        
        return await projectsAPI.uploadProjectFile(projectId, file, metadata);
      },
      deleteFile: async (projectId: string, fileId: string) => {
        await projectsAPI.deleteFile(projectId, fileId);
      },
      getProjectFiles: async (projectId: string) => {
        return await projectsAPI.getProjectFiles(projectId);
      }
    };
  }, [projectType]);

  const createProject = useCallback(async (data: CreateProjectRequest): Promise<BaseProject> => {
    const handler = getHandler();
    return await handler.createProject(data);
  }, [getHandler]);

  const updateProject = useCallback(async (id: string, data: UpdateProjectRequest): Promise<BaseProject> => {
    const handler = getHandler();
    return await handler.updateProject(id, data);
  }, [getHandler]);

  const deleteProject = useCallback(async (id: string): Promise<void> => {
    const handler = getHandler();
    await handler.deleteProject(id);
  }, [getHandler]);

  const getProject = useCallback(async (id: string): Promise<BaseProject> => {
    const handler = getHandler();
    return await handler.getProject(id);
  }, [getHandler]);

  const getProjects = useCallback(async (userId: string): Promise<BaseProject[]> => {
    const handler = getHandler();
    return await handler.getProjects(userId);
  }, [getHandler]);

  const saveProjectData = useCallback(async (id: string, data: ProjectData): Promise<void> => {
    const handler = getHandler();
    await handler.saveProjectData(id, data);
  }, [getHandler]);

  const loadProjectData = useCallback(async (id: string): Promise<ProjectData> => {
    const handler = getHandler();
    return await handler.loadProjectData(id);
  }, [getHandler]);

  const uploadFile = useCallback(async (projectId: string, file: File, metadata?: any): Promise<string> => {
    const handler = getHandler();
    return await handler.uploadFile(projectId, file, metadata);
  }, [getHandler]);

  const deleteFile = useCallback(async (projectId: string, fileId: string): Promise<void> => {
    const handler = getHandler();
    await handler.deleteFile(projectId, fileId);
  }, [getHandler]);

  const getProjectFiles = useCallback(async (projectId: string): Promise<any[]> => {
    const handler = getHandler();
    return await handler.getProjectFiles(projectId);
  }, [getHandler]);

  return {
    getHandler,
    createProject,
    updateProject,
    deleteProject,
    getProject,
    getProjects,
    saveProjectData,
    loadProjectData,
    uploadFile,
    deleteFile,
    getProjectFiles
  };
}

// Convenience hooks for specific project types
export function useMusicClipProject() {
  return useProjectFactory({ projectType: 'music-clip' });
}

export function useVideoEditProject() {
  return useProjectFactory({ projectType: 'video-edit' });
}

export function useAudioEditProject() {
  return useProjectFactory({ projectType: 'audio-edit' });
}

export function useImageEditProject() {
  return useProjectFactory({ projectType: 'image-edit' });
}

export function useCustomProject() {
  return useProjectFactory({ projectType: 'custom' });
}
