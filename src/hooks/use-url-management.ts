"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";

interface UseUrlManagementOptions {
  basePath?: string;
  projectType?: string;
  projectId?: string | null;
  currentStep?: number;
  maxReachedStep?: number;
  onStepChange?: (step: number) => void;
  onProjectIdChange?: (projectId: string | null) => void;
  enableStorageSync?: boolean;
}

interface UseUrlManagementReturn {
  urlProjectId: string | null;
  isNewProject: boolean;
  updateStepInUrl: (step: number) => void;
  updateProjectIdInUrl: (projectId: string | null) => void;
  preventRedirects: boolean;
  syncWithStorage: () => void;
  isStorageSynced: boolean;
}

export function useUrlManagement(options: UseUrlManagementOptions = {}): UseUrlManagementReturn {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  
  const [preventRedirects, setPreventRedirects] = useState(false);
  const [isStorageSynced, setIsStorageSynced] = useState(false);
  
  const urlProjectId = searchParams.get('projectId');
  const isNewProject = !urlProjectId;
  
  const updateStepInUrl = useCallback((step: number) => {
    if (preventRedirects) return;
    
    const params = new URLSearchParams(searchParams);
    params.set('step', step.toString());
    
    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
  }, [searchParams, pathname, router, preventRedirects]);
  
  const updateProjectIdInUrl = useCallback((projectId: string | null) => {
    if (preventRedirects) return;
    
    const params = new URLSearchParams(searchParams);
    
    if (projectId) {
      params.set('projectId', projectId);
    } else {
      params.delete('projectId');
    }
    
    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
  }, [searchParams, pathname, router, preventRedirects]);
  
  const syncWithStorage = useCallback(() => {
    setIsStorageSynced(true);
    // Additional sync logic can be added here
  }, []);
  
  // Reset sync state when URL changes
  useEffect(() => {
    setIsStorageSynced(false);
  }, [urlProjectId]);
  
  return {
    urlProjectId,
    isNewProject,
    updateStepInUrl,
    updateProjectIdInUrl,
    preventRedirects,
    syncWithStorage,
    isStorageSynced
  };
}
