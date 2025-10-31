"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { ClipizyLoading } from "@/components/ui/clipizy-loading";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Shield, ArrowLeft } from "lucide-react";
import Link from "next/link";

interface AdminRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export function AdminRoute({
  children,
  redirectTo = "/dashboard"
}: AdminRouteProps) {
  // Temporarily bypass all authentication for database access
  return <>{children}</>;
  
  // Original authentication logic (commented out for now)
  // const { user, loading, isAuthenticated } = useAuth();
  // const router = useRouter();

  // useEffect(() => {
  //   if (!loading) {
  //     if (!isAuthenticated) {
  //       // Redirect to login if not authenticated
  //       router.push("/auth/login");
  //     }
  //     // Temporarily disabled admin check for database access
  //     // } else if (user && !user.is_admin) {
  //     //   // Redirect to dashboard if not admin
  //     //   router.push(redirectTo);
  //     // }
  //   }
  // }, [user, loading, isAuthenticated, router, redirectTo]);

  // // Show loading while checking authentication
  // if (loading) {
  //   return (
  //     <div className="min-h-screen flex items-center justify-center">
  //       <ClipizyLoading message="Loading..." size="lg" />
  //     </div>
  //   );
  // }

  // Temporarily disabled admin check for database access
  // Show access denied if not admin
  // if (isAuthenticated && user && !user.is_admin) {
  //   return (
  //     <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-muted/20 to-background p-4">
  //       <Card className="w-full max-w-md">
  //         <CardHeader className="text-center">
  //           <div className="mx-auto mb-4 w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center">
  //             <Shield className="w-8 h-8 text-destructive" />
  //           </div>
  //           <CardTitle className="text-2xl font-bold">Access Denied</CardTitle>
  //           <CardDescription>
  //             You don't have permission to access this area. Admin privileges are required.
  //           </CardDescription>
  //         </CardHeader>
  //         <CardContent className="space-y-4">
  //           <div className="text-center text-sm text-muted-foreground">
  //             <p>This area is restricted to administrators only.</p>
  //             <p>Contact your system administrator if you believe this is an error.</p>
  //           </div>
  //           <div className="flex flex-col gap-2">
  //             <Button asChild>
  //               <Link href="/dashboard">
  //                 <ArrowLeft className="w-4 h-4 mr-2" />
  //                 Go to Dashboard
  //               </Link>
  //             </Button>
  //             <Button variant="outline" asChild>
  //               <Link href="/auth/login">
  //                 Switch Account
  //               </Link>
  //             </Button>
  //           </div>
  //         </CardContent>
  //       </Card>
  //     </div>
  //   );
  // }

  // Temporarily allow all authenticated users to access admin
  if (isAuthenticated && user) {
    return <>{children}</>;
  }

  // Show children if user is admin (original logic)
  // if (isAuthenticated && user && user.is_admin) {
  //   return <>{children}</>;
  // }

  // Default case (should not reach here due to useEffect redirects)
  return null;
}
