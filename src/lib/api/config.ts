// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export const API_PATHS = {
  // Authentication - using auth router
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    PROFILE: '/api/auth/profile',
    GOOGLE_LOGIN: '/api/auth/google',
    GOOGLE_CALLBACK: '/api/auth/google/callback',
    GITHUB_LOGIN: '/api/auth/github',
    GITHUB_CALLBACK: '/api/auth/github/callback',
  },
  
  // Music Clip - using storage router
  MUSIC_CLIP: {
    PROJECTS: '/api/storage/projects',
    PROJECT: (id: string) => `/api/storage/projects/${id}`,
    TRACKS: (projectId: string) => `/api/storage/projects/${projectId}/tracks`,
    TRACK: (projectId: string, trackId: string) => `/api/storage/projects/${projectId}/files/${trackId}`,
    SCRIPT: (projectId: string) => `/api/storage/projects/${projectId}/script`,
    SETTINGS: (projectId: string) => `/api/storage/projects/${projectId}/settings`,
    UPLOAD_TRACK: (projectId: string) => `/api/storage/projects/${projectId}/tracks/upload`,
    GENERATE: '/api/music-clip/generate-videos',
    STATUS: (jobId: string) => `/api/music-clip/status/${jobId}`,
    PROJECT_STATUS: (projectId: string) => `/api/music-clip/project/${projectId}/status`,
  },
  
  // Storage - using storage router
  STORAGE: {
    PROJECTS: '/api/storage/projects',
    PROJECT: (id: string) => `/api/storage/projects/${id}`,
    UPLOAD_TRACK: (projectId: string) => `/api/storage/projects/${projectId}/tracks/upload`,
    DELETE_TRACK: (projectId: string, trackId: string) => `/api/storage/projects/${projectId}/files/${trackId}`,
    TRACK_URL: (projectId: string, trackId: string) => `/api/storage/projects/${projectId}/files/${trackId}/url`,
  },
  
  // Analysis - using music-analysis router
  ANALYSIS: {
    COMPREHENSIVE: '/api/music-analysis/upload/music/comprehensive',
    SIMPLE: '/api/music-analysis/upload/music/simple',
    MUSIC: (trackId: string) => `/api/music-analysis/music/${trackId}`,
    FILE_PATH: '/api/music-analysis/file-path/music',
  },
  
  // Credits - using business router
  CREDITS: {
    BALANCE: '/api/credits/balance',
    TRANSACTIONS: '/api/credits/transactions',
    SPEND: '/api/credits/spend',
    PURCHASE: '/api/credits/purchase',
    CAN_AFFORD: (amount: number) => `/api/credits/can-afford/${amount}`,
    PRICING: {
      MUSIC: '/api/credits/pricing/music',
      IMAGE: '/api/credits/pricing/image',
      VIDEO: '/api/credits/pricing/video',
      LOOPED_ANIMATION: '/api/credits/pricing/looped-animation',
      RECURRING_SCENES: '/api/credits/pricing/recurring-scenes',
      CALCULATE_BUDGET: '/api/credits/pricing/calculate-budget',
    },
  },
  
  // Payments - using business router
  PAYMENTS: {
    CHECKOUT: '/api/credits/checkout',
    WEBHOOK: '/api/credits/webhook',
    SUBSCRIPTIONS: '/api/credits/subscriptions',
  },
  
  // AI Services - using AI routers
  AI: {
    PROMPTS: {
      RANDOM: '/api/ai/prompts/random',
      CATEGORIES: '/api/ai/prompts/categories',
    },
    COMFYUI: {
      STATUS: '/api/comfyui/status',
      WORKFLOWS: '/api/comfyui/workflows',
      EXECUTE: '/api/comfyui/execute',
      REQUEST: (requestId: string) => `/api/comfyui/request/${requestId}`,
    },
    PRODUCER: {
      GENERATE: '/api/producer/generate',
      FILES: '/api/producer/files',
      TEST: '/api/producer/test',
    },
  },
  
  // Social Media - using social router
  SOCIAL: {
    CONNECT: (platform: string) => `/api/social/connect/${platform}`,
    ACCOUNTS: '/api/social/accounts',
    DISCONNECT: (accountId: string) => `/api/social/accounts/${accountId}`,
    PUBLISH: (exportId: string) => `/api/social/publish/${exportId}`,
    ANALYTICS: (statsId: string) => `/api/social/analytics/${statsId}`,
    PLATFORMS: '/api/social/platforms',
  },
  
  // Mailing - using business router
  MAILING: {
    SUBSCRIBE: '/api/mailing/subscribe',
    UNSUBSCRIBE: '/api/mailing/unsubscribe',
    STATUS: (email: string) => `/api/mailing/status/${email}`,
  },
  
  // Health
  HEALTH: '/api/health',
} as const;

// Re-export from main config
export { BACKEND_CONFIG } from '../config';

export const API_CONFIG = {
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;
