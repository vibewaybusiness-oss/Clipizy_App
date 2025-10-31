import { projectsService } from './api/projects';

export const autoSaveService = {
  scheduleSave: (projectId: string, data: any) => {
    // Use unified projects service for all project types
    projectsService.scheduleSave(projectId, data);
  },
  
  flushAllSaves: () => {
    projectsService.flushAllSaves();
  },
  
  getQueueStatus: () => {
    return projectsService.getQueueStatus();
  },

  pushDataOnRefresh: async (projectId: string, data: any) => {
    return projectsService.pushDataOnRefresh(projectId, data);
  },

  loadProjectData: async (projectId: string) => {
    return await projectsService.loadProjectData(projectId);
  }
};
