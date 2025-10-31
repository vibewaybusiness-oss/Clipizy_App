"use client";

import { useEffect } from "react";
import { authService } from "@/lib/api/auth";

interface OnboardingLoadingProps {
  message?: string;
  isVisible: boolean;
  onComplete?: () => void;
}

export function OnboardingLoading({ 
  isVisible,
  onComplete
}: OnboardingLoadingProps) {
  useEffect(() => {
    if (!isVisible) return;

    const setupOnboarding = async () => {
      try {
        const result = await authService.setupOnboarding();
        console.log('✅ Onboarding setup completed:', result);
        onComplete?.();
      } catch (err: any) {
        console.error('❌ Onboarding setup failed:', err);
        onComplete?.();
      }
    };

    setupOnboarding();
  }, [isVisible, onComplete]);

  return null;
}
