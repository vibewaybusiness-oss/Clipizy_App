"use client";

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useLoading } from '@/contexts/loading-context';

export function useNavigationLoading() {
  const pathname = usePathname();
  const { startLoading, stopLoading } = useLoading();

  useEffect(() => {
    // Start loading when navigating to a new page
    startLoading("Loading page...");
    
    // Stop loading after a short delay to allow the page to render
    const timer = setTimeout(() => {
      stopLoading();
    }, 500);

    return () => {
      clearTimeout(timer);
    };
  }, [pathname, startLoading, stopLoading]);
}
