"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { ClipizyLoading } from "@/components/ui/clipizy-loading";

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export function ProtectedRoute({
  children,
  redirectTo = "/auth/login"
}: ProtectedRouteProps) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);

  useEffect(() => {
    // Only redirect after we've completed the initial auth check
    if (!loading && hasCheckedAuth && !isAuthenticated) {
      // Store the intended destination
      const currentPath = window.location.pathname;
      if (currentPath !== redirectTo) {
        sessionStorage.setItem("redirect_after_login", currentPath);
      }
      router.push(redirectTo);
    }
  }, [isAuthenticated, loading, hasCheckedAuth, router, redirectTo]);

  useEffect(() => {
    // Mark that we've completed the initial auth check
    if (!loading) {
      setHasCheckedAuth(true);
    }
  }, [loading]);

  // Show loading while checking authentication or before first auth check
  if (loading || !hasCheckedAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-muted/20 to-background">
        <ClipizyLoading message="Loading..." size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}

