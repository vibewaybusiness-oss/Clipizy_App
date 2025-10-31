"use client";

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { projectsService as projectsAPI } from '@/lib/api/projects';
import { authService } from '@/lib/api/auth';

interface UserOnboardingState {
  isNewUser: boolean;
  isLoading: boolean;
  hasChecked: boolean;
}

interface UserOnboardingActions {
  checkUserStatus: () => Promise<void>;
  markAsReturningUser: () => void;
}

export function useUserOnboarding() {
  const { user } = useAuth();
  const [isNewUser, setIsNewUser] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [hasChecked, setHasChecked] = useState<boolean>(false);

  const checkUserStatus = useCallback(async () => {
    if (!user?.id || hasChecked) {
      return;
    }

    setIsLoading(true);
    setHasChecked(true);

    try {
      console.log('🔍 Checking if user is new:', user.id);
      
      // Check if user has any existing projects
      const response = await projectsAPI.getAllProjects();
      const projects = response.projects;
      const hasExistingProjects = projects && projects.length > 0;
      
      console.log('📊 User project status:', {
        userId: user.id,
        hasExistingProjects,
        projectCount: projects?.length || 0
      });

      // User is considered "new" if they have no existing projects
      setIsNewUser(!hasExistingProjects);
      
      if (!hasExistingProjects) {
        console.log('🆕 User is new - no existing projects found');
        console.log('ℹ️ Note: User storage structure and credits are automatically created during login');
      } else {
        console.log('👤 User is returning - has existing projects');
      }
    } catch (error: any) {
      console.error('Failed to check user status:', error);
      
      // On error, assume user is new to be safe
      setIsNewUser(true);
      
      // Handle authentication errors
      if (error?.status === 401 || error?.status === 403) {
        console.log('Authentication error during user status check');
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/auth/login';
        }
        return;
      }
    } finally {
      setIsLoading(false);
    }
  }, [user?.id, hasChecked]);

  const markAsReturningUser = useCallback(() => {
    console.log('✅ Marking user as returning user');
    setIsNewUser(false);
  }, []);

  // Auto-check user status when user changes
  useEffect(() => {
    if (user?.id && !hasChecked) {
      checkUserStatus();
    }
  }, [user?.id, checkUserStatus, hasChecked]);

  const state: UserOnboardingState = {
    isNewUser,
    isLoading,
    hasChecked
  };

  const actions: UserOnboardingActions = {
    checkUserStatus,
    markAsReturningUser
  };

  return {
    state,
    actions
  };
}
